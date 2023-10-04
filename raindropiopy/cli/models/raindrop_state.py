"""Abstract data types to support Raindrop CLI."""
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from pydantic import parse_obj_as
from typing import TypeVar

from rich import print

from raindropiopy import (
    API,
    Collection,
    CollectionRef,
    SystemCollection,
    Tag,
    User,
    View,
)
from raindropiopy.cli.models.spinner import Spinner

RaindropState = TypeVar(
    "RaindropState",
)  # In py3.11, we'll be able to do 'from typing import Self' instead


def get_app_data_path() -> Path | None:
    """Based on the platform, return the normal location for application data."""
    if sys.platform.startswith("linux"):
        data_home = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        if data_home.exists():
            app_data_path = Path(data_home)
        else:
            print("[red]Sorry, unable to find $XDG_DATA_HOME or ~/.local/share")
            return None

    elif sys.platform.startswith("darwin"):
        app_data_path = Path.home() / Path("Library")
        if not app_data_path.exists():
            print("[red]Sorry, unable to find ~/Library folder")
            return None

    elif sys.platform.startswith("win"):
        data_home = os.path.expandvars("%APPDATA%")
        if data_home and Path(data_home).exists():
            app_data_path = Path(data_home)
        else:
            print("[red]Sorry, unable to find %APPDATA%")
            return None
    else:
        raise RuntimeError(f"Sorry, unexpected platform encountered: {sys.platform=}")

    app_data_path /= Path("RaindropIOpy")
    app_data_path.mkdir(exist_ok=True)

    return app_data_path


def get_meta(api: API) -> dict:
    """Query and return the 'meta' information from the System Collection."""
    return SystemCollection.get_meta(api)


