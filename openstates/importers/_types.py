import typing
from django.db.models import Model, Q

# type aliases
_ID = typing.Union[int, str]
_JsonDict = typing.Dict[str, typing.Any]
_DBSpec = typing.Union[_JsonDict, Q]
# TODO: the third parameter in the tuple should be _RelatedModels, but this doesn't
# play nicely with mypy (nested dictionary types may not be supported?)
_RelatedModels = typing.Dict[str, typing.Tuple[Model, str, typing.Dict]]
_TransformerFunc = typing.Callable[[str], str]
_TransformerMapping = typing.Dict[str, _TransformerFunc]
