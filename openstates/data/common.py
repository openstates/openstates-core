"""
Module for declaration of common constants available throughout Open Civic Data code.
"""

DIVISION_ID_REGEX = r"^ocd-division/country:[a-z]{2}(/[^\W\d]+:[\w.~-]+)*$"
JURISDICTION_ID_REGEX = r"^ocd-jurisdiction/country:[a-z]{2}(/[^\W\d]+:[\w.~-]+)*/\w+$"

# helper for making options-only lists
_keys = lambda allopts: [opt[0] for opt in allopts]  # noqa

"""
Policy on addition of new types here:

Because these lists are strictly enforced in lots of code for the purposes of data quality
we have a fairly liberal policy on amendment.

If a type is needed and is not duplicative of another type, it will be accepted.

At the moment, because of this policy, no method exists to extend these lists, instead we will
strive for them to be comprehensive.

The only exception to this would be translations, which should simply exist as translations of
the display name (2nd attribute).
"""


JURISDICTION_CLASSIFICATION_CHOICES = (
    ("state", "State"),
    ("country", "Country"),
    ("municipality", "Municipality"),
)
JURISDICTION_CLASSIFICATIONS = _keys(JURISDICTION_CLASSIFICATION_CHOICES)


SESSION_CLASSIFICATION_CHOICES = (("primary", "Primary"), ("special", "Special"))
SESSION_CLASSIFICATIONS = _keys(SESSION_CLASSIFICATION_CHOICES)


ORGANIZATION_CLASSIFICATION_CHOICES = (
    ("legislature", "Legislature"),
    ("executive", "Executive"),
    ("upper", "Upper Chamber"),
    ("lower", "Lower Chamber"),
    ("party", "Party"),
    ("committee", "Committee"),
    ("government", "Government"),
)
ORGANIZATION_CLASSIFICATIONS = _keys(ORGANIZATION_CLASSIFICATION_CHOICES)

BILL_CLASSIFICATION_CHOICES = (
    ("bill", "Bill"),
    ("resolution", "Resolution"),
    ("concurrent resolution", "Concurrent Resolution"),
    ("joint resolution", "Joint Resolution"),
    ("memorial", "Memorial"),
    ("commemoration", "Commemoration"),
    ("concurrent memorial", "Concurrent Memorial"),
    ("joint memorial", "Joint Memorial"),
    ("proposed bill", "Proposed Bill"),
    ("proclamation", "Proclamation"),
    ("nomination", "Nomination"),
    ("contract", "Contract"),
    ("claim", "Claim"),
    ("appointment", "Appointment"),
    ("constitutional amendment", "Constitutional Amendment"),
    ("petition", "Petition"),
    ("order", "Order"),
    ("concurrent order", "Concurrent Order"),
    ("appropriation", "Appropriation"),
    ("ordinance", "Ordinance"),
    ("motion", "Motion"),
    ("study request", "Study Request"),
    ("concurrent study request", "Concurrent Study Request"),
    ("bill of address", "Bill of Address"),
)
BILL_CLASSIFICATIONS = _keys(BILL_CLASSIFICATION_CHOICES)

BILL_RELATION_TYPE_CHOICES = (
    ("companion", "Companion"),  # a companion in another chamber
    ("prior-session", "Prior Session"),  # an introduction from a prior session
    ("replaced-by", "Replaced By"),  # a bill has been replaced by another
    ("replaces", "Replaces"),  # a bill that replaces another
    ("related", "Related"),  # otherwise related
)
BILL_RELATION_TYPES = _keys(BILL_RELATION_TYPE_CHOICES)

