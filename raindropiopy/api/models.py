"""All abstract data types to interact with Raindrop's API."""
from __future__ import annotations

import datetime
import enum
import json
from pathlib import Path
from typing import Any, Optional, Sequence

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    EmailStr,
    NonNegativeInt,
    root_validator,
    HttpUrl,
)

from .api import API

__all__ = [
    "Access",
    "AccessLevel",
    "BrokenLevel",
    "Collection",
    "CollectionRef",
    "FontColor",
    "Group",
    "Raindrop",
    "RaindropType",
    "Tag",
    "User",
    "UserFiles",
    "UserRef",
    "View",
]

# Base URL
URL = "https://api.raindrop.io/rest/v1/{path}"


class AccessLevel(enum.IntEnum):
    """Map the Access levels defined by Raindrop's API."""

    readonly = 1
    collaborator_read = 2
    collaborator_write = 3
    owner = 4


class CacheStatus(enum.Enum):
    """Represents the various states the cache of a Raindrop might be in."""

    ready = "ready"
    retry = "retry"
    failed = "failed"
    invalid_origin = "invalid-origin"
    invalid_timeout = "invalid-timeout"
    invalid_size = "invalid-size"


class View(enum.Enum):
    """Map the names of the views for Raindrop's API."""

    list = "list"
    simple = "simple"
    grid = "grid"
    masonry = "masonry"


class CollectionRef(BaseModel):
    """Represents a *reference* to a Raindrop Collection (almost a TypeVar of id: int)."""

    id: int = Field(None, alias="$id")


# We define the 3 "system" collections in the Raindrop environment:
CollectionRef.All = CollectionRef(**{"$id": 0})
CollectionRef.Trash = CollectionRef(**{"$id": -99})
CollectionRef.Unsorted = CollectionRef(**{"$id": -1})


class UserRef(BaseModel):
    """Represents a *reference* to :class:`User` object."""

    id: int = Field(None, alias="$id")
    ref: str = Field(None, alias="$user")


class Access(BaseModel):
    """Represents Access control of Collections."""

    level: AccessLevel
    draggable: bool


class Collection(BaseModel):
    """Represents a concrete Raindrop Collection."""

    id: int = Field(None, alias="_id")
    title: str
    user: UserRef

    access: Access | None
    collaborators: list[Any] | None = []
    color: str | None = None
    count: NonNegativeInt
    cover: list[str] | None = []
    created: datetime.datetime | None
    expanded: bool = False
    lastUpdate: datetime.datetime | None
    parent: int | None  # Id of parent collection
    public: bool | None
    sort: NonNegativeInt | None
    view: View | None

    @classmethod
    def get_roots(cls, api: API) -> Sequence[Collection]:
        """Get "root" Raindrop collections."""
        ret = api.get(URL.format(path="collections"))
        items = ret.json()["items"]
        return [cls(**item) for item in items]

    @classmethod
    def get_childrens(cls, api: API) -> Sequence[Collection]:
        """Get the "child" Raindrop collections (ie. all below root level)."""
        ret = api.get(URL.format(path="collections/childrens"))
        items = ret.json()["items"]
        return [cls(**item) for item in items]

    @classmethod
    def get_collections(cls, api: API) -> Sequence[Collection]:
        """Query *ALL* collections. Wrapper on get_roots and get_childrens.

        (hiding the distinction between root/child collections)
        """
        return cls.get_roots(api) + cls.get_childrens(api)

    @classmethod
    def get(cls, api: API, id: int) -> Collection:
        """Return a Raindrop collection based on it's id."""
        url = URL.format(path=f"collection/{id}")
        item = api.get(url).json()["item"]
        return cls(**item)

    @classmethod
    def create(
        cls,
        api: API,
        view: Optional[View] = None,
        title: Optional[str] = None,
        sort: Optional[int] = None,
        public: Optional[bool] = None,
        parent: Optional[int] = None,
        cover: Optional[Sequence[str]] = None,
    ) -> Collection:
        """Create a new Raindrop collection."""
        args: dict[str, Any] = {}
        if view is not None:
            args["view"] = view
        if title is not None:
            args["title"] = title
        if sort is not None:
            args["sort"] = sort
        if public is not None:
            args["public"] = public
        if parent is not None:
            args["parent"] = parent
        if cover is not None:
            args["cover"] = cover

        url = URL.format(path="collection")
        item = api.post(url, json=args).json()["item"]
        return cls(**item)

    @classmethod
    def update(
        cls,
        api: API,
        id: int,
        expanded: Optional[bool] = None,
        view: Optional[View] = None,
        title: Optional[str] = None,
        sort: Optional[int] = None,
        public: Optional[bool] = None,
        parent: Optional[int] = None,
        cover: Optional[Sequence[str]] = None,
    ) -> Collection:
        """Update an existing Raindrop collection with any of the attribute values provided."""
        args: dict[str, Any] = {}
        for attr in ["expanded", "view", "title", "sort", "public", "parent", "cover"]:
            if (value := locals().get(attr)) is not None:
                args[attr] = value
        url = URL.format(path=f"collection/{id}")
        item = api.put(url, json=args).json()["item"]
        return cls(**item)

    @classmethod
    def remove(cls, api: API, id: int) -> None:
        """Remove/delete a Raindrop collection."""
        api.delete(URL.format(path=f"collection/{id}"), json={})

    @classmethod
    def get_or_create(cls, api: API, title: str) -> Collection:
        """Get a Raindrop collection based on it's *title*, if it doesn't exist, create it.

        Return the ID associated with the collection with specified collection title (this
        doesn't seem to be a supported method of the Raindrop API directly). If collection
        is not found, add it!.
        """
        # Note: Since
        for collection in Collection.get_roots(api):
            if title.casefold() == collection.title.casefold():
                return collection

        # Doesn't exist, create it!
        return Collection.create(api, title=title)


