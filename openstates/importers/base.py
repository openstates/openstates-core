import os
import copy
import glob
import json
import logging
import re
import typing
from datetime import datetime
from django.db.models import Q, Model
from django.db.models.signals import post_save
from .. import settings
from ..data.models import LegislativeSession, Person, Bill
from ..exceptions import DuplicateItemError, UnresolvedIdError, DataImportError
from ..utils import get_pseudo_id, utcnow
from ._types import _ID, _JsonDict, _RelatedModels, _TransformerMapping

_PersonCacheKey = typing.Tuple[str, typing.Optional[str], typing.Optional[str]]


def omnihash(obj: typing.Any) -> int:
    """recursively hash unhashable objects"""
    if isinstance(obj, set):
        return hash(frozenset(omnihash(e) for e in obj))
    elif isinstance(obj, (tuple, list)):
        return hash(tuple(omnihash(e) for e in obj))
    elif isinstance(obj, dict):
        return hash(frozenset((k, omnihash(v)) for k, v in obj.items()))
    else:
        return hash(obj)


def _match(
    dbitem: Model,
    jsonitem: _JsonDict,
    keys: typing.Iterable[str],
    subfield_dict: typing.Dict[str, typing.Any],
) -> bool:
    # check if all keys (excluding subfields) match
    for k in keys:
        if k not in subfield_dict and getattr(dbitem, k) != jsonitem.get(k, None):
            return False

    # all fields match so far, possibly equal, just check subfields now
    for k in subfield_dict:
        jsonsubitems = jsonitem[k]
        dbsubitems = list(getattr(dbitem, k).all())
        if items_differ(jsonsubitems, dbsubitems, subfield_dict[k][2]):
            return False

    # if we got here, item values match
    return True


def items_differ(
    jsonitems: typing.List[_JsonDict],
    dbitems: typing.List[Model],
    subfield_dict: _JsonDict,
) -> bool:
    """check whether or not jsonitems and dbitems differ"""

    # short circuit common cases
    if len(jsonitems) == len(dbitems) == 0:
        # both are empty
        return False
    elif len(jsonitems) != len(dbitems):
        # if lengths differ, they're definitely different
        return True

    original_jsonitems = jsonitems
    jsonitems = copy.deepcopy(jsonitems)
    keys = jsonitems[0].keys()

    # go over dbitems looking for matches
    for dbitem in dbitems:
        order = getattr(dbitem, "order", None)

        match = None

        # if we have an order, we can just check one item
        if order is not None:
            # use original so that pop calls don't affect ordering
            if not _match(dbitem, original_jsonitems[order], keys, subfield_dict):
                # short circuit if there isn't a match in the right spot
                return True

        # need to get position of match to remove
        for i, jsonitem in enumerate(jsonitems):
            if _match(dbitem, jsonitem, keys, subfield_dict):
                match = i

        if match is not None:
            # item exists in both, remove from jsonitems
            jsonitems.pop(match)
        else:
            # exists in db but not json
            return True

    # if we get here, jsonitems has to be empty because we asserted that the length was
    # the same and we found a match for each thing in dbitems, here's a safety check just in case
    if jsonitems:  # pragma: no cover
        return True

    return False