BILL_ACTION_CLASSIFICATION_CHOICES = (
    ("filing", "Filing"),
    ("introduction", "Introduced"),
    ("enrolled", "Enrolled"),
    ("reading-1", "First Reading"),
    ("reading-2", "Second Reading"),
    ("reading-3", "Third Reading"),
    ("passage", "Passage"),
    ("informal-passage", "Informal Passage"),
    ("failure", "Passage Failure"),
    ("withdrawal", "Withdrawal"),
    ("substitution", "Substitution"),
    ("amendment-introduction", "Amendment Introduction"),
    ("amendment-passage", "Amendment Passage"),
    ("amendment-withdrawal", "Amendment Withdrawal"),
    ("amendment-failure", "Amendment Failure"),
    ("amendment-amendment", "Amendment Amended"),
    ("amendment-deferral", "Amendment Deferred or Tabled"),
    ("committee-passage", "Passage from Committee"),
    ("committee-passage-favorable", "Favorable Passage from Committee"),
    ("committee-passage-unfavorable", "Unfavorable Passage from Committee"),
    ("committee-failure", "Failure in Committee"),
    ("executive-receipt", "Received By Executive"),
    ("executive-signature", "Signed By Executive"),
    ("executive-veto", "Veto By Executive"),
    ("executive-veto-line-item", "Line Item Veto By Executive"),
    ("became-law", "Became Law"),
    ("veto-override-passage", "Veto Override Passage"),
    ("veto-override-failure", "Veto Override Failure"),
    ("deferral", "Deferred or Tabled"),
    ("receipt", "Received"),
    ("referral", "Referred"),
    ("referral-committee", "Referred to Committee"),
    ("hearing-held", "Public Hearing Held/Scheduled"),
    ("work-session", "Work Session Held/Scheduled"),
    ("sponsorship", "Authorship/Sponsorship Details"),
    ("carried-over", "Carried Over from Previous Session"),
    ("reported-out-of-committee", "Reported Out of Committee"),
    ("concurrence", "Sent for Concurrence")


)
BILL_ACTION_CLASSIFICATIONS = _keys(BILL_ACTION_CLASSIFICATION_CHOICES)

CITATION_TYPE_CHOICES = {
    ("proposed", "Proposed Change"),
    ("chapter", "Chapter Law"),
    ("final", "Final"),
    ("other", "Other"),
}

CITATION_TYPES = _keys(CITATION_TYPE_CHOICES)

VOTE_CLASSIFICATION_CHOICES = (
    ("passage", "Passage in Chamber"),
    ("amendment", "Amendment Passage"),
    ("committee-passage", "Passage in Committee"),
    ("amendment", "Amendment"),
    ("reading-1", "First Reading"),
    ("reading-3", "Third Reading"),
    ("veto", "Veto"),
    ("veto-override", "Veto Override"),
)
VOTE_CLASSIFICATIONS = _keys(VOTE_CLASSIFICATION_CHOICES)

VOTE_OPTION_CHOICES = (
    ("yes", "Yes"),
    ("no", "No"),
    ("absent", "Absent"),
    ("abstain", "Abstain"),
    ("not voting", "Not Voting"),
    ("paired", "Paired"),
    ("excused", "Excused"),
    # Only for open states.
    ("other", "Other"),
)
VOTE_OPTIONS = _keys(VOTE_OPTION_CHOICES)

VOTE_RESULT_CHOICES = (("pass", "Pass"), ("fail", "Fail"))
VOTE_RESULTS = _keys(VOTE_RESULT_CHOICES)

BILL_VERSION_CHOICES = (
    ("", "Unknown"),
    ("filed", "Filed"),
    ("introduced", "Introduced"),
    ("amendment", "Amendment"),
    ("substituted", "Substituted"),
    ("enrolled", "Enrolled"),
    ("became-law", "Became Law"),
)
BILL_VERSION_CLASSIFICATIONS = _keys(BILL_VERSION_CHOICES)

BILL_DOCUMENT_CHOICES = (
    ("", "Unknown"),
    ("fiscal-note", "Fiscal Note"),
    ("committee-report", "Committee Report"),
    ("summary", "Summary"),
    ("digest", "Digest"),
    ("veto-message", "Veto Message"),
    ("analysis", "Analysis"),
    ("law", "Law"),
)
BILL_DOCUMENT_CLASSIFICATIONS = _keys(BILL_DOCUMENT_CHOICES)

EVENT_MEDIA_CLASSIFICATION_CHOICES = (
    ("audio recording", "Audio Recording"),
    ("video recording", "Video Recording"),
)
EVENT_MEDIA_CLASSIFICATIONS = _keys(EVENT_MEDIA_CLASSIFICATION_CHOICES)

EVENT_DOCUMENT_CLASSIFICATION_CHOICES = (
    ("agenda", "Agenda"),
    ("minutes", "Minutes"),
    ("transcript", "Transcript"),
    ("testimony", "Testimony"),
)
EVENT_DOCUMENT_CLASSIFICATIONS = _keys(EVENT_DOCUMENT_CLASSIFICATION_CHOICES)
