import attr
import typing


@attr.s
class District:
    name: str = attr.ib()
    chamber_type: str = attr.ib()
    division_id: typing.Optional[str] = attr.ib()
    num_seats: int = attr.ib(default=1)
    title_override: typing.Optional[str] = attr.ib(default=None)


@attr.s(auto_attribs=True)
class Chamber:
    chamber_type: str
    name: str
    title: str
    num_seats: int
    organization_id: str
    districts: typing.List[District]

    def lookup_district(
        self,
        division_id: typing.Optional[str] = None,
        *,
        name: typing.Optional[str] = None,
    ) -> typing.Optional[District]:
        for d in self.districts:
            if division_id and d.division_id == division_id:
                return d
            if name and d.name == name:
                return d
        return None


@attr.s(auto_attribs=True)
class State:
    name: str
    abbr: str
    capital: str
    capital_tz: str
    fips: str
    unicameral: bool
    legislature_name: str
    legislature_organization_id: str
    executive_name: str
    executive_organization_id: str
    division_id: str
    jurisdiction_id: str
    url: str
    lower: typing.Optional[Chamber] = None
    upper: typing.Optional[Chamber] = None
    legislature: typing.Optional[Chamber] = None

    @property
    def chambers(self) -> typing.List[Chamber]:
        if self.unicameral:
            return [typing.cast(Chamber, self.legislature)]
        else:
            return [typing.cast(Chamber, self.lower), typing.cast(Chamber, self.upper)]

    @property
    def legacy_districts(self) -> typing.List[District]:
        from .data.legacy_districts import legacy_districts

        return legacy_districts.get(self.abbr.lower(), [])

    def lookup_district(
        self, division_id: str = None, *, name: str = None, chamber: str = None
    ) -> typing.Optional[District]:
        if self.legislature and self.unicameral:
            return self.legislature.lookup_district(division_id=division_id, name=name)
        elif self.lower and (
            division_id and "sldl" in division_id or chamber == "lower"
        ):
            return self.lower.lookup_district(division_id=division_id, name=name)
        elif self.upper and (
            division_id and "sldu" in division_id or chamber == "upper"
        ):
            return self.upper.lookup_district(division_id=division_id, name=name)
        return None


def simple_numbered_districts(
    parent_id: str, chamber_type: str, total: int, *, num_seats: int = 1
) -> typing.List[District]:
    prefix = "sldl" if chamber_type == "lower" else "sldu"
    return [
        District(str(n), chamber_type, f"{parent_id}/{prefix}:{n}", num_seats)
        for n in range(1, total + 1)
    ]