class BaseImporter:
    """BaseImporter

    Override:
        get_object(data)
        limit_spec(spec)                [optional, required if pseudo_ids are used]
        prepare_for_db(data)            [optional]
        postimport()                    [optional]
        update_computed_fields(obj)     [optional]
    """

    _type: str
    model_class: Model = None
    related_models: _RelatedModels = {}
    preserve_order: typing.Set[str] = set()
    merge_related: typing.Dict[str, typing.List[str]] = {}
    cached_transformers: _TransformerMapping = {}

    def __init__(self, jurisdiction_id: str, do_postimport=True) -> None:
        self.jurisdiction_id = jurisdiction_id
        self.do_postimport = do_postimport
        self.json_to_db_id: typing.Dict[str, _ID] = {}
        self.duplicates: typing.Dict[str, str] = {}
        self.pseudo_id_cache: typing.Dict[str, typing.Optional[_ID]] = {}
        self.person_cache: typing.Dict[_PersonCacheKey, typing.Optional[str]] = {}
        self.session_cache: typing.Dict[str, LegislativeSession] = {}
        # Get all_session_cache is a list of all sessions available for this jurisdiction.
        # It is different from session_cache: which is a dictionary session(s) that is loaded a session
        # session_cache may not contain all jurisdiction legislative sessions while all_session_cache will.
        self.all_sessions_cache: typing.List[LegislativeSession] = []
        self.logger = logging.getLogger("openstates")
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

        # load transformers from appropriate setting
        if settings.IMPORT_TRANSFORMERS.get(self._type):
            self.cached_transformers = settings.IMPORT_TRANSFORMERS[self._type]

    def get_all_sessions(self) -> typing.List[LegislativeSession]:
        if not self.all_sessions_cache:
            self.all_sessions_cache = LegislativeSession.objects.filter(
                jurisdiction_id=self.jurisdiction_id
            ).order_by("-start_date")
        return self.all_sessions_cache

    def get_session(self, identifier: str) -> LegislativeSession:
        if identifier not in self.session_cache:
            self.session_cache[identifier] = LegislativeSession.objects.get(
                identifier=identifier, jurisdiction_id=self.jurisdiction_id
            )
        return self.session_cache[identifier]

    def limit_spec(self, spec: _JsonDict) -> _JsonDict:
        raise NotImplementedError()

    def get_object(self, object: _JsonDict) -> Model:
        raise NotImplementedError()

    # no-ops to be overriden
    def prepare_for_db(self, data: _JsonDict) -> _JsonDict:
        return data

    def postimport(self) -> None:
        pass

    def update_computed_fields(self, obj: Model) -> None:
        pass

    def resolve_bill(self, bill_id: str, *, date: str) -> typing.Optional[_ID]:
        bill_transform_func = settings.IMPORT_TRANSFORMERS.get("bill", {}).get(
            "identifier", None
        )
        all_sessions = self.get_all_sessions()
        if bill_transform_func:
            bill_id = bill_transform_func(bill_id)

        # Some steps here to first find the session that matches the incoming entity using the entity date
        # If a unique session is not found, then use the session with the latest "start_date"
        date = datetime.fromisoformat(date).strftime("%Y-%m-%d")
        session_ids = [
            session.id
            for session in all_sessions
            if session.start_date <= date
            and (session.end_date >= date or not session.end_date)
        ]

        if len(session_ids) == 1:
            session_id = session_ids.pop()
        else:
            session_id = all_sessions[0].id if all_sessions else None

        objects = Bill.objects.filter(
            legislative_session__id=session_id,
            identifier=bill_id,
        )
        ids = {each.id for each in objects}

        if len(ids) == 1:
            return ids.pop()
        elif len(ids) == 0:
            self.error(f"could not resolve bill id {bill_id}, {date}, no matches")
        else:
            self.error(
                f"could not resolve bill id {bill_id}, {date}, {len(ids)} matches"
            )
        return None

    def resolve_json_id(
        self, json_id: str, allow_no_match: bool = False
    ) -> typing.Optional[_ID]:
        """
        Given an id found in scraped JSON, return a DB id for the object.

        params:
            json_id:        id from json
            allow_no_match: just return None if id can't be resolved

        returns:
            database id

        raises:
            ValueError if id couldn't be resolved
        """
        if not json_id:
            return None

        if json_id.startswith("~"):
            # keep caches of all the pseudo-ids to avoid doing 1000s of lookups during import
            if json_id not in self.pseudo_id_cache:
                spec = get_pseudo_id(json_id)
                spec = self.limit_spec(spec)

                if isinstance(spec, Q):
                    objects = self.model_class.objects.filter(spec)
                else:
                    objects = self.model_class.objects.filter(**spec)
                ids = {each.id for each in objects}
                if len(ids) == 1:
                    self.pseudo_id_cache[json_id] = ids.pop()
                    errmsg = None
                elif not ids:
                    errmsg = "cannot resolve pseudo id to {}: {}".format(
                        self.model_class.__name__, json_id
                    )
                else:
                    errmsg = "multiple objects returned for {} pseudo id {}: {}".format(
                        self.model_class.__name__, json_id, ids
                    )

                # either raise or log error
                if errmsg:
                    if not allow_no_match:
                        raise UnresolvedIdError(errmsg)
                    else:
                        self.error(errmsg)
                        self.pseudo_id_cache[json_id] = None

            # return the cached object
            return self.pseudo_id_cache[json_id]

        # get the id that the duplicate points to, or use self
        json_id = self.duplicates.get(json_id, json_id)

        try:
            return self.json_to_db_id[json_id]
        except KeyError:
            raise UnresolvedIdError("cannot resolve id: {}".format(json_id))

    def import_directory(
        self, datadir: str, allow_duplicates=False
    ) -> typing.Dict[str, typing.Dict]:
        """import a JSON directory into the database"""

        def json_stream() -> typing.Iterator[_JsonDict]:
            # load all json, mapped by json_id
            for fname in glob.glob(os.path.join(datadir, self._type + "_*.json")):
                with open(fname) as f:
                    yield json.load(f)

        return self.import_data(json_stream(), allow_duplicates)

    def _prepare_imports(
        self, dicts: typing.Iterable[_JsonDict]
    ) -> typing.Iterator[typing.Tuple[str, _JsonDict]]:
        """filters the import stream to remove duplicates

        also serves as a good place to override if anything special has to be done to the
        order of the import stream (see OrganizationImporter)
        """
        # hash(json): id
        seen_hashes = {}

        for data in dicts:
            json_id = data.pop("_id")
            if self._type == "vote_event":
                data.pop("bill_identifier", None)

            # map duplicates (using omnihash to tell if json dicts are identical-ish)
            objhash = omnihash(data)
            if objhash not in seen_hashes:
                seen_hashes[objhash] = json_id
                yield json_id, data
            else:
                self.duplicates[json_id] = seen_hashes[objhash]

    def import_data(
        self, data_items: typing.Iterable[_JsonDict], allow_duplicates=False
    ) -> typing.Dict[str, typing.Dict]:
        """import a bunch of dicts together"""
        # keep counts of all actions
        record = {
            "insert": 0,
            "update": 0,
            "noop": 0,
            "start": utcnow(),
            "records": {"insert": [], "update": [], "noop": []},
        }

        for json_id, data in self._prepare_imports(data_items):
            obj_id, what = self.import_item(data, allow_duplicates)
            if not obj_id or not what:
                "Skipping data because it did not have an associated ID or type"
                continue
            self.json_to_db_id[json_id] = obj_id
            record["records"][what].append(obj_id)
            record[what] += 1

        # all objects are loaded, a perfect time to do inter-object resolution and other tasks
        if self.json_to_db_id and self.do_postimport:
            # only do postimport step if requested by client code AND there are some items of this type
            # resolution of bills take a long time if not
            # and events & votes get deleted!
            self.postimport()

        record["end"] = utcnow()

        return {self._type: record}

    def import_item(
        self, data: _JsonDict, allow_duplicates=False
    ) -> typing.Tuple[_ID, str]:
        """function used by import_data"""
        what = "noop"

        # remove the JSON _id (may still be there if called directly)
        data.pop("_id", None)
        # Drop "jurisdiction" and "scraped_at" that is not needed for import
        data.pop("jurisdiction", None)
        data.pop("scraped_at", None)
        if self._type == "vote_event":
            data.pop("bill_identifier", None)

        # add fields/etc.
        data = self.apply_transformers(data)
        try:
            data = self.prepare_for_db(data)
        except UnresolvedIdError:
            return None, what

        try:
            obj = self.get_object(data)
        except self.model_class.DoesNotExist:
            obj = None

        # pull related fields off
        related = {}
        for field in self.related_models:
            related[field] = data.pop(field)

        # obj existed, check if we need to do an update
        if obj:
            # If --allow_duplicates flag is set on client CLI command
            # then we ignore duplicates instead of raising an exception
            if not allow_duplicates and obj.id in self.json_to_db_id.values():
                raise DuplicateItemError(data, obj, related.get("sources", []))
            elif allow_duplicates and obj.id in self.json_to_db_id.values():
                self.logger.warning(f"Ignored a DuplicateItemError for {obj.id}")
            # check base object for changes
            for key, value in data.items():
                if getattr(obj, key) != value:
                    setattr(obj, key, value)
                    what = "update"

            updated = self._update_related(obj, related, self.related_models)
            if updated:
                what = "update"

            if what == "update":
                # make sure to do this after create related
                self.update_computed_fields(obj)
                obj.save()

        # need to create the data
        else:
            what = "insert"
            try:
                obj = self.model_class(**data)
                obj.save()
            except Exception as e:
                raise DataImportError(
                    "{} while importing {} as {}".format(e, data, self.model_class)
                )
            self._create_related(obj, related, self.related_models)

            # make sure to do this after create related
            self.update_computed_fields(obj)

            # Fire post-save signal after related objects are created to allow
            # for handlers make use of related objects
            post_save.send(sender=self.model_class, instance=obj, created=True)

        return obj.id, what

    def _update_related(
        self,
        obj: Model,
        related: typing.Dict[str, typing.List[Model]],
        subfield_dict: _JsonDict,
    ) -> bool:
        """
        update DB objects related to a base object
            obj:            a base object to create related
            related:        dict mapping field names to lists of related objects
            subfield_list:  where to get the next layer of subfields
        """
        # keep track of whether or not anything was updated
        updated = False

        # for each related field - check if there are differences
        for field, items in related.items():
            # get items from database
            dbitems = list(getattr(obj, field).all())
            dbitems_count = len(dbitems)

            # default to doing nothing
            do_delete = do_update = False

            if items and dbitems_count:  # we have items, so does db, check for conflict
                do_delete = do_update = items_differ(
                    items, dbitems, subfield_dict[field][2]
                )
            elif items and not dbitems_count:  # we have items, db doesn't, just update
                do_update = True
            elif not items and dbitems_count:  # db has items, we don't, just delete
                do_delete = True
            # otherwise: no items or dbitems, so nothing is done

            # don't delete if field is in merge_related
            if field in self.merge_related:
                new_items = []
                # build a list of keyfields to existing database objects
                keylist = self.merge_related[field]
                keyed_dbitems = {
                    tuple(getattr(item, k) for k in keylist): item for item in dbitems
                }

                # go through 'new' items
                #   if item with the same keyfields exists:
                #       update the database item w/ the new item's properties
                #   else:
                #       add it to new_items
                for item in items:
                    key = tuple(item.get(k) for k in keylist)
                    dbitem = keyed_dbitems.get(key)
                    if not dbitem:
                        new_items.append(item)
                    else:
                        # update dbitem
                        for fname, val in item.items():
                            setattr(dbitem, fname, val)
                        dbitem.save()

                # import anything that made it to new_items in the usual fashion
                self._create_related(obj, {field: new_items}, subfield_dict)
            else:
                # default logic is to just wipe and recreate subobjects
                if do_delete:
                    updated = True
                    getattr(obj, field).all().delete()
                if do_update:
                    updated = True
                    self._create_related(obj, {field: items}, subfield_dict)

        return updated

    def _create_related(
        self,
        obj: Model,
        related: typing.Dict[str, typing.List[Model]],
        subfield_dict: _JsonDict,
    ) -> None:
        """
        create DB objects related to a base object
            obj:            a base object to create related
            related:        dict mapping field names to lists of related objects
            subfield_list:  where to get the next layer of subfields
        """
        for field, items in related.items():
            subobjects = []
            all_subrelated = []
            Subtype, reverse_id_field, subsubdict = subfield_dict[field]
            for order, item in enumerate(items):
                # pull off 'subrelated' (things that are related to this obj)
                subrelated = {}
                for subfield in subsubdict:
                    subrelated[subfield] = item.pop(subfield)

                if field in self.preserve_order:
                    item["order"] = order

                item[reverse_id_field] = obj.id

                try:
                    subobjects.append(Subtype(**item))
                    all_subrelated.append(subrelated)
                except Exception as e:
                    raise DataImportError(
                        "{} while importing {} as {}".format(e, item, Subtype)
                    )

            # add all subobjects at once (really great for actions & votes)
            try:
                Subtype.objects.bulk_create(subobjects)
            except Exception as e:
                raise DataImportError(
                    "{} while importing {} as {}".format(e, subobjects, Subtype)
                )

            # after import the subobjects, import their subsubobjects
            for subobj, subrel in zip(subobjects, all_subrelated):
                self._create_related(subobj, subrel, subsubdict)

    def apply_transformers(
        self, data: _JsonDict, transformers: typing.Optional[_TransformerMapping] = None
    ) -> _JsonDict:
        if transformers is None:
            transformers = self.cached_transformers

        if isinstance(data, list):
            for data_item in data:
                self.apply_transformers(data_item, transformers)
        else:
            for key, key_transformers in transformers.items():
                if key not in data:
                    continue
                if isinstance(key_transformers, list):
                    for transformer in key_transformers:
                        data[key] = transformer(data[key])
                elif isinstance(key_transformers, dict):
                    self.apply_transformers(data[key], key_transformers)
                else:
                    data[key] = key_transformers(data[key])

        return data

    def get_seen_sessions(self) -> typing.List[str]:
        return [s.id for s in self.session_cache.values()]

    def resolve_person(
        self,
        psuedo_person_id: str,
        start_date: typing.Optional[str] = None,
        end_date: typing.Optional[str] = None,
        org_classification: typing.Optional[str] = None,
    ) -> str:
        cache_key = (psuedo_person_id, start_date, end_date)
        if cache_key in self.person_cache:
            return self.person_cache[cache_key]

        # turn spec into DB query
        spec = get_pseudo_id(psuedo_person_id)

        # if chamber is included in pseudo_person_id, use that as org_classification
        if "chamber" in spec and org_classification is None:
            org_classification = spec["chamber"]
            del spec["chamber"]

        if list(spec.keys()) == ["name"]:
            # if we're just resolving on name, include other names and family name
            name = spec["name"]
            name = re.sub(r"\s+", " ", name)
            spec = (
                Q(name__iexact=name)
                | Q(other_names__name__iexact=name)
                | Q(family_name__iexact=name)
            )
        else:
            spec = Q(**spec)

        spec &= Q(
            memberships__organization__jurisdiction_id=self.jurisdiction_id,
        )

        if org_classification:
            spec &= Q(memberships__organization__classification=org_classification)
        else:
            spec &= Q(
                memberships__organization__classification__in=(
                    "upper",
                    "lower",
                    "legislature",
                )
            )

        # we don't know what dates we have available to us... it can be any configuration
        # of start/end dates or they can all be null.  Instead of requiring a strict overlap
        # we use them to exclude people that are definitely not serving in the session:
        # if we know when the session started, ensure they are either in office still or
        #   that their end date was after the start of the session
        if start_date:
            spec &= Q(memberships__end_date="") | Q(
                memberships__end_date__gt=start_date
            )
        # if we know when the session ended, ensure that they didn't start after it ended
        if end_date:
            spec &= Q(memberships__start_date="") | Q(
                memberships__start_date__lt=end_date
            )

        query_result = Person.objects.filter(spec).values("id", "current_role")
        result_set = set([p["id"] for p in query_result])
        errmsg = None
        if len(result_set) == 1:
            self.person_cache[cache_key] = result_set.pop()
        elif not result_set:
            errmsg = "no people returned for spec"
        else:
            # If there are multiple rows returned see we can get the active legislator.
            ids = set([p["id"] for p in query_result if p["current_role"] is not None])
            if len(ids) == 1:
                self.person_cache[cache_key] = ids.pop()
            else:
                errmsg = "multiple people returned for spec"

        # either raise or log error
        if errmsg:
            self.error(errmsg)
            self.person_cache[cache_key] = None

        # return the newly-cached object
        return self.person_cache[cache_key]
