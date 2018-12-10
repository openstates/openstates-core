import csv

seen = set()

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


with open('version-export.csv') as f, open('output.csv', 'w') as outf:
    out = csv.writer(outf)
    for line in csv.reader(f):
        bill_id, session, identifier, title, org_name, org_classification, jurisdiction, date, note, media_type, url = line

        key = (jurisdiction, session, org_classification, media_type)

        if key not in seen:
            out.writerow(line)
            seen.add(key)
