import typing


class OpenStatesError(Exception):
    """Base class for exceptions from core"""


class InternalError(OpenStatesError):
    """Indication something went wrong inside the backend that never should happen"""


class CommandError(OpenStatesError):
    """Errors from within CLI"""


# import-related errors


class DataImportError(OpenStatesError):
    """A generic error related to the import process."""


class InvalidVoteEventError(DataImportError):
    """Attempt to create a vote event without an identifier or bill_id"""


class DuplicateItemError(DataImportError):
    """Attempt was made to import items that resolve to the same database item."""

    def __init__(self, data: dict, obj: typing.Any, data_sources: list[dict] = None):
        # obj.sources can be a list or subobject
        obj_sources = getattr(obj, "sources", [])
        if not isinstance(obj_sources, list):
            obj_sources = list(obj_sources.values_list("url", flat=True))
        super(DuplicateItemError, self).__init__(
            "attempt to import data that would conflict with "
            "data already in the import: {} "
            "(already imported as {})\n"
            "obj1 sources: {}\nobj2 sources: {}".format(
                data,
                obj,
                obj_sources,
                [s["url"] for s in data_sources or []],
            )
        )


class UnresolvedIdError(DataImportError):
    """Attempt was made to resolve an id that has no result."""


# scrape-related errors


class ScrapeError(OpenStatesError):
    """A generic error related to the scrape process."""


class ScrapeValueError(OpenStatesError, ValueError):
    """An invalid value was passed to a scrape object."""


class EmptyScrape(OpenStatesError):
    """Indicate an intentionally empty scrape."""
