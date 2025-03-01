import click
import json
import datetime
import jsonschema
from jsonschema import validate, Draft3Validator
from ..scrape.schemas.bill import schema as bill_schema
from ..scrape.schemas.event import schema as event_schema
from ..scrape.schemas.jurisdiction import schema as jurisdiction_schema
from ..scrape.schemas.organization import schema as organization_schema
from ..scrape.schemas.vote_event import schema as vote_event_schema


@click.command()
@click.argument("scraper_entity_type")
@click.argument("filepath", type=click.Path(exists=True))
def main(
    scraper_entity_type: str,
    filepath: str,
) -> None:
    """Validate a JSON file against scraper data schema. scraper_entity_type may be bill, event, jurisdiction,
    organization, vote_event. filepath needs to be a json file"""
    with open(filepath) as json_file:
        entity_instance = json.load(json_file)

    schema = None
    if scraper_entity_type == "bill":
        schema = bill_schema
    elif scraper_entity_type == "event":
        schema = event_schema
    elif scraper_entity_type == "jurisdiction":
        schema = jurisdiction_schema
    elif scraper_entity_type == "organization":
        schema = organization_schema
    elif scraper_entity_type == "vote_event":
        schema = vote_event_schema

    # See openstates/scrape/base.py for source of this validation code
    type_checker = Draft3Validator.TYPE_CHECKER.redefine(
        "datetime", lambda c, d: isinstance(d, (datetime.date, datetime.datetime))
    )
    type_checker = type_checker.redefine(
        "date",
        lambda c, d: (
            isinstance(d, datetime.date) and not isinstance(d, datetime.datetime)
        ),
    )
    ValidatorCls = jsonschema.validators.extend(
        Draft3Validator, type_checker=type_checker
    )
    validate(instance=entity_instance, schema=schema, cls=ValidatorCls)  # type: ignore


if __name__ == "__main__":
    main()
