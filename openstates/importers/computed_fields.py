"""
functions in this module should take a single object and update it in place

optionally, they can take a save parameter, that should default to False
but can be set to True to force a save if changes were made
(this allows for usage from CLI)
"""
from ._types import Model


def update_bill_fields(bill: Model, *, save: bool = False) -> None:
    first_action_date = None
    latest_action_date = None
    latest_action_description = ""
    latest_passage_date = None

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
