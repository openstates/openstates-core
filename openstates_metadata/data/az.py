from ..models import State, Chamber, District

AZ = State(
    name="Arizona",
    abbr="AZ",
    capital="Phoenix",
    capital_tz="America/Denver",
    fips="04",
    unicameral=False,
    legislature_name="Arizona State Legislature",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=60,
        title="Representative",
        districts=[
            District("1", 2),
            District("2", 2),
            District("3", 2),
            District("4", 2),
            District("5", 2),
            District("6", 2),
            District("7", 2),
            District("8", 2),
            District("9", 2),
            District("10", 2),
            District("11", 2),
            District("12", 2),
            District("13", 2),
            District("14", 2),
            District("15", 2),
            District("16", 2),
            District("17", 2),
            District("18", 2),
            District("19", 2),
            District("20", 2),
            District("21", 2),
            District("22", 2),
            District("23", 2),
            District("24", 2),
            District("25", 2),
            District("26", 2),
            District("27", 2),
            District("28", 2),
            District("29", 2),
            District("30", 2),
        ],
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=30,
        title="Senator",
        districts=None,
    ),
)