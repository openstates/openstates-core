import csv
import os
import urllib.request


def jid_to_abbr(j):
    return j.split(':')[-1].split('/')[0]


def download(version):
    abbr = jid_to_abbr(version['jurisdiction_id'])
    ext = {'application/pdf': 'pdf',
           'text/html': 'html',
           'application/msword': 'doc',
           'application/rtf': 'rtf',
           'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
           }[version["media_type"]]
    filename = f'raw/{abbr}/{version["session"]}-{version["identifier"]}.{ext}'

    if not os.path.exists(filename):
        print(version['url'])
        urllib.request.urlretrieve(version['url'], filename)


def main():
    with open('sample.csv') as f:
        for version in csv.DictReader(f):
            download(version)
            # if jid_to_abbr(version['jurisdiction_id']) == state:


if __name__ == '__main__':
    main()
