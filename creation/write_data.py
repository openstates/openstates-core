import us
import csv
import yaml


def calc_seats(data):
    chamber_seats = {}
    for key in ("upper", "lower", "legislature"):
        seats = data.get(key + "_seats")
        if not seats:
            continue
        elif isinstance(seats, int):
            # one seat per district by default
            chamber_seats[key] = {str(s): 1 for s in range(1, seats + 1)}
        elif isinstance(seats, list):
            chamber_seats[key] = {str(s): 1 for s in seats}
        elif isinstance(seats, dict):
            chamber_seats[key] = seats
        else:  # pragma: no cover
            raise ValueError(seats)
    return chamber_seats


def seats_to_args(seats):
    if isinstance(seats, int):
        return seats, None
    elif isinstance(seats, list):
        return len(seats), {str(s): 1 for s in seats}
    else:
        return sum(seats.values()), seats


def slugify(name):
    return name.lower().replace(" ", "_")


def make_districts(parent_id, chamber_type, num, seats, division_ids):
    if not seats and not division_ids:
        return f"simple_numbered_districts('{parent_id}', '{chamber_type}', {num})"
    elif (
        parent_id.split(":")[-1] in ("az", "id", "nd", "nj", "wa")
        and chamber_type == "lower"
    ):
        return f"simple_numbered_districts('{parent_id}', '{chamber_type}', {num//2}, num_seats=2)"
    elif seats and not division_ids:
        prefix = "sldl" if chamber_type == "lower" else "sldu"
        return (
            "["
            + "\n".join(
                (
                    f'District("{seat}", "{chamber_type}", "{parent_id}/{prefix}:{slugify(seat)}", {num}),'
                    for seat, num in seats.items()
                )
            )
            + "]"
        )
    else:
        # seats and division_ids together
        return (
            "["
            + "\n".join(
                (
                    f'District("{seat}", "{chamber_type}", "{division_ids[seat]}", {num}),'
                    for seat, num in seats.items()
                )
            )
            + "]"
        )


if __name__ == "__main__":
    settings = yaml.load(open(f"../people/settings.yml"))
    jurisdictions = csv.DictReader(open("creation/jurisdictions.csv"))
    jurisdictions_by_name = {j["state"]: j for j in jurisdictions}

    for state in us.STATES + [us.states.lookup("PR")]:

        obj = settings[state.abbr.lower()]
        j = jurisdictions_by_name[state.name]

        leg_name = obj.pop("legislature_name")
        unicameral = state.abbr in ("DC", "NE")
        extra_import = ""

        if not unicameral:
            lower_name = obj.pop("lower_chamber_name", "House")
            lower_title = obj.pop("lower_title", "Representative")
            num_lower_seats, lower_seats = seats_to_args(obj.pop("lower_seats"))
            lower_div_ids = obj.pop("lower_division_ids", None)
            upper_name = obj.pop("upper_chamber_name", "Senate")
            upper_title = obj.pop("upper_title", "Senator")
            num_upper_seats, upper_seats = seats_to_args(obj.pop("upper_seats"))
            upper_div_ids = obj.pop("upper_division_ids", None)

            lower_ds = make_districts(
                j["division_id"], "lower", num_lower_seats, lower_seats, lower_div_ids
            )
            upper_ds = make_districts(
                j["division_id"], "upper", num_upper_seats, upper_seats, upper_div_ids
            )

            if "District" in lower_ds + upper_ds:
                extra_import += ", District"
            if "simple_numbered_districts" in lower_ds + upper_ds:
                extra_import += ", simple_numbered_districts"

            seats_block = f"""
                lower=Chamber(chamber_type="lower", name="{lower_name}",
                   num_seats={num_lower_seats}, title="{lower_title}", districts={lower_ds}),
                upper=Chamber(chamber_type="upper", name="{upper_name}",
                   num_seats={num_upper_seats}, title="{upper_title}", districts={upper_ds},),
        """
        else:
            num_leg_seats, leg_seats = seats_to_args(obj.pop("legislature_seats"))
            leg_title = obj.pop("legislature_title")
            div_ids = obj.pop("legislature_division_ids", None)
            districts = make_districts(
                j["division_id"], "legislature", num_leg_seats, leg_seats, div_ids
            )

            if "District" in districts:
                extra_import += ", District"
            if "simple_numbered_districts" in districts:
                extra_import += ", simple_numbered_districts"

            seats_block = f"""
                legislature=Chamber(chamber_type="unicameral", name="{leg_name}",
                     num_seats={num_leg_seats}, title="{leg_title}", districts={districts}),
                """

        # ensure we got it all
        obj.pop("vacancies", None)
        if obj:
            raise Exception(obj)

        if state.abbr == "OR":
            fname = f"openstates_metadata/data/ore.py"
        elif state.abbr == "IN":
            fname = f"openstates_metadata/data/ind.py"
        else:
            fname = f"openstates_metadata/data/{state.abbr.lower()}.py"
        with open(fname, "w") as f:
            f.write(
                f"""from ..models import State, Chamber{extra_import}

{state.abbr} = State(
    name="{state.name}",
    abbr="{state.abbr}",
    capital="{state.capital}",
    capital_tz="{state.capital_tz}",
    fips="{state.fips}",
    unicameral={unicameral},
    legislature_name="{leg_name}",
    division_id="{j['division_id']}",
    jurisdiction_id="{j['jurisdiction_id']}",
    url="{j['url']}",
    {seats_block}
)"""
            )
