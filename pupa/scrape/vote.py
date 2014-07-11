from ..utils import make_psuedo_id
from .base import BaseModel, cleanup_list, SourceMixin
from .bill import Bill
from .popolo import psuedo_organization
from .schemas.vote import schema


class Vote(BaseModel, SourceMixin):
    _type = 'vote'
    _schema = schema

    def __init__(self, *, legislative_session, motion_text, start_date, classification, result,
                 identifier='', bill=None, bill_chamber=None, organization=None, chamber=None):
        super(Vote, self).__init__()

        self.legislative_session = legislative_session
        self.motion_text = motion_text
        self.motion_classification = cleanup_list(classification, [])
        self.start_date = start_date
        self.result = result
        self.identifier = identifier

        self.set_bill(bill, chamber=bill_chamber)
        self.organization = psuedo_organization(organization, chamber, 'legislature')
        self.votes = []
        self.counts = []

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.legislative_session, self.start_date,
                                        self.motion_text)

    def set_bill(self, bill_or_identifier, *, chamber=None):
        if not bill_or_identifier:
            self.bill = None
        elif isinstance(bill_or_identifier, Bill):
            if chamber:
                raise ValueError("set_bill takes no arguments when using a `Bill` object")
            self.bill = bill_or_identifier._id
        else:
            if chamber is None:
                chamber = 'legislature'
            kwargs = {'identifier': bill_or_identifier,
                      'from_organization__classification': chamber}
            self.bill = make_psuedo_id(**kwargs)

    def vote(self, option, voter):
        self.votes.append({"option": option, "voter_name": voter})

    def yes(self, name, *, id=None):
        return self.vote('yes', name)

    def no(self, name, *, id=None):
        return self.vote('no', name)

    def set_count(self, option, value):
        for co in self.counts:
            if co['option'] == option:
                co['value'] = value
                break
        else:
            self.counts.append({'option': option, 'value': value})