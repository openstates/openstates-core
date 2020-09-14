from .. import metadata


def jid_to_abbr(jid):
    return metadata.lookup(jurisdiction_id=jid).abbr.lower()


def abbr_to_jid(abbr):
    return metadata.lookup(abbr=abbr).jurisdiction_id
