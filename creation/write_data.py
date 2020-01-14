import us
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


if __name__ == "__main__":
    settings = yaml.load(open(f'../people/settings.yml'))

    for state in us.STATES:

        obj = settings[state.abbr.lower()]
        leg_name = obj.pop("legislature_name")
        unicameral = state.abbr in ("DC", "NE")

        if not unicameral:
            lower_name = obj.pop("lower_chamber_name", "House")
            lower_title = obj.pop("lower_title", "Representative")
            num_lower_seats, lower_seats = seats_to_args(obj.pop("lower_seats"))
            lower_div_ids = obj.pop("lower_division_ids", None)
            upper_name = obj.pop("upper_chamber_name", "Senate")
            upper_title = obj.pop("upper_title", "Senator")
            num_upper_seats, upper_seats = seats_to_args(obj.pop("upper_seats"))
            upper_div_ids = obj.pop("upper_division_ids", None)

            seats_block = f"""
                lower=Chamber(chamber_type="lower", name="{lower_name}", num_seats={num_lower_seats}, seats={lower_seats}, division_ids={lower_div_ids}, title="{lower_title}"),
                upper=Chamber(chamber_type="upper", name="{upper_name}", num_seats={num_upper_seats}, seats={upper_seats}, division_ids={upper_div_ids}, title="{upper_title}"),
        """
        else:
            num_leg_seats, leg_seats = seats_to_args(obj.pop("legislature_seats"))
            leg_title = obj.pop("legislature_title")
            div_ids = obj.pop("legislature_division_ids", None)
            seats_block = f"""
                legislature=Chamber(chamber_type="unicameral", name="{leg_name}", num_seats={num_leg_seats}, seats={leg_seats}, division_ids={div_ids}, title="{leg_title}"),
                """

        # ensure we got it all
        obj.pop("vacancies", None)
        if obj:
            raise Exception(obj)

        with open(f"openstates_metadata/data/{state.abbr.lower()}.py", "w") as f:
            f.write(f"""from ..models import State, Chamber

{state.abbr} = State(
    name="{state.name}",
    abbr="{state.abbr}",
    capital="{state.capital}",
    capital_tz="{state.capital_tz}",
    fips="{state.fips}",
    unicameral={unicameral},
    legislature_name="{leg_name}",
    {seats_block}
)""")
