
from __future__ import annotations

import io
import warnings
import xml.etree.ElementTree as ET
from typing import Iterator

import requests
from astropy.io import fits


class S3Client:
    """Cliente de solo lectura para el archivo público SPHEREx en AWS S3."""

    BASE_URL = "https://nasa-irsa-spherex.s3.us-east-1.amazonaws.com/"
    XML_NAMESPACE = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

    def __init__(self, timeout: int = 60, header_bytes: int = 1_048_576):
        self.timeout = timeout
        self.header_bytes = header_bytes
        self.session = requests.Session()

    def list_objects(
        self,
        prefix: str,
        max_files: int | None = None,
    ) -> Iterator[dict]:
        """Recorre objetos S3 usando paginación automática."""

        continuation_token = None
        encontrados = 0

        while True:
            params = {
                "list-type": "2",
                "prefix": prefix,
                "max-keys": 1000,
            }

            if continuation_token:
                params["continuation-token"] = continuation_token

            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)

            for item in root.findall(".//s3:Contents", self.XML_NAMESPACE):
                key = item.findtext("s3:Key", namespaces=self.XML_NAMESPACE)
                size = item.findtext("s3:Size", namespaces=self.XML_NAMESPACE)
                modified = item.findtext(
                    "s3:LastModified",
                    namespaces=self.XML_NAMESPACE,
                )

                if not key:
                    continue

                yield {
                    "key": key,
                    "size": int(size or 0),
                    "last_modified": modified,
                }

                encontrados += 1

                if max_files is not None and encontrados >= max_files:
                    return

            truncated = (
                root.findtext("s3:IsTruncated", namespaces=self.XML_NAMESPACE)
                == "true"
            )

            if not truncated:
                break

            continuation_token = root.findtext(
                "s3:NextContinuationToken",
                namespaces=self.XML_NAMESPACE,
            )

            if not continuation_token:
                raise RuntimeError(
                    "S3 indicó que hay más resultados, "
                    "pero no devolvió un token de continuación."
                )

    def list_fits(
        self,
        prefix: str,
        max_files: int | None = None,
    ) -> Iterator[dict]:
        """Devuelve solamente archivos FITS."""

        for item in self.list_objects(prefix, max_files=None):
            if item["key"].lower().endswith((".fits", ".fits.gz")):
                yield item

                # El límite se aplica a FITS, no a todos los objetos.
                if max_files is not None:
                    max_files -= 1
                    if max_files <= 0:
                        return

    def get_image_header(self, key: str) -> fits.Header:
        """
        Lee la primera cabecera de imagen de un FITS mediante HTTP Range.
        No descarga deliberadamente el contenido completo del archivo.
        """

        url = self.BASE_URL + key.lstrip("/")
        end_byte = self.header_bytes - 1

        response = self.session.get(
            url,
            headers={"Range": f"bytes=0-{end_byte}"},
            timeout=self.timeout,
        )

        if response.status_code != 206:
            raise RuntimeError(
                f"S3 no devolvió una respuesta parcial para {key}. "
                f"HTTP {response.status_code}. "
                "Se cancela la lectura para evitar descargar el FITS completo."
            )

        with warnings.catch_warnings():
            # El archivo está intencionalmente incompleto: solo leemos cabeceras.
            warnings.simplefilter("ignore")

            with fits.open(
                io.BytesIO(response.content),
                lazy_load_hdus=True,
                ignore_missing_end=True,
            ) as hdul:
                for hdu in hdul:
                    if hdu.header.get("NAXIS", 0) >= 2:
                        return hdu.header.copy()

        raise RuntimeError(
            f"No se encontró una extensión de imagen en {key}."
        )

    def close(self) -> None:
        self.session.close()


def main():
    cliente = S3Client()

    prefijo = (
        "dr1/level2/2025W33_1B/"
        "l2b-v27-2026-227/1/"
    )

    try:
        print("BUSCANDO ARCHIVOS FITS EN SPHEREx")
        print("=" * 60)

        archivos = list(cliente.list_fits(prefijo, max_files=5))

        print(f"Archivos FITS encontrados en la muestra: {len(archivos)}")

        for archivo in archivos:
            print(
                f'{archivo["key"]} '
                f'({archivo["size"] / 1024 / 1024:.2f} MB)'
            )

        if not archivos:
            print("No se encontraron archivos FITS.")
            return

        print("\nLEYENDO CABECERA DEL PRIMER FITS")
        print("=" * 60)

        header = cliente.get_image_header(archivos[0]["key"])

        for campo in (
            "DATE-OBS",
            "MJD-OBS",
            "BUNIT",
            "NAXIS1",
            "NAXIS2",
            "CRVAL1",
            "CRVAL2",
            "CTYPE1",
            "CTYPE2",
        ):
            if campo in header:
                print(f"{campo}: {header[campo]}")

        print("\nLectura parcial de cabecera completada.")

    finally:
        cliente.close()


if __name__ == "__main__":
    main()
