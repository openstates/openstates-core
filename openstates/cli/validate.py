import click
import json

from ..scrape.schemas.bill import schema as bill_schema
from ..scrape.schemas.event import schema as event_schema
from ..scrape.schemas.jurisdiction import schema as jurisdiction_schema
from ..scrape.schemas.organization import schema as organization_schema
from ..scrape.schemas.vote_event import schema as vote_event_schema
from ..scrape.base import validator_setup


@click.command()
@click.argument("scraper_entity_type", type=click.Choice(["bill", "event", "jurisdiction", "organization", "vote_event"]))
@click.argument("filepath", type=click.Path(exists=True))
def main(
    scraper_entity_type: str,
    filepath: str,
) -> None:
    """Validate a JSON file against scraper data schema. scraper_entity_type may be bill, event, jurisdiction,
    organization, vote_event. filepath needs to be a json file"""
    with open(filepath) as json_file:
        data = json.load(json_file)

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

    validator = validator_setup(schema)
    validator.validate(data)
    click.secho(f"{filepath} is a valid {scraper_entity_type} object")


if __name__ == "__main__":
    main()
