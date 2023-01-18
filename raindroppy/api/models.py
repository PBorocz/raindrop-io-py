"""All abstract data types to interact with Raindrop's API."""
from __future__ import annotations

import datetime
import enum
import json
from pathlib import Path
from typing import Any, ClassVar, Optional, Sequence

from dateutil.parser import parse as dateparse
from jashin.dictattr import DictModel, ItemAttr, SequenceAttr

from .api import API

__all__ = [
    "Access",
    "AccessLevel",
    "BrokenLevel",
    "Collection",
    "CollectionRef",
    "DictModel",
    "FontColor",
    "Group",
    "Raindrop",
    "RaindropType",
    "Tag",
    "User",
    "UserConfig",
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


class View(enum.Enum):
    """Map the names of the views for Raindrop's API."""

    list = "list"
    simple = "simple"
    grid = "grid"
    masonry = "masonry"


class CollectionRef(DictModel):
    """Abstract data type for a Raindrop Collection reference."""

    All: ClassVar[CollectionRef]
    Trash: ClassVar[CollectionRef]
    Unsorted: ClassVar[CollectionRef]

    id = ItemAttr[int](name="$id")


CollectionRef.All = CollectionRef({"$id": 0})
CollectionRef.Trash = CollectionRef({"$id": -99})
CollectionRef.Unsorted = CollectionRef({"$id": -1})


class UserRef(DictModel):
    """Represents reference to :class:`User` object."""

    #: (:class:`int`) The id of the :class:`User`.
    id = ItemAttr[int](name="$id")


class Access(DictModel):
    """Represents Access control of Collections."""

    #: (:class:`UserRef`) The user for this permission.
    level = ItemAttr(AccessLevel)

    #: (:class:`bool`) True if possible to change parent.
    draggable = ItemAttr[bool]()


class Collection(DictModel):
    """Represents a concrete Raindrop Collection."""

    #: (:class:`int`) The id of the collection.
    id = ItemAttr[int](name="_id")

    #: (:class:`Access`) Permissions for this collection
    access = ItemAttr(Access)

    collaborators = ItemAttr[Optional[list[Any]]](default=None)
    color = ItemAttr[Optional[str]](default=None)
    count = ItemAttr[int]()
    cover = ItemAttr[list[str]]()
    created = ItemAttr(dateparse)
    expanded = ItemAttr[bool]()
    lastUpdate = ItemAttr(dateparse)
    parent = ItemAttr[Optional[CollectionRef]](CollectionRef, default=None)
    public = ItemAttr[bool]()
    sort = ItemAttr[int]()
    title = ItemAttr[str]()
    user = ItemAttr(UserRef)
    view = ItemAttr(View)

    @classmethod
    def get_roots(cls, api: API) -> Sequence[Collection]:
        """Get root collections."""
        ret = api.get(URL.format(path="collections"))
        items = ret.json()["items"]
        return [cls(item) for item in items]

    @classmethod
    def get_childrens(cls, api: API) -> Sequence[Collection]:
        """Get the "child" collections (ie. all below 'root' level)."""
        ret = api.get(URL.format(path="collections/childrens"))
        items = ret.json()["items"]
        return [cls(item) for item in items]

    @classmethod
    def get_collections(cls, api: API) -> Sequence[Collection]:
        """Utility method for query *ALL* collections.

        Ie. hiding the distinction between "root" and "child"
        collections.
        """
        return cls.get_roots(api) + cls.get_childrens(api)

    @classmethod
    def get(cls, api: API, id: int) -> Collection:
        """Primary call to return a Raindrop collection based on it's id."""
        url = URL.format(path=f"collections/{id}")
        item = api.get(url).json()["item"]
        return cls(item)

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
        return Collection(item)

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
        return Collection(item)

    @classmethod
    def remove(cls, api: API, id: int) -> None:
        """Remove/delete a Raindrop collection."""
        api.delete(URL.format(path=f"collection/{id}"), json={})

    @classmethod
    def get_or_create(cls, api: API, title: str) -> Collection:
        """Get a Raindrop collection based on it's *title*, creating it doesn't exist.

        Return the ID associated with the collection with specified
        collection title (this doesn't seem to be a supported method
        of the Raindrop API directly). If collection is not found, add
        it!.
        """
        # Note: Since
        for collection in Collection.get_roots(api):
            if title.casefold() == collection.values.get("title").casefold():
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


class UserConfig(DictModel):
    """Abstract data type defining a Raindrop user's configuration."""

    broken_level = ItemAttr(BrokenLevel)
    font_color = ItemAttr[Optional[FontColor]](FontColor, default=None)
    font_size = ItemAttr[int]()
    last_collection = ItemAttr[int]()
    raindrops_view = ItemAttr(View)


class Group(DictModel):
    """Abstract data type defining a Raindrop user group."""

    title = ItemAttr[str]()
    hidden = ItemAttr[bool]()
    sort = ItemAttr[int]()
    collectionids = SequenceAttr[int](name="collections")


class UserFiles(DictModel):
    """Abstract data type defining a file associated with a user (?)."""

    used = ItemAttr[int]()
    size = ItemAttr[int]()
    lastCheckPoint = ItemAttr(dateparse)


class User(DictModel):
    """User."""

    id = ItemAttr[int](name="_id")
    config = ItemAttr(UserConfig)
    email = ItemAttr[str]()
    email_MD5 = ItemAttr[str]()
    files = ItemAttr(UserFiles)
    fullName = ItemAttr[str]()
    groups = SequenceAttr(Group)
    password = ItemAttr[bool]()
    pro = ItemAttr[bool]()
    registered = ItemAttr(dateparse)

    @classmethod
    def get(cls, api: API) -> User:
        """Get all the information about a specific Raindrop user."""
        user = api.get(URL.format(path="user")).json()["user"]
        return cls(user)


class SystemCollection(DictModel):
    """Represents a Raindrop System Collection, eg. Unsorted, Trash etc."""

    id = ItemAttr[int](name="_id")
    count = ItemAttr[int]()
    title = ItemAttr[str]()

    # The Raindrop API doesn't give us the names/titles of the
    # "system" collections, let's provide them here.
    CollectionRefsTitles = {
        CollectionRef.All.id: "All",
        CollectionRef.Trash.id: "Trash",
        CollectionRef.Unsorted.id: "Unsorted",
    }

    @classmethod
    def get_status(cls, api: API) -> User:
        """Get the title and counts of Raindrops across all 3 "system" collections."""

        def _add_title(item: dict) -> dict:
            """Add the title (since we don't get from the API)."""
            item["title"] = cls.CollectionRefsTitles[item["_id"]]
            return item

        items = api.get(URL.format(path="user/stats")).json()["items"]
        return [cls(_add_title(item)) for item in items]


class RaindropType(enum.Enum):
    """Map the types of Raindrop bookmarks possible (ie. what type of content they hold)."""

    link = "link"
    article = "article"
    image = "image"
    video = "video"
    document = "document"
    audio = "audio"


class Raindrop(DictModel):
    """Core class of a Raindrop bookmark 'item'."""

    id = ItemAttr[int](name="_id")
    collection = ItemAttr(CollectionRef)
    cover = ItemAttr[str]()
    created = ItemAttr(dateparse)
    domain = ItemAttr[str]()
    excerpt = ItemAttr[str]()  # aka "Description" on the Raindrop UI.
    lastUpdate = ItemAttr(dateparse)
    link = ItemAttr[str]()
    media = ItemAttr[Sequence[dict[str, Any]]]()
    tags = ItemAttr[Sequence[str]]()
    title = ItemAttr[str]()
    type = ItemAttr(RaindropType)
    user = ItemAttr(UserRef)

    #    broken: bool
    #    cache: Cache
    #    creatorRef: UserRef
    #    file: File
    #    important: bool
    #    html: str

    @classmethod
    def get(cls, api: API, id: int) -> Raindrop:
        """Primary call to return a Raindrop bookmark based on it's id."""
        item = api.get(URL.format(path=f"{id}")).json()["item"]
        return cls(item)

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
            if isinstance(collection, (Collection, CollectionRef)):
                args["collection"] = {"$id": collection.id}
            else:
                args["collection"] = {"$id": collection}

        url = URL.format(path="raindrop")
        item = api.post(url, json=args).json()["item"]
        return cls(item)

    @classmethod
    def create_file(
        cls,
        api: API,
        path: Path,
        content_type: str,
        collection: CollectionRef = CollectionRef.Unsorted,
        tags: Optional[Sequence[str]] = None,
        title: Optional[str] = None,
    ) -> Raindrop:
        """Create a new file-based Raindrop bookmark."""
        url = URL.format(path="raindrop/file")

        # Structure here confirmed through communication with RustemM
        # on 2022-11-29 and his subsequent update to API docs.
        data = {"collectionId": str(collection.id)}
        files = {"file": (path.name, open(path, "rb"), content_type)}
        results = api.put_file(url, path, data, files).json()["item"]
        raindrop = cls(results)

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
            return cls(item)
        else:
            return raindrop

    @classmethod
    def update(
        cls,
        api: API,
        id: int,
        pleaseParse: Optional[bool] = False,
        created: Optional[datetime.datetime] = None,
        lastUpdate: Optional[datetime.datetime] = None,
        order: Optional[int] = None,
        important: Optional[bool] = None,
        tags: Optional[Sequence[str]] = None,
        media: Optional[Sequence[dict[str, Any]]] = None,
        cover: Optional[str] = None,
        collection: Optional[Collection | CollectionRef, int] = None,
        type: Optional[str] = None,
        html: Optional[str] = None,
        excerpt: Optional[str] = None,
        title: Optional[str] = None,
        link: Optional[str] = None,
    ) -> Raindrop:
        """Update an existing Raindrop bookmark with any of the attribute values provided."""
        # Setup args to be sent to Raindrop..
        args: dict[str, Any] = {}
        if pleaseParse:
            args["pleaseParse"] = {}
        for attr in [
            "created",
            "lastUpdate",
            "order",
            "important",
            "tags",
            "media",
            "cover",
            "html",
            "excerpt",
            "title",
            "type",
        ]:
            if (value := locals().get(attr)) is not None:
                args[attr] = value
        if collection is not None:
            if isinstance(collection, (Collection, CollectionRef)):
                args["collection"] = collection.id
            else:
                args["collection"] = collection

        url = URL.format(path=f"raindrop/{id}")
        item = api.put(url, json=args).json()["item"]
        return cls(item)

    @classmethod
    def remove(cls, api: API, id: int) -> None:
        """Remove/delete a Raindrop bookmark."""
        api.delete(URL.format(path=f"raindrop/{id}"), json={})

    @classmethod
    def search(
        cls,
        api: API,
        collection: CollectionRef = CollectionRef.All,
        page: int = 0,
        perpage: int = 50,
        word: Optional[str] = None,
        tag: Optional[str] = None,
        important: Optional[bool] = None,
    ) -> list[Raindrop]:
        """Search for bookmarks in the specified collection with key word, tag or importance parms."""
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
        return [cls(item) for item in results["items"]]


class Tag(DictModel):
    """Represents existing Tags, either all or just a specific collection."""

    tag = ItemAttr[str](name="_id")
    count = ItemAttr[int]()

    @classmethod
    def get(cls, api: API, collection_id: int = None) -> list[Tag]:
        """Get all the tags currently defined, either in a specific collections or across all collections."""
        url = URL.format(path="tags")
        if collection_id:
            url += "/" + str(collection_id)
        items = api.get(url).json()["items"]
        return [cls(item) for item in items]

    @classmethod
    def remove(cls, api: API, tags: Sequence[str]) -> None:
        """Remove/delete one or more tags."""
        api.delete(URL.format(path="tags"), json={})
