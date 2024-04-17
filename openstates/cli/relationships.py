import click
import logging
import logging.config
from typing import Union
from openstates.utils import abbr_to_jid
from ..utils.django import init_django
from ..utils import transformers
from ..exceptions import InternalError
from .. import settings


# Attempt to fix bill identifiers in the DB that were NOT normalized when saved the first time
# non-normalized bill identifiers will never be matchable to a bill.identifier value
def fix_abnormal_related_bill_identifiers(jurisdiction_id: str) -> None:
    # import of model has to be after django_init
    from ..data.models import RelatedBill
    abnormal_unresolved_rb = RelatedBill.objects.filter(
        bill__legislative_session__jurisdiction_id=jurisdiction_id,
        related_bill=None,
    ).exclude(identifier__contains=' ')
    for rb in abnormal_unresolved_rb:
        new_identifier = transformers.fix_bill_id(rb.identifier)
        if new_identifier is not rb.identifier:
            # update this related bill row with normalized identifier
            rb.identifier = new_identifier
            rb.save()


@click.command(help="Resolve unresolved relationships between entities")
@click.argument("jurisdiction_abbreviation")
@click.option(
    "--log_level",
    help="Set the level of logging to output.",
    default="INFO"
)
@click.option(
    "--session",
    help="Session identifier, used to restrict resolution to within a specific session",
    default=None
)
def main(jurisdiction_abbreviation: str, log_level: str, session: Union[str, None]) -> None:
    # set up logging
    logger = logging.getLogger("openstates")
    handler_level = log_level
    settings.LOGGING["handlers"]["default"]["level"] = handler_level  # type: ignore
    logging.config.dictConfig(settings.LOGGING)

    # set up django for DB access
    # has to be done before any importer can be imported (?)
    init_django()
    from openstates.importers import resolve_related_bills

    logger.info(f"Beginning resolution of bill relationships for {jurisdiction_abbreviation}, session: {session}")
    jurisdiction_id = abbr_to_jid(jurisdiction_abbreviation)

    # Prep: resolve any non-normalized bill identifiers in related bill data
    # ie if RelatedBill has an identifier like "A1675" instead of "A 1675", then it can't be matched to a real bill
    # (this was a historical problem only fixed in mid 2024)
    fix_abnormal_related_bill_identifiers(jurisdiction_id)

    # Run the resolution logic
    try:
        resolve_related_bills(jurisdiction_id, session, logger)
    except InternalError as e:
        logger.error(f"Error during bill relationship resolution for {jurisdiction_abbreviation}: {e}")


if __name__ == "__main__":
    main()
