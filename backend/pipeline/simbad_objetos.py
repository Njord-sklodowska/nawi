from astroquery.simbad import Simbad

Simbad.add_votable_fields("pmra", "pmdec")
nombres = ["Barnard's star", "eps Ind", "WISE J085510.83-071442.5", "RW Aur", "R Dra"]
for n in nombres:
    print("=" * 40, n)
    try:
        print(Simbad.query_object(n))
    except Exception as e:
        print("ERROR:", e)