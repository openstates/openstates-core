import csv
from collections import Counter

"""
Generate version-export.csv via a query like:

```
SELECT b.id, s.identifier as session, b.identifier, b.title, org.name, org.classification, org.jurisdiction_id, v.date, v.note, link.media_type, link.url
from opencivicdata_bill b
join opencivicdata_organization org on b.from_organization_id=org.id 
join opencivicdata_legislativesession s on b.legislative_session_id=s.id
join opencivicdata_billversion v on v.bill_id=b.id
join opencivicdata_billversionlink link on link.version_id=v.id;
```
"""


seen = Counter()

COUNT_PER_KEY = 25
output = []

with open("version-export.csv") as f, open("sample.csv", "w") as outf:
    versions = csv.DictReader(f)
    for version in versions:
        key = (
            version["jurisdiction_id"],
            version["session"],
            version["classification"],
            version["media_type"],
        )
        if seen[key] < COUNT_PER_KEY:
            output.append(version)
            seen[key] += 1

    out = csv.DictWriter(outf, fieldnames=versions.fieldnames)
    out.writeheader()
    for v in sorted(output, key=lambda x: (x["jurisdiction_id"], x["session"])):
        out.writerow(v)
