import click
from django.db import transaction
import openstates_metadata as metadata
from ..utils.django import init_django
from ..importers.postprocessing import update_bill_fields


def update_bill_fields_for_state(abbr):
    from ..data.models import Bill

    state = metadata.lookup(abbr=abbr)

    with transaction.atomic():
        bills = Bill.objects.filter(
            legislative_session__jurisdiction=state.jurisdiction_id
        )

        with click.progressbar(bills, label=f"updating {abbr} bills") as bills_p:
            for bill in bills_p:
                update_bill_fields(bill, save=True)


@click.command()
@click.argument("state", default="all")
def main(state):
    """ updates computed fields """
    init_django()
    if state == "all":
        abbrs = metadata.STATES_BY_ABBR.keys()
        for abbr in abbrs:
            update_bill_fields_for_state(abbr)
    else:
        update_bill_fields_for_state(state)