@dataclass
class RaindropState:
    """Encapsulate all aspects for current state of the Raindrop environment."""

    # NOT persisted across invocations! (and come in on initial create call):
    api: API
    user: User

    # PERSISTED across invocations in state.json (and are set after create call):
    collections: list[Collection] = field(default_factory=list)
    tags: list[str] = field(
        default_factory=list,
    )  # We don't need to use the Tag pydantic class here...
    meta: dict | None = field(default_factory=dict)
    refreshed: datetime = (
        None  # The timestamp associated with when we last refreshed from RaindropIO
    )

    def get_collection_titles(
        self,
        exclude_unsorted=False,
        casefold=False,
    ) -> list[str]:
        """Return a sorted list of Collection titles, with or without 'Unsorted' and either casefolded or not."""
        if exclude_unsorted:
            titles = [
                collection.title
                for collection in self.collections
                if collection.id > 0 and collection.title
            ]
        else:
            titles = [
                collection.title for collection in self.collections if collection.title
            ]

        if casefold:
            titles = [title.casefold() for title in titles if title]

        return sorted(titles)

    def find_collection(self, title: str) -> Collection | None:
        """Find the actual Collection object with the title provided."""
        for collection in self.collections:
            if title.casefold() == collection.title.casefold():
                return collection
        return None

    def find_collection_by_id(self, id: int) -> Collection | None:
        """Find the actual Collection object with the *id* provided."""
        for collection in self.collections:
            if collection.id == id:
                return collection
        return None

    def refresh(self) -> bool:
        """Refresh the current state of this Raindrop environment (ie. current collections and tags available)."""

        def __refresh_collections() -> None:
            """Gather and set the *COLLECTIONS* associated with the current API user."""
            # This get's us both "root" and "children" collections:
            collections: list[Collection] = Collection.get_collections(self.api)

            # Add the "Unsorted" system collection (we don't care about "Trash" or "All" here)
            for collection in SystemCollection.get_counts(self.api):
                if collection.id == CollectionRef.Unsorted.id:
                    unsorted_collection = Collection(
                        _id=collection.id,
                        count=collection.count,
                        title=collection.title,
                        user=self.user,
                    )
                    collections.append(unsorted_collection)

            # Leave our collections in a presentable order, ie. by Title.
            self.collections = sorted(
                collections,
                key=lambda collection: getattr(collection, "title", ""),
            )

        def __refresh_tags() -> None:
            """Gather and set the *TAGS* associated with the current API user."""
            # use set to get rid of potential duplicates
            tags: set[str] = set([tag.tag for tag in Tag.get(self.api)])
            self.tags = list(sorted(tags))

        ################################################################################
        # Essentially, we want to determine if we need to perform the somewhat time-consuming
        # queries on behalf of the current Collections and Tags. By saving the last known state
        # of these from a previous invocation, we may not have to query for them.
        #
        # We determine this by comparing what essentially seems to be a "lastUpdated" field
        # (specifically: "changedBookmarksDate")on the "meta" object coming back from the
        # SystemCollection. In interactive tests, any time we make *any* modifying change to our
        # RaindropIO environment, this field will get a new timestamp.
        #
        # Thus, by comparing the -last- timestamp we had of this (from our state file) against
        # the -current- timestamp (by asking RaindropIO for it), we can determine if we
        # need to refresh everything again.
        ################################################################################
        with Spinner("Refreshing Raindrop Status..."):
            full_refresh = True
            current_meta = None
            if app_data_path := get_app_data_path():
                state_path = app_data_path / Path("state.json")
                if state_path.exists():
                    self = refresh_from_state_file(self, state_path)

                    current_meta = get_meta(self.api)

                    # Have any changes occurred on Raindrop.IO to cause us to refresh order
                    # are we good to stay with what we already have?
                    full_refresh = (
                        current_meta["changedBookmarksDate"]
                        > self.meta["changedBookmarksDate"]
                    )
                    if False:
                        print(f"   {self.meta['changedBookmarksDate']=}")
                        print(f"{current_meta['changedBookmarksDate']=}")
                        print(f"{full_refresh=}")
                else:
                    print("State file does not exist yet, doing a FULL refresh.")
            else:
                print("No app data path found, can't query for previous state.")

            if full_refresh:
                __refresh_collections()
                __refresh_tags()
                if current_meta:
                    self.meta = current_meta
                else:
                    self.meta = get_meta(self.api)
                self.refreshed = datetime.utcnow()

                if app_data_path:
                    save_save_to_file(self, state_path)
                else:
                    print("No app data path found, can't save current state.")

        return True

    @classmethod
    def factory(cls) -> RaindropState:
        """Log into Raindrop and return a new, refreshed RaindropState instance."""
        with Spinner("Logging into Raindrop..."):
            api: API = API(
                os.environ["RAINDROP_TOKEN"],
            )  # Setup our connection to Raindrop
            try:
                user = User.get(api)  # What user are we currently defined "for"?
            except Exception:
                print(
                    "[red]Sorry, unable to get query Raindrop.IO for the user requested!",
                )
                sys.exit(1)
        state = RaindropState(api=api, user=user)
        state.refresh()
        return state


################################################################################
# Utilities
################################################################################
class RaindropJSONStateEncoder(json.JSONEncoder):
    """Allow for custom object encoding."""

    def default(self, obj):
        """Allow for custom object encoding."""
        if isinstance(obj, Collection):
            return obj.dict()
        elif isinstance(obj, View):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def save_save_to_file(state_: RaindropState, state_path: Path) -> None:
    """Save the RaindropState instance provided to the specified path as JSON."""
    state_dict = {}
    state_dict["collections"] = state_.collections
    state_dict["tags"] = state_.tags
    state_dict["refreshed"] = state_.refreshed
    state_dict["meta"] = state_.meta
    json_string = json.dumps(state_dict, cls=RaindropJSONStateEncoder, indent=4)
    with open(state_path, "w") as fh_json:
        fh_json.write(json_string)


def refresh_from_state_file(state_: RaindropState, state_path: Path) -> RaindropState:
    """Read our state file of collections and tags and place into instance provided."""
    with open(state_path) as fh_json:
        data = json.load(fh_json)
        state_.tags = data.get("tags", [])
        state_.meta = data.get("meta", {})
        state_.refreshed = datetime.fromisoformat(data.get("refreshed"))

        # Collections need a bit more TLC due to the alias of the _id/id field.
        for d_collection in data.get("collections", []):
            collection = parse_obj_as(Collection, d_collection)
            collection.id = d_collection["id"]
            state_.collections.append(collection)

    return state_
