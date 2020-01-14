from ..models import State, Chamber, District

AK = State(
    name="Alaska",
    abbr="AK",
    capital="Juneau",
    capital_tz="America/Anchorage",
    fips="02",
    unicameral=False,
    legislature_name="Alaska State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=40,
        title="Representative",
        districts=None,
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=20,
        title="Senator",
        districts=[
            District("A", 1),
            District("B", 1),
            District("C", 1),
            District("D", 1),
            District("E", 1),
            District("F", 1),
            District("G", 1),
            District("H", 1),
            District("I", 1),
            District("J", 1),
            District("K", 1),
            District("L", 1),
            District("M", 1),
            District("N", 1),
            District("O", 1),
            District("P", 1),
            District("Q", 1),
            District("R", 1),
            District("S", 1),
            District("T", 1),
        ],
    ),
)