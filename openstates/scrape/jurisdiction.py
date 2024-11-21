from .base import BaseModel, Scraper
from .popolo import Organization
from .schemas.jurisdiction import schema
from ..metadata import lookup
import requests
import os
from datetime import datetime


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
    historical_legislative_sessions = []
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
    def new_sessions(
        self,
        endpoint: str = os.getenv("CRONOS_ENDPOINT"),
    ):
        """Requires CRONOS_ENDPOINT for getting the legislative sessions. Note that legislative sessions are retrieved as a list of json objects.

        The legislative sessions appear in the following format
        {
            "identifier": "2021",
            "name": "2021 Regular Session",
            "start_date": "2021-01-01",
            "end_date": "2021-12-31",
            "classification": "primary", # primary or special
            }
        """
        params = {"state_name": self.name}
        response = requests.get(
            endpoint,
            params=params,
        )

        try:
            response.raise_for_status()
        except requests.RequestException:
            print("No sessions found for ", self.name, " in cronos")
            return []

        sessions = []
        for session in response.json():
            # Clean the session by removing any unnecessary fields from cronos (session ID, etc.)
            clean_session = self.check_session_active(
                {
                    key: value
                    for key, value in session.items()
                    if key
                    in [
                        "classification",
                        "identifier",
                        "active",
                        "name",
                        "start_date",
                        "end_date",
                    ]
                }
            )
            sessions.append(clean_session)

        # TODO: Move the above feature to cronos' endpoint, and then we can just have this line: return [{key: value for key, value in session.items() if key in ["classification", "identifier", "name", "start_date", "end_date", "active"]} for session in response.json()]
        return sessions

    @property
    def legislative_sessions(self, opt_for_new: bool = True):
        """Returns a list of legislative sessions. If opt_for_new is True, it will override the historical sessions with the new ones from cronos. Otherwise,
        any sessions from cronos with the same identifier as the historical ones will not be used.
        """
        if not opt_for_new:
            sessions_table = {
                session["identifier"]: session for session in self.new_sessions
            }
            # Now, any historical sessions with the same identifier will be overridden
            sessions_table.update(
                {
                    session["identifier"]: session
                    for session in self.historical_legislative_sessions
                }
            )
        else:  # Override sessions with the same identifier with the new ones from cronos.
            sessions_table = {
                session["identifier"]: session
                for session in self.historical_legislative_sessions
            }
            sessions_table.update(
                {session["identifier"]: session for session in self.new_sessions}
            )

        return list(sessions_table.values())

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

    def check_session_active(session: dict):
        """For a given session dictionary, checks to see if "active" is a denoted field. If it's not, then 'active' is set based on the start_date and end_date"""
        if "active" not in session:
            session["active"] = (
                datetime.strptime(session["start_date"], "%Y-%m-%d").date()
                <= datetime.now().date()
                <= datetime.strptime(session["end_date"], "%Y-%m-%d").date()
            )
        return session

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
