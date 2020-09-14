import click
from django.db import transaction
from .. import metadata
from ..utils.django import init_django


def update_bill_fields_for_state(abbr):
    from ..data.models import Bill
    from ..importers.computed_fields import update_bill_fields

    state = metadata.lookup(abbr=abbr)

    with transaction.atomic():
        bills = Bill.objects.filter(
            legislative_session__jurisdiction=state.jurisdiction_id
        )

        with click.progressbar(bills, label=f"updating {abbr} bills") as bills_p:
            for bill in bills_p:
                update_bill_fields(bill, save=True)


@click.command()
@click.argument("abbrs", nargs=-1)
def main(abbrs):
    """ updates computed fields """
    init_django()
    if not abbrs:
        abbrs = metadata.STATES_BY_ABBR.keys()
    for abbr in abbrs:
        update_bill_fields_for_state(abbr)
