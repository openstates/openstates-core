import datetime
import json
import os
import pytz
import subprocess
import typing
import uuid


def is_valid_uuid(val: str) -> bool:
    """
    Check if a string is a valid UUID.

    Parameters
    ----------
    val : str
        The string to be checked.
    """
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _make_pseudo_id(**kwargs: str) -> str:
    """pseudo ids are just JSON"""
    # ensure keys are sorted so that these are deterministic
    return "~" + json.dumps(kwargs, sort_keys=True)


def get_pseudo_id(pid: str) -> dict[str, typing.Any]:
    if pid[0] != "~":
        raise ValueError("pseudo id doesn't start with ~")
    return json.loads(pid[1:])


def makedirs(dname: str) -> None:
    if not os.path.isdir(dname):
        os.makedirs(dname)


class JSONEncoderPlus(json.JSONEncoder):
    """
    JSONEncoder that encodes datetime objects as Unix timestamps.
    """

    def default(self, obj, **kwargs):  # type: ignore
        if isinstance(obj, datetime.datetime):
            if obj.tzinfo is None:
                raise TypeError("date '%s' is not fully timezone qualified." % (obj))
            obj = obj.astimezone(pytz.UTC)
            return "{}".format(obj.replace(microsecond=0).isoformat())
        elif isinstance(obj, datetime.date):
            return "{}".format(obj.isoformat())
        return super(JSONEncoderPlus, self).default(obj, **kwargs)


def convert_pdf(filename: str, type: str = "xml") -> bytes:
    commands = {
        "text": ["pdftotext", "-layout", filename, "-"],
        "text-nolayout": ["pdftotext", filename, "-"],
        "xml": ["pdftohtml", "-xml", "-stdout", filename],
        "html": ["pdftohtml", "-stdout", filename],
    }
    try:
        pipe = subprocess.Popen(
            commands[type], stdout=subprocess.PIPE, close_fds=True
        ).stdout
    except OSError as e:
        raise EnvironmentError(
            "error running {}, missing executable? [{}]".format(
                " ".join(commands[type]), e
            )
        )
    if not pipe:
        raise EnvironmentError(
            "error running {}, no pipe".format(" ".join(commands[type]))
        )
    data = pipe.read()
    pipe.close()
    return data


def format_datetime(dt: datetime.datetime, timezone: str) -> str:
    return pytz.timezone(timezone).localize(dt).replace(microsecond=0).isoformat()
