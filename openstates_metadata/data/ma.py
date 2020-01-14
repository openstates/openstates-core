from ..models import State, Chamber, District

MA = State(
    name="Massachusetts",
    abbr="MA",
    capital="Boston",
    capital_tz="America/New_York",
    fips="25",
    unicameral=False,
    legislature_name="Massachusetts General Court",
    lower=Chamber(
        chamber_type="lower",
        name="House",
        num_seats=160,
        title="Representative",
        districts=[
            District(
                "Tenth Bristol", 1, "ocd-division/country:us/state:ma/sldl:10th_bristol"
            ),
            District(
                "Tenth Essex", 1, "ocd-division/country:us/state:ma/sldl:10th_essex"
            ),
            District(
                "Tenth Hampden", 1, "ocd-division/country:us/state:ma/sldl:10th_hampden"
            ),
            District(
                "Tenth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:10th_middlesex",
            ),
            District(
                "Tenth Norfolk", 1, "ocd-division/country:us/state:ma/sldl:10th_norfolk"
            ),
            District(
                "Tenth Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:10th_plymouth",
            ),
            District(
                "Tenth Suffolk", 1, "ocd-division/country:us/state:ma/sldl:10th_suffolk"
            ),
            District(
                "Tenth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:10th_worcester",
            ),
            District(
                "Eleventh Bristol",
                1,
                "ocd-division/country:us/state:ma/sldl:11th_bristol",
            ),
            District(
                "Eleventh Essex", 1, "ocd-division/country:us/state:ma/sldl:11th_essex"
            ),
            District(
                "Eleventh Hampden",
                1,
                "ocd-division/country:us/state:ma/sldl:11th_hampden",
            ),
            District(
                "Eleventh Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:11th_middlesex",
            ),
            District(
                "Eleventh Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldl:11th_norfolk",
            ),
            District(
                "Eleventh Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:11th_plymouth",
            ),
            District(
                "Eleventh Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:11th_suffolk",
            ),
            District(
                "Eleventh Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:11th_worcester",
            ),
            District(
                "Twelfth Bristol",
                1,
                "ocd-division/country:us/state:ma/sldl:12th_bristol",
            ),
            District(
                "Twelfth Essex", 1, "ocd-division/country:us/state:ma/sldl:12th_essex"
            ),
            District(
                "Twelfth Hampden",
                1,
                "ocd-division/country:us/state:ma/sldl:12th_hampden",
            ),
            District(
                "Twelfth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:12th_middlesex",
            ),
            District(
                "Twelfth Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldl:12th_norfolk",
            ),
            District(
                "Twelfth Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:12th_plymouth",
            ),
            District(
                "Twelfth Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:12th_suffolk",
            ),
            District(
                "Twelfth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:12th_worcester",
            ),
            District(
                "Thirteenth Bristol",
                1,
                "ocd-division/country:us/state:ma/sldl:13th_bristol",
            ),
            District(
                "Thirteenth Essex",
                1,
                "ocd-division/country:us/state:ma/sldl:13th_essex",
            ),
            District(
                "Thirteenth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:13th_middlesex",
            ),
            District(
                "Thirteenth Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldl:13th_norfolk",
            ),
            District(
                "Thirteenth Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:13th_suffolk",
            ),
            District(
                "Thirteenth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:13th_worcester",
            ),
            District(
                "Fourteenth Bristol",
                1,
                "ocd-division/country:us/state:ma/sldl:14th_bristol",
            ),
            District(
                "Fourteenth Essex",
                1,
                "ocd-division/country:us/state:ma/sldl:14th_essex",
            ),
            District(
                "Fourteenth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:14th_middlesex",
            ),
            District(
                "Fourteenth Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldl:14th_norfolk",
            ),
            District(
                "Fourteenth Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:14th_suffolk",
            ),
            District(
                "Fourteenth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:14th_worcester",
            ),
            District(
                "Fifteenth Essex", 1, "ocd-division/country:us/state:ma/sldl:15th_essex"
            ),
            District(
                "Fifteenth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:15th_middlesex",
            ),
            District(
                "Fifteenth Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldl:15th_norfolk",
            ),
            District(
                "Fifteenth Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:15th_suffolk",
            ),
            District(
                "Fifteenth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:15th_worcester",
            ),
            District(
                "Sixteenth Essex", 1, "ocd-division/country:us/state:ma/sldl:16th_essex"
            ),
            District(
                "Sixteenth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:16th_middlesex",
            ),
            District(
                "Sixteenth Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:16th_suffolk",
            ),
            District(
                "Sixteenth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:16th_worcester",
            ),
            District(
                "Seventeenth Essex",
                1,
                "ocd-division/country:us/state:ma/sldl:17th_essex",
            ),
            District(
                "Seventeenth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:17th_middlesex",
            ),
            District(
                "Seventeenth Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:17th_suffolk",
            ),
            District(
                "Seventeenth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:17th_worcester",
            ),
            District(
                "Eighteenth Essex",
                1,
                "ocd-division/country:us/state:ma/sldl:18th_essex",
            ),
            District(
                "Eighteenth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:18th_middlesex",
            ),
            District(
                "Eighteenth Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:18th_suffolk",
            ),
            District(
                "Eighteenth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:18th_worcester",
            ),
            District(
                "Nineteenth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:19th_middlesex",
            ),
            District(
                "Nineteenth Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:19th_suffolk",
            ),
            District(
                "First Barnstable",
                1,
                "ocd-division/country:us/state:ma/sldl:1st_barnstable",
            ),
            District(
                "First Berkshire",
                1,
                "ocd-division/country:us/state:ma/sldl:1st_berkshire",
            ),
            District(
                "First Bristol", 1, "ocd-division/country:us/state:ma/sldl:1st_bristol"
            ),
            District(
                "First Essex", 1, "ocd-division/country:us/state:ma/sldl:1st_essex"
            ),
            District(
                "First Franklin",
                1,
                "ocd-division/country:us/state:ma/sldl:1st_franklin",
            ),
            District(
                "First Hampden", 1, "ocd-division/country:us/state:ma/sldl:1st_hampden"
            ),
            District(
                "First Hampshire",
                1,
                "ocd-division/country:us/state:ma/sldl:1st_hampshire",
            ),
            District(
                "First Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:1st_middlesex",
            ),
            District(
                "First Norfolk", 1, "ocd-division/country:us/state:ma/sldl:1st_norfolk"
            ),
            District(
                "First Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:1st_plymouth",
            ),
            District(
                "First Suffolk", 1, "ocd-division/country:us/state:ma/sldl:1st_suffolk"
            ),
            District(
                "First Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:1st_worcester",
            ),
            District(
                "Twentieth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:20th_middlesex",
            ),
            District(
                "Twenty-First Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:21st_middlesex",
            ),
            District(
                "Twenty-Second Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:22nd_middlesex",
            ),
            District(
                "Twenty-Third Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:23rd_middlesex",
            ),
            District(
                "Twenty-Fourth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:24th_middlesex",
            ),
            District(
                "Twenty-Fifth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:25th_middlesex",
            ),
            District(
                "Twenty-Sixth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:26th_middlesex",
            ),
            District(
                "Twenty-Seventh Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:27th_middlesex",
            ),
            District(
                "Twenty-Eighth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:28th_middlesex",
            ),
            District(
                "Twenty-Ninth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:29th_middlesex",
            ),
            District(
                "Second Barnstable",
                1,
                "ocd-division/country:us/state:ma/sldl:2nd_barnstable",
            ),
            District(
                "Second Berkshire",
                1,
                "ocd-division/country:us/state:ma/sldl:2nd_berkshire",
            ),
            District(
                "Second Bristol", 1, "ocd-division/country:us/state:ma/sldl:2nd_bristol"
            ),
            District(
                "Second Essex", 1, "ocd-division/country:us/state:ma/sldl:2nd_essex"
            ),
            District(
                "Second Franklin",
                1,
                "ocd-division/country:us/state:ma/sldl:2nd_franklin",
            ),
            District(
                "Second Hampden", 1, "ocd-division/country:us/state:ma/sldl:2nd_hampden"
            ),
            District(
                "Second Hampshire",
                1,
                "ocd-division/country:us/state:ma/sldl:2nd_hampshire",
            ),
            District(
                "Second Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:2nd_middlesex",
            ),
            District(
                "Second Norfolk", 1, "ocd-division/country:us/state:ma/sldl:2nd_norfolk"
            ),
            District(
                "Second Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:2nd_plymouth",
            ),
            District(
                "Second Suffolk", 1, "ocd-division/country:us/state:ma/sldl:2nd_suffolk"
            ),
            District(
                "Second Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:2nd_worcester",
            ),
            District(
                "Thirtieth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:30th_middlesex",
            ),
            District(
                "Thirty-First Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:31st_middlesex",
            ),
            District(
                "Thirty-Second Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:32nd_middlesex",
            ),
            District(
                "Thirty-Third Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:33rd_middlesex",
            ),
            District(
                "Thirty-Fourth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:34th_middlesex",
            ),
            District(
                "Thirty-Fifth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:35th_middlesex",
            ),
            District(
                "Thirty-Sixth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:36th_middlesex",
            ),
            District(
                "Thirty-Seventh Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:37th_middlesex",
            ),
            District(
                "Third Barnstable",
                1,
                "ocd-division/country:us/state:ma/sldl:3rd_barnstable",
            ),
            District(
                "Third Berkshire",
                1,
                "ocd-division/country:us/state:ma/sldl:3rd_berkshire",
            ),
            District(
                "Third Bristol", 1, "ocd-division/country:us/state:ma/sldl:3rd_bristol"
            ),
            District(
                "Third Essex", 1, "ocd-division/country:us/state:ma/sldl:3rd_essex"
            ),
            District(
                "Third Hampden", 1, "ocd-division/country:us/state:ma/sldl:3rd_hampden"
            ),
            District(
                "Third Hampshire",
                1,
                "ocd-division/country:us/state:ma/sldl:3rd_hampshire",
            ),
            District(
                "Third Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:3rd_middlesex",
            ),
            District(
                "Third Norfolk", 1, "ocd-division/country:us/state:ma/sldl:3rd_norfolk"
            ),
            District(
                "Third Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:3rd_plymouth",
            ),
            District(
                "Third Suffolk", 1, "ocd-division/country:us/state:ma/sldl:3rd_suffolk"
            ),
            District(
                "Third Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:3rd_worcester",
            ),
            District(
                "Fourth Barnstable",
                1,
                "ocd-division/country:us/state:ma/sldl:4th_barnstable",
            ),
            District(
                "Fourth Berkshire",
                1,
                "ocd-division/country:us/state:ma/sldl:4th_berkshire",
            ),
            District(
                "Fourth Bristol", 1, "ocd-division/country:us/state:ma/sldl:4th_bristol"
            ),
            District(
                "Fourth Essex", 1, "ocd-division/country:us/state:ma/sldl:4th_essex"
            ),
            District(
                "Fourth Hampden", 1, "ocd-division/country:us/state:ma/sldl:4th_hampden"
            ),
            District(
                "Fourth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:4th_middlesex",
            ),
            District(
                "Fourth Norfolk", 1, "ocd-division/country:us/state:ma/sldl:4th_norfolk"
            ),
            District(
                "Fourth Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:4th_plymouth",
            ),
            District(
                "Fourth Suffolk", 1, "ocd-division/country:us/state:ma/sldl:4th_suffolk"
            ),
            District(
                "Fourth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:4th_worcester",
            ),
            District(
                "Fifth Barnstable",
                1,
                "ocd-division/country:us/state:ma/sldl:5th_barnstable",
            ),
            District(
                "Fifth Bristol", 1, "ocd-division/country:us/state:ma/sldl:5th_bristol"
            ),
            District(
                "Fifth Essex", 1, "ocd-division/country:us/state:ma/sldl:5th_essex"
            ),
            District(
                "Fifth Hampden", 1, "ocd-division/country:us/state:ma/sldl:5th_hampden"
            ),
            District(
                "Fifth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:5th_middlesex",
            ),
            District(
                "Fifth Norfolk", 1, "ocd-division/country:us/state:ma/sldl:5th_norfolk"
            ),
            District(
                "Fifth Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:5th_plymouth",
            ),
            District(
                "Fifth Suffolk", 1, "ocd-division/country:us/state:ma/sldl:5th_suffolk"
            ),
            District(
                "Fifth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:5th_worcester",
            ),
            District(
                "Sixth Bristol", 1, "ocd-division/country:us/state:ma/sldl:6th_bristol"
            ),
            District(
                "Sixth Essex", 1, "ocd-division/country:us/state:ma/sldl:6th_essex"
            ),
            District(
                "Sixth Hampden", 1, "ocd-division/country:us/state:ma/sldl:6th_hampden"
            ),
            District(
                "Sixth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:6th_middlesex",
            ),
            District(
                "Sixth Norfolk", 1, "ocd-division/country:us/state:ma/sldl:6th_norfolk"
            ),
            District(
                "Sixth Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:6th_plymouth",
            ),
            District(
                "Sixth Suffolk", 1, "ocd-division/country:us/state:ma/sldl:6th_suffolk"
            ),
            District(
                "Sixth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:6th_worcester",
            ),
            District(
                "Seventh Bristol",
                1,
                "ocd-division/country:us/state:ma/sldl:7th_bristol",
            ),
            District(
                "Seventh Essex", 1, "ocd-division/country:us/state:ma/sldl:7th_essex"
            ),
            District(
                "Seventh Hampden",
                1,
                "ocd-division/country:us/state:ma/sldl:7th_hampden",
            ),
            District(
                "Seventh Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:7th_middlesex",
            ),
            District(
                "Seventh Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldl:7th_norfolk",
            ),
            District(
                "Seventh Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:7th_plymouth",
            ),
            District(
                "Seventh Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldl:7th_suffolk",
            ),
            District(
                "Seventh Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:7th_worcester",
            ),
            District(
                "Eighth Bristol", 1, "ocd-division/country:us/state:ma/sldl:8th_bristol"
            ),
            District(
                "Eighth Essex", 1, "ocd-division/country:us/state:ma/sldl:8th_essex"
            ),
            District(
                "Eighth Hampden", 1, "ocd-division/country:us/state:ma/sldl:8th_hampden"
            ),
            District(
                "Eighth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:8th_middlesex",
            ),
            District(
                "Eighth Norfolk", 1, "ocd-division/country:us/state:ma/sldl:8th_norfolk"
            ),
            District(
                "Eighth Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:8th_plymouth",
            ),
            District(
                "Eighth Suffolk", 1, "ocd-division/country:us/state:ma/sldl:8th_suffolk"
            ),
            District(
                "Eighth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:8th_worcester",
            ),
            District(
                "Ninth Bristol", 1, "ocd-division/country:us/state:ma/sldl:9th_bristol"
            ),
            District(
                "Ninth Essex", 1, "ocd-division/country:us/state:ma/sldl:9th_essex"
            ),
            District(
                "Ninth Hampden", 1, "ocd-division/country:us/state:ma/sldl:9th_hampden"
            ),
            District(
                "Ninth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldl:9th_middlesex",
            ),
            District(
                "Ninth Norfolk", 1, "ocd-division/country:us/state:ma/sldl:9th_norfolk"
            ),
            District(
                "Ninth Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldl:9th_plymouth",
            ),
            District(
                "Ninth Suffolk", 1, "ocd-division/country:us/state:ma/sldl:9th_suffolk"
            ),
            District(
                "Ninth Worcester",
                1,
                "ocd-division/country:us/state:ma/sldl:9th_worcester",
            ),
            District(
                "Barnstable, Dukes and Nantucket",
                1,
                "ocd-division/country:us/state:ma/sldl:barnstable_dukes_and_nantucket",
            ),
        ],
    ),
    upper=Chamber(
        chamber_type="upper",
        name="Senate",
        num_seats=40,
        title="Senator",
        districts=[
            District(
                "Bristol and Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldu:bristol_and_norfolk",
            ),
            District(
                "Cape and Islands",
                1,
                "ocd-division/country:us/state:ma/sldu:cape_and_islands",
            ),
            District(
                "Fifth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:5th_middlesex",
            ),
            District(
                "First Bristol and Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldu:1st_bristol_and_plymouth",
            ),
            District(
                "First Essex", 1, "ocd-division/country:us/state:ma/sldu:1st_essex"
            ),
            District(
                "First Essex and Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:1st_essex_and_middlesex",
            ),
            District(
                "First Hampden and Hampshire",
                1,
                "ocd-division/country:us/state:ma/sldu:1st_hampden_and_hampshire",
            ),
            District(
                "First Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:1st_middlesex",
            ),
            District(
                "First Middlesex and Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldu:1st_middlesex_and_norfolk",
            ),
            District(
                "First Plymouth and Bristol",
                1,
                "ocd-division/country:us/state:ma/sldu:1st_plymouth_and_bristol",
            ),
            District(
                "First Suffolk", 1, "ocd-division/country:us/state:ma/sldu:1st_suffolk"
            ),
            District(
                "First Suffolk and Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:1st_suffolk_and_middlesex",
            ),
            District(
                "First Worcester",
                1,
                "ocd-division/country:us/state:ma/sldu:1st_worcester",
            ),
            District(
                "Fourth Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:4th_middlesex",
            ),
            District("Hampden", 1, "ocd-division/country:us/state:ma/sldu:hampden"),
            District(
                "Berkshire, Hampshire, Franklin and Hampden",
                1,
                "ocd-division/country:us/state:ma/sldu:berkshire_hampshire_franklin_and_hampden",
            ),
            District(
                "Middlesex and Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldu:middlesex_and_suffolk",
            ),
            District(
                "Middlesex and Worcester",
                1,
                "ocd-division/country:us/state:ma/sldu:middlesex_and_worcester",
            ),
            District(
                "Norfolk, Bristol and Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:norfolk_bristol_and_middlesex",
            ),
            District(
                "Norfolk, Bristol and Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldu:norfolk_bristol_and_plymouth",
            ),
            District(
                "Norfolk and Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldu:norfolk_and_plymouth",
            ),
            District(
                "Norfolk and Suffolk",
                1,
                "ocd-division/country:us/state:ma/sldu:norfolk_and_suffolk",
            ),
            District(
                "Plymouth and Barnstable",
                1,
                "ocd-division/country:us/state:ma/sldu:plymouth_and_barnstable",
            ),
            District(
                "Plymouth and Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldu:plymouth_and_norfolk",
            ),
            District(
                "Second Bristol and Plymouth",
                1,
                "ocd-division/country:us/state:ma/sldu:2nd_bristol_and_plymouth",
            ),
            District(
                "Second Essex", 1, "ocd-division/country:us/state:ma/sldu:2nd_essex"
            ),
            District(
                "Second Essex and Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:2nd_essex_and_middlesex",
            ),
            District(
                "Second Hampden and Hampshire",
                1,
                "ocd-division/country:us/state:ma/sldu:2nd_hampden_and_hampshire",
            ),
            District(
                "Second Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:2nd_middlesex",
            ),
            District(
                "Second Middlesex and Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldu:2nd_middlesex_and_norfolk",
            ),
            District(
                "Second Plymouth and Bristol",
                1,
                "ocd-division/country:us/state:ma/sldu:2nd_plymouth_and_bristol",
            ),
            District(
                "Second Suffolk", 1, "ocd-division/country:us/state:ma/sldu:2nd_suffolk"
            ),
            District(
                "Second Suffolk and Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:2nd_suffolk_and_middlesex",
            ),
            District(
                "Second Worcester",
                1,
                "ocd-division/country:us/state:ma/sldu:2nd_worcester",
            ),
            District(
                "Third Essex", 1, "ocd-division/country:us/state:ma/sldu:3rd_essex"
            ),
            District(
                "Third Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:3rd_middlesex",
            ),
            District(
                "Worcester and Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:worcester_and_middlesex",
            ),
            District(
                "Worcester and Norfolk",
                1,
                "ocd-division/country:us/state:ma/sldu:worcester_and_norfolk",
            ),
            District(
                "Worcester, Hampden, Hampshire and Middlesex",
                1,
                "ocd-division/country:us/state:ma/sldu:worcester_hampden_hampshire_and_middlesex",
            ),
            District(
                "Hampshire, Franklin and Worcester",
                1,
                "ocd-division/country:us/state:ma/sldu:hampshire_franklin_and_worcester",
            ),
        ],
    ),
)
