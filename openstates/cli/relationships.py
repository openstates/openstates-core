import click
import logging
import logging.config
from openstates.utils import abbr_to_jid
from ..utils.django import init_django
from ..exceptions import InternalError
from .. import settings


@click.command(help="Resolve unresolved relationships between entities")
@click.argument("jurisdiction_abbreviation")
@click.option(
    "--log_level",
    help="Set the level of logging to output.",
    default="INFO"
)
def main(jurisdiction_abbreviation: str, log_level: str) -> None:
    # set up logging
    logger = logging.getLogger("openstates")
    handler_level = log_level
    settings.LOGGING["handlers"]["default"]["level"] = handler_level  # type: ignore
    logging.config.dictConfig(settings.LOGGING)

    # set up django for DB access
    # has to be done before any importer can be imported (?)
    init_django()
    from openstates.importers import resolve_related_bills

    logger.info(f"Beginning resolution of bill relationships for {jurisdiction_abbreviation}")
    jurisdiction_id = abbr_to_jid(jurisdiction_abbreviation)
    try:
        resolve_related_bills(jurisdiction_id, logger)
    except InternalError as e:
        logger.error(f"Error during bill relationship resolution for {jurisdiction_abbreviation}: {e}")


if __name__ == "__main__":
    main()
