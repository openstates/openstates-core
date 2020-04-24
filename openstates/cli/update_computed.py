import click
from django.db import transaction
import openstates_metadata as metadata
from ..utils.django import init_django


def update_bill_fields(bill):
    first_action_date = ""
    latest_action_date = ""
    latest_action_description = ""
    latest_passage_date = ""

    # iterate over according to order
    # first action date will use first by order (<)
    # latest will use latest by order (>=)
    for action in bill.actions.order_by("order"):
        if not first_action_date or action.date < first_action_date:
            first_action_date = action.date
        if not latest_action_date or action.date >= latest_action_date:
            latest_action_date = action.date
            latest_action_description = action.description
        if "passage" in action.classification and (
            not latest_passage_date or action.date >= latest_passage_date
        ):
            latest_passage_date = action.date

    if (
        bill.first_action_date != first_action_date
        or bill.latest_action_date != latest_action_date
        or bill.latest_passage_date != latest_passage_date
        or bill.latest_action_description != latest_action_description
    ):
        bill.first_action_date = first_action_date
        bill.latest_passage_date = latest_passage_date
        bill.latest_action_date = latest_action_date
        bill.latest_action_description = latest_action_description
        bill.save()


def update_bill_fields_for_state(abbr):
    from ..data.models import Bill

    state = metadata.lookup(abbr=abbr)

    with transaction.atomic():
        bills = Bill.objects.filter(
            legislative_session__jurisdiction=state.jurisdiction_id
        )

        with click.progressbar(bills, label=f"updating {abbr} bills") as bills_p:
            for bill in bills_p:
                update_bill_fields(bill)


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
