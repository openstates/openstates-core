from .base import BaseModel, Scraper
from .popolo import Organization
from .schemas.jurisdiction import schema
from ..metadata import lookup
import requests


_name_fixes = {
    "SouthCarolina": "South Carolina",
    "NorthCarolina": "North Carolina",
    "SouthDakota": "South Dakota",
    "NorthDakota": "North Dakota",
    "RhodeIsland": "Rhode Island",
    "NewHampshire": "New Hampshire",
    "NewJersey": "New Jersey",
    "NewYork": "New York",
    "NewMexico": "New Mexico",
    "WestVirginia": "West Virginia",
    "PuertoRico": "Puerto Rico",
    "DistrictOfColumbia": "District of Columbia",
    "UnitedStates": "United States",
    "southafrica": "South Africa",
    "VirginIslands": "Virgin Islands",
    "AmericanSamoa": "American Samoa",
    "NorthernMarianaIslands": "Northern Mariana Islands",
}


class State(BaseModel):
    """Base class for a jurisdiction"""

    _type = "jurisdiction"
    _schema = schema

    # schema objects
    legislative_sessions = []
    extras = {}

    # non-db properties
    scrapers = {}
    default_scrapers = None
    ignored_scraped_sessions = []
    _metadata = None

    def __init__(self):
        super(BaseModel, self).__init__()
        self._related = []
        self.extras = {}

    @property
    def classification(self):
        if any(c == self.name for c in ["United States", "South Africa"]):
            return "country"
        else:
            return "state"

    @property
    def metadata(self):
        if not self._metadata:
            name = _name_fixes.get(self.__class__.__name__, self.__class__.__name__)
            self._metadata = lookup(name=name)
        return self._metadata

    @property
    def division_id(self):
        return self.metadata.division_id

    @property
    def jurisdiction_id(self):
        return "{}/government".format(
            self.division_id.replace("ocd-division", "ocd-jurisdiction"),
        )

    @property
    def name(self):
        return self.metadata.name

    @property
    def url(self):
        return self.metadata.url

    @property
    def legislative_sessions(self):
        params = {"state_name": self.name}
        response = requests.get(
            "http://abstractcronos.us-west-2.elasticbeanstalk.com/sessions/query",
            params=params,
        )
        response.raise_for_status()
        return response.json()

    def get_organizations(self):
        legislature = Organization(
            name=self.metadata.legislature_name, classification="legislature"
        )
        yield legislature
        if not self.metadata.unicameral:
            yield Organization(
                self.metadata.upper.name,
                classification="upper",
                parent_id=legislature._id,
            )
            yield Organization(
                self.metadata.lower.name,
                classification="lower",
                parent_id=legislature._id,
            )

    def get_session_list(self) -> list[str]:
        raise NotImplementedError()

    _id = jurisdiction_id

    def as_dict(self):
        return {
            "_id": self.jurisdiction_id,
            "id": self.jurisdiction_id,
            "name": self.name,
            "url": self.url,
            "division_id": self.division_id,
            "classification": self.classification,
            "legislative_sessions": self.legislative_sessions,
            "extras": self.extras,
        }

    def __str__(self):
        return self.name


class JurisdictionScraper(Scraper):
    def scrape(self):
        # yield a single Jurisdiction object
        yield self.jurisdiction

        # yield all organizations
        for org in self.jurisdiction.get_organizations():
            yield org