class BrokenLevel(enum.Enum):
    """Enumerate user levels."""

    basic = "basic"
    default = "default"
    strict = "strict"
    off = "off"


class FontColor(enum.Enum):
    """Enumerate user display themes available."""

    sunset = "sunset"
    night = "night"


class UserConfig(BaseModel):
    """Sub-model defining a Raindrop user's configuration."""

    broken_level: BrokenLevel = None
    font_color: FontColor | None = None
    font_size: int
    last_collection: int
    raindrops_view: View


class Group(BaseModel):
    """Sub-model defining a Raindrop user group."""

    title: str
    hidden: bool
    sort: NonNegativeInt
    collectionids: list[int] = Field(None, alias="collections")


class UserFiles(BaseModel):
    """Sub-model defining a file associated with a user (?)."""

    used: int
    size: PositiveInt
    lastCheckPoint: datetime.datetime


class User(BaseModel):
    """Raindrop User model."""

    id: int = Field(None, alias="_id")
    email: EmailStr
    email_MD5: str | None = None
    files: UserFiles
    fullName: str
    groups: list[Group]
    password: bool  # My interpretation: "does this user have a password?"
    pro: bool
    registered: datetime.datetime

    @classmethod
    def get(cls, api: API) -> User:
        """Get all the information about the Raindrop user associated with the API token."""
        user = api.get(URL.format(path="user")).json()["user"]
        return cls(**user)


class SystemCollection(BaseModel):
    """Raindrop System Collection model, ie. collections for Unsorted, Trash and 'All'."""

    id: int = Field(None, alias="_id")
    count: NonNegativeInt
    title: str | None

    @root_validator(pre=False)
    def _map_systemcollection_id_to_title(cls, values):
        """Map the hard-coded id's of the System Collections to the descriptions used on the UI."""
        _titles = {
            CollectionRef.Unsorted.id: "Unsorted",
            CollectionRef.All.id: "All",
            CollectionRef.Trash.id: "Trash",
        }
        values["title"] = _titles.get(values["id"])
        return values

    @classmethod
    def get_status(cls, api: API) -> User:
        """Get the count of Raindrops across all 3 'system' collections."""
        items = api.get(URL.format(path="user/stats")).json()["items"]
        return [cls(**item) for item in items]


class RaindropType(enum.Enum):
    """Map the types of Raindrop bookmarks possible (ie. what type of content they hold)."""

    link = "link"
    article = "article"
    image = "image"
    video = "video"
    document = "document"
    audio = "audio"


class File(BaseModel):
    """Represents the attributes associated with a file within a document-based Raindrop."""

    name: str
    size: PositiveInt
    type: str


class Cache(BaseModel):
    """Represents the cache information of Raindrop."""

    status: CacheStatus
    size: PositiveInt
    created: datetime.datetime


