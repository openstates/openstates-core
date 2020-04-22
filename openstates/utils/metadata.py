import openstates_metadata


def jid_to_abbr(jid):
    return openstates_metadata.lookup(jurisdiction_id=jid).abbr.lower()


def abbr_to_jid(abbr):
    return openstates_metadata.lookup(abbr=abbr).jurisdiction_id