class CreatorRef(BaseModel):
    """Represents original creator of the Raindrop if different from the current user (ie. shared collections)."""

    id: int = Field(alias="_id")
    fullName: str


class Raindrop(BaseModel):
    """Core class of a Raindrop bookmark 'item'."""

    # "Main" fields (per https://developer.raindrop.io/v1/raindrops)
    id: int = Field(None, alias="_id")
    collection: CollectionRef | Collection = CollectionRef.Unsorted
    cover: str | None
    created: datetime.datetime | None
    domain: str | None
    excerpt: str | None  # aka 'Description' on the Raindrop UI.
    lastUpdate: datetime.datetime | None
    link: HttpUrl | None
    media: list[dict[str, Any]] | None
    tags: list[str] | None
    title: str | None
    type: RaindropType | None
    user: UserRef | None

    # "Other" fields:
    broken: bool | None
    cache: Cache | None
    file: File | None
    important: bool | None  # aka marked as Favorite.

    @classmethod
    def get(cls, api: API, id: int) -> Raindrop:
        """Return a Raindrop bookmark based on it's id."""
        item = api.get(URL.format(path=f"{id}")).json()["item"]
        return cls(**item)

    @classmethod
    def create_link(
        cls,
        api: API,
        link: str,
        collection: Optional[Collection | CollectionRef, int] = None,
        cover: Optional[str] = None,
        created: Optional[datetime.datetime] = None,
        excerpt: Optional[str] = None,
        html: Optional[str] = None,
        important: Optional[bool] = None,
        lastUpdate: Optional[datetime.datetime] = None,
        media: Optional[Sequence[dict[str, Any]]] = None,
        order: Optional[int] = None,
        pleaseParse: bool = True,
        tags: Optional[Sequence[str]] = None,
        title: Optional[str] = None,
        type: Optional[str] = None,
    ) -> Raindrop:
        """Create a new link-type Raindrop bookmark."""
        # NOTE: We have small code style conflict here between Vulture
        # and Ruff, specifically:

        # Vulture will report all the optional variables above as
        # "unused". This is clearly technically true as their only
        # appearance below is as a string to the arg below from which
        # we take the actual value of the inbound argument from
        # locals(), instead of referring to the argument explicitly.
        #
        # However, converting all of these to a (rather lengthy set)
        # of simple statements like:
        #
        # if <arg> is not None:
        #     args[<arg>] = <arg>
        #
        # keeps Vulture happy but now trips the McCabe complexity
        # metric(!) implemented in our Ruff pre-commit pass due to the
        # number of conditionals in a single method!
        #
        # While, we /could/, convert to kwargs, we lose the documentation
        # and verbosity available with explicit arguments.
        #
        # Thus, for now, we *leave* vulture out of pre-commit and
        # simply run it manually as necessary (through our justfile)

        # Setup the args that will be passed to the underlying
        # Raindrop API, only link is absolutely required, rest are
        # optional!
        args: dict[str, Any] = {"link": link}

        if pleaseParse:
            args["pleaseParse"] = {}

        for attr in [
            "cover",
            "created",
            "excerpt",
            "html",
            "important",
            "lastUpdate",
            "media",
            "order",
            "tags",
            "title",
            "type",
        ]:
            if (value := locals().get(attr)) is not None:
                args[attr] = value

        if collection is not None:
            # <collection> arg could be *either* an actual collection
            # or simply an int collection "id" already, handle either:
            if isinstance(collection, (Collection, CollectionRef)):
                args["collection"] = {"$id": collection.id}
            else:
                args["collection"] = {"$id": collection}

        url = URL.format(path="raindrop")
        item = api.post(url, json=args).json()["item"]
        return cls(**item)

    @classmethod
    def create_file(
        cls,
        api: API,
        path: Path,
        content_type: str,
        collection: int = -1,
        tags: Optional[Sequence[str]] = None,
        title: Optional[str] = None,
    ) -> Raindrop:
        """Create a new file-based Raindrop bookmark."""
        url = URL.format(path="raindrop/file")

        # Structure here confirmed through communication with RustemM
        # on 2022-11-29 and his subsequent update to API docs.
        data = {"collectionId": str(collection)}
        files = {"file": (path.name, open(path, "rb"), content_type)}
        item = api.put_file(url, path, data, files).json()["item"]
        raindrop = cls(**item)

        # The Raindrop API's "Create Raindrop From File" does not
        # allow us to set other attributes, thus, we need to check if
        # any of the possible attributes need to be set and do so
        # explicitly with another call:
        args: dict[str, Any] = {}
        if title is not None:
            args["title"] = title
        if tags is not None:
            args["tags"] = tags
        if args:
            url = URL.format(path=f"raindrop/{raindrop.id}")
            item = api.put(url, json=args).json()["item"]
            return cls(**item)
        else:
            return raindrop

    @classmethod
    def update(
        cls,
        api: API,
        id: int,
        collection: Optional[Collection | CollectionRef, int] = None,
        cover: Optional[str] = None,
        created: Optional[datetime.datetime] = None,
        excerpt: Optional[str] = None,
        html: Optional[str] = None,
        important: Optional[bool] = None,
        lastUpdate: Optional[datetime.datetime] = None,
        link: Optional[str] = None,
        media: Optional[Sequence[dict[str, Any]]] = None,
        order: Optional[int] = None,
        pleaseParse: Optional[bool] = False,
        tags: Optional[Sequence[str]] = None,
        title: Optional[str] = None,
        type: Optional[str] = None,
    ) -> Raindrop:
        """Update an existing Raindrop bookmark with any of the attribute values provided."""
        # Setup the args that will be passed to the underlying Raindrop API
        # optional!
        args: dict[str, Any] = {}

        if pleaseParse:
            args["pleaseParse"] = {}

        for attr in [
            "cover",
            "created",
            "excerpt",
            "html",
            "important",
            "lastUpdate",
            "link",
            "media",
            "order",
            "tags",
            "title",
            "type",
        ]:
            if (value := locals().get(attr)) is not None:
                args[attr] = value

        if collection is not None:
            # <collection> arg could be *either* an actual collection
            # or simply an int collection "id" already, handle either:
            if isinstance(collection, (Collection, CollectionRef)):
                args["collection"] = collection.id
            else:
                args["collection"] = collection

        url = URL.format(path=f"raindrop/{id}")
        item = api.put(url, json=args).json()["item"]
        return cls(**item)

    @classmethod
    def remove(cls, api: API, id: int) -> None:
        """Remove/delete a Raindrop bookmark."""
        api.delete(URL.format(path=f"raindrop/{id}"), json={})

    @classmethod
    def search_paged(
        cls,
        api: API,
        collection: CollectionRef = CollectionRef.All,
        page: int = 0,
        perpage: int = 50,
        word: Optional[str] = None,
        tag: Optional[str] = None,
        important: Optional[bool] = None,
    ) -> list[Raindrop]:
        """Lower-level search for bookmarks on a "paged" basis.

        In the specified collection with key word, tag or importance parameters.
        """
        args: list[dict[str, Any]] = []
        if word is not None:
            args.append({"key": "word", "val": word})
        if tag is not None:
            args.append({"key": "tag", "val": tag})
        if important is not None:
            args.append({"key": "important", "val": important})

        params = {"search": json.dumps(args), "perpage": perpage, "page": page}
        url = URL.format(path=f"raindrops/{collection.id}")
        results = api.get(url, params=params).json()
        return [cls(**item) for item in results["items"]]

    @classmethod
    def search(
        cls,
        api: API,
        collection: CollectionRef = CollectionRef.All,
        word: Optional[str] = None,
        tag: Optional[str] = None,
        important: Optional[bool] = None,
    ) -> list[Raindrop]:
        """Search for Raindrops.

        Essentially, a simple wrapper over the paged version above
        """
        page = 0
        results = list()
        while raindrops := Raindrop.search_paged(
            api,
            collection,
            page=page,
            word=word,
            tag=tag,
            important=important,
        ):
            results.extend(raindrops)
            page += 1
        return results


class Tag(BaseModel):
    """Represents existing Tags, either all or just a specific collection."""

    tag: str = Field(None, alias="_id")
    count: int

    @classmethod
    def get(cls, api: API, collection_id: int = None) -> list[Tag]:
        """Get all the tags currently defined, either in a specific collections or across all collections."""
        url = URL.format(path="tags")
        if collection_id:
            url += "/" + str(collection_id)
        items = api.get(url).json()["items"]
        return [Tag(**item) for item in items]

    @classmethod
    def remove(cls, api: API, tags: Sequence[str]) -> None:
        """Remove/delete one or more tags."""
        api.delete(URL.format(path="tags"), json={})
