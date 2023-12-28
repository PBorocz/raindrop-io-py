"""All data classes to interact with Raindrops API.

Raindrop.IO has a small set of core data entities (e.g. Raindrops aka bookmarks, Collections, Tags etc.). We
deliver the services provided by Raindrop.IO as a set of class-based methods on these various data entities.

For example, to create a new raindrop, use Raindrop.create_link(...); a collection would be Collection.create(...) etc.

"""
from __future__ import annotations

import enum
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    HttpUrl,
    NonNegativeInt,
    PositiveInt,
    root_validator,
    validator,
)

from .api import T_API  # ie. for typing only...

__all__ = [
    "Access",
    "AccessLevel",
    "BrokenLevel",
    "Collection",
    "CollectionRef",
    "FontColor",
    "Group",
    "Raindrop",
    "RaindropSort",
    "RaindropType",
    "Tag",
    "User",
    "UserFiles",
    "UserRef",
    "View",
]

# Base URL for Raindrop IO's API
URL = "https://api.raindrop.io/rest/v1/{path}"


################################################################################
# Utility methods
################################################################################
def _collect_other_attributes(cls, v):
    """Gather all non-recognised/unofficial non-empty attribute values into a single one."""
    skip_attrs = "_id"  # We don't need to store alias attributes again (pydantic will take care of)
    v["other"] = dict()
    for attr, value in v.items():
        if value and attr not in cls.__fields__ and attr not in skip_attrs:
            v["other"][attr] = value
    return v


def _resolve_parent_reference(parent_reference: dict | int | None) -> int | None:
    """Convert a Raindrop.IO parent reference dict to just the respective ID of the parent collection.

    For a child collection that has a parent, the reference to the parent received from Raindrop.IO is:

    {"$id": 12345678, "$ref": 'collections'}.

    We don't need the $ref part (at least I don't believe so), so simply pull the $id key.
    """
    if parent_reference is None:
        return None
    elif isinstance(parent_reference, int):
        return parent_reference
    return parent_reference.get("$id")


################################################################################
# Enumerated types
################################################################################
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


class RaindropSort(enum.Enum):
    """Enumerate Raindrop sort options available."""

    created_up = "created"
    created_dn = "-created"
    title_up = "title"
    title_dn = "-title"
    domain_up = "domain"
    domain_dn = "-domain"
    last_update_up = "+lastUpdate"
    last_update_dn = "-lastUpdate"


class RaindropType(enum.Enum):
    """Map the types of Raindrop bookmarks possible (ie. what type of content they hold)."""

    link = "link"
    article = "article"
    image = "image"
    video = "video"
    document = "document"
    audio = "audio"


################################################################################
# Base Models
################################################################################
class CollectionRef(BaseModel):
    """Represents a **reference** to a Raindrop Collection (essentially a TypeVar of id: int).

    Note: We also instantiate three particular ``CollectionRefs`` associated with **System** Collections:
        *All*, *Trash* and *Unsorted*.

        System Collections always exist and can be explicitly used to query anywhere you'd use a Collection ID.

    """

    id: int = Field(None, alias="$id")


# We define the 3 "system" collections in the Raindrop environment:
CollectionRef.All = CollectionRef(
    **{"$id": 0},
)  # Note: "all" here does NOT include Trash.
CollectionRef.Trash = CollectionRef(**{"$id": -99})
CollectionRef.Unsorted = CollectionRef(**{"$id": -1})


class UserRef(BaseModel):
    """Represents a **reference** to `User` object."""

    id: int = Field(None, alias="$id")
    ref: str = Field(None, alias="$user")


class Access(BaseModel):
    """Represents Access control level of a `Collection`."""

    level: AccessLevel
    draggable: bool


class Collection(BaseModel):
    """Represents a Raindrop `Collection`, ie. a group of Raindrop Bookmarks.

    Attributes:
        id: The id of the collection (required)
        title: The name of the collection.
        user: The user who created the collection.
        access: Describes current Access levels to the collection (eg. ReadOnly, OwnerOnly etc.).
        collaborators: Populated with list of collaborating users iff collection is shared.
        color: Primary color of the collection cover.
        count: Count of Raindrops in the collection.
        cover: URL of the collection's cover.
        created: When the collection was created.
        expanded: Whether the collection's sub-collection are expanded (on the interface)
        last_update: When the collection was last updated.
        parent: Parent ID of this is a sub-collection.
        public: Are contents of this collection available to non-authenticated users?
        sort: The order of the collection. Defines the position of the collection against
          all other collections at the same level in the tree (only used for sub-collections?)
        view: Current view style of the collection, e.g. list, simple, grid etc.
        other: All other attributes received from Raindrop's API (see Warning below)

    Warning:
        Attributes in `other` are *NOT* OFFICIALLY SUPPORTED...use at your own risk!
    """

    id: int = Field(None, alias="_id")
    title: str
    user: UserRef

    access: Access | None
    collaborators: list[Any] | None = Field(default_factory=list)
    color: str | None = None
    count: NonNegativeInt
    cover: list[str] | None = Field(default_factory=list)
    created: datetime | None
    expanded: bool = False
    last_update: datetime | None
    parent: int | None  # Id of parent collection (if any)
    public: bool | None
    sort: int | None
    view: View | None

    # Per API Doc: "Our API response could contain other fields, not described above.
    # It's unsafe to use them in your integration! They could be removed or renamed at any time."
    other: dict[str, Any] = {}

    # Used to convert parent reference's of sub-collections to simply id's of the respective parent collection.
    _extract_parent_id = validator("parent", pre=True, allow_reuse=True)(
        _resolve_parent_reference,
    )

    @root_validator(pre=True)
    # FIXME: noqa here is because work-around in https://github.com/pydantic/pydantic/issues/568 doesn't work!
    def _validator(cls, v):  # noqa: N805
        """Gather all non-recognised/unofficial attributes into a single attribute."""
        return _collect_other_attributes(cls, v)

    @classmethod
    def get_root_collections(cls, api: T_API) -> list[Collection]:
        """Get **root** Raindrop collections.

        Args:
            api: API Handle to use for the request.

        Returns:
            The (potentially empty) list of non-system, **top-level** Collections associated with the API's user.

        Note:
            Since Raindrop allows for collections to be nested, the RaindropIO's API distinguishes between Collections
            at the top-level/root of a collection hierarchy versus those all that are below the top level, aka 'child'
            or 'sub' collections. Thus, use ``get_root_collections`` to get all Collections without parents and
            ``get_child_collections`` for all Collections with parents.
        """
        ret = api.get(URL.format(path="collections"))
        items = ret.json()["items"]
        return [cls(**item) for item in items]

    @classmethod
    def get_child_collections(cls, api: T_API) -> list[Collection]:
        """Get the **child** Raindrop collections (ie. all below root level).

        Args:
            api: API Handle to use for the request.

        Returns:
            The (potentially empty) list of non-system, **non-top-level** Collections associated with the API's user.

        Note:
            Since Raindrop allows for collections to be nested, the RaindropIO's API distinguishes between Collections
            at the top-level/root of a collection hierarchy versus those all that are below the top level, aka 'child'
            collections. Thus, use ``get_root_collections`` to get all Collections without parents and
            ``get_child_collections`` for all Collections with parents.
        """
        ret = api.get(URL.format(path="collections/childrens"))
        items = ret.json()["items"]
        return [cls(**item) for item in items]

    @classmethod
    def get_collections(cls, api: T_API) -> list[Collection]:
        """Query for all non-system collections (essentially a convenience wrapper, combining root & child Collections).

        Args:
            api: API Handle to use for the request.

        Returns:
            The (potentially empty) list of all **non-system** Collections associated with the API's user,
            ie. hiding the distinction between root/child collections.
        """
        return cls.get_root_collections(api) + cls.get_child_collections(api)

    @classmethod
    def get(cls, api: T_API, id: int) -> Collection:
        """Return a Raindrop Collection instance based on it's id.

        Args:
            api: API Handle to use for the request.

            id: Id of Collection to query for.

        Returns:
            ``Collection`` instance associated with the id provided.

        Raises:
            HTTPError: If the id provided could not be found (specifically 404)
        """
        url = URL.format(path=f"collection/{id}")
        item = api.get(url).json()["item"]
        return cls(**item)

    @classmethod
    def create(
        cls,
        api: T_API,
        title: str,
        cover: list[str] | None = None,
        expanded: bool | None = None,
        parent: int | None = None,
        public: bool | None = None,
        sort: int | None = None,
        view: View | None = None,
    ) -> Collection:
        """Create a new Raindrop collection.

        Args:
            api: Required: API Handle to use for the request.

            cover: Optional, URL of collection's cover (as a list but only the first entry is used).

            expanded: Optional, flag for whether or not any of the collection's sub-collections are expanded.

            parent: Optional, Id of the collection's **parent** you want to create nested collections.

            public: Optional, flag for whether or not the collection should be publically available.

            sort: Optional, sort order for Raindrops created in this collection.

            title: Required: Title of the collection to be created.

            view: Optional, View associated with the default view to display Raindrops in this collection.

        Returns:
            ``Collection`` instance created.
        """
        args: dict[str, Any] = {}
        if cover is not None:
            args["cover"] = cover
        if expanded is not None:
            args["expanded"] = cover
        if parent is not None:
            args["parent"] = parent
        if public is not None:
            args["public"] = public
        if sort is not None:
            args["sort"] = sort
        if title is not None:
            args["title"] = title
        if view is not None:
            args["view"] = view

        url = URL.format(path="collection")
        item = api.post(url, json=args).json()["item"]
        return cls(**item)

    @classmethod
    def update(
        cls,
        api: T_API,
        id: int,
        cover: list[str] | None = None,
        expanded: bool | None = None,
        parent: int | None = None,
        public: bool | None = None,
        sort: int | None = None,
        title: str | None = None,
        view: View | None = None,
    ) -> Collection:
        """Update an existing Raindrop collection with any of the attribute values provided.

        Args:
            api: API Handle to use for the request.

            id: Required, Id of Collection to be updated.

            cover: URL of collection's cover (as a list but only the first entry is used).

            expanded: Flag for whether or not any of the collection's sub-collections are expanded.

            parent: Id of the collection's **parent** to set the current collection to.

            public: Flag for whether or not the collection should be publically available.

            sort: Sort order for Raindrops created in this collection.

            title: New collection title.

            view: View enum associated with the default view to display Raindrops in this collection.

        Returns:
            Updated ``Collection`` instance.
        """
        args: dict[str, Any] = {}
        for attr in ["expanded", "view", "title", "sort", "public", "parent", "cover"]:
            if (value := locals().get(attr)) is not None:
                args[attr] = value
        url = URL.format(path=f"collection/{id}")
        item = api.put(url, json=args).json()["item"]
        return cls(**item)

    @classmethod
    def delete(cls, api: T_API, id: int) -> None:
        """Delete a Raindrop collection.

        Args:
            api: API Handle to use for the request.

            id: Id of Collection to be deleted.

        Returns:
            None.
        """
        api.delete(URL.format(path=f"collection/{id}"), json={})

    @classmethod
    def get_or_create(cls, api: T_API, title: str) -> Collection:
        """Get a Raindrop collection based on it's **title**, if it doesn't exist, create it.

        Args:
            api: API Handle to use for the request.

            title: Title of the collection.

        Returns:
            Collection with the specified collection title if it already exists or newly created
              collection if it doesn't.
        """
        for collection in Collection.get_root_collections(api):
            if title.casefold() == collection.title.casefold():
                return collection

        # Doesn't exist, create it!
        return Collection.create(api, title=title)


class Group(BaseModel):
    """Sub-model defining a Raindrop user group."""

    title: str
    hidden: bool
    sort: NonNegativeInt
    collectionids: list[int] = Field(None, alias="collections")


class UserConfig(BaseModel):
    """Sub-model defining a Raindrop user's configuration.

    Warning:
        Attributes in `other` are NOT OFFICIALLY SUPPORTED!.
    """

    broken_level: BrokenLevel = None
    font_color: FontColor | None = None
    font_size: int | None = None
    lang: str | None = None
    last_collection: CollectionRef | None = None
    raindrops_sort: RaindropSort | None = None
    raindrops_view: View | None = None

    # Per API Doc: "Our API response could contain other fields, not described above.
    # It's unsafe to use them in your integration! They could be removed or renamed at any time."
    other: dict[str, Any] = {}

    @validator("last_collection", pre=True)
    def cast_last_collection_to_ref(cls, v):  # noqa: N805
        """Cast last_collection provided as a raw int to a valid CollectionRef."""
        return CollectionRef(**{"$id": v})

    @root_validator(pre=True)
    def _validator_other_attributes(cls, v):  # noqa: N805
        """Gather all non-recognised/unofficial attributes into a single attribute."""
        return _collect_other_attributes(cls, v)


class UserFiles(BaseModel):
    """Sub-model defining a file associated with a user (?)."""

    used: int
    size: PositiveInt
    last_checkpoint: datetime = Field(None, alias="lastCheckpoint")


class User(BaseModel):
    """Raindrop User model."""

    id: int = Field(None, alias="_id")
    email: EmailStr
    email_md5: str | None = Field(None, alias="email_MD5")
    files: UserFiles
    full_name: str = Field(None, alias="fullName")
    groups: list[Group]
    password: bool
    pro: bool
    pro_expire: datetime | None = Field(None, alias="proExpire")
    registered: datetime
    config: UserConfig

    @classmethod
    def get(cls, api: T_API) -> User:
        """Get all the information about the Raindrop user associated with the API token."""
        user = api.get(URL.format(path="user")).json()["user"]
        return cls(**user)


class SystemCollection(BaseModel):
    """Raindrop **System** collection model, ie. collections for *Unsorted*, *Trash* and *All*.

    Note:
        - The *All* collection contains **all** currently active (ie. non-Trash) Raindrops held by the User.

        - The *Unsorted* collection contains Raindrops created that are **not** held within any other collection.

        - The *Trash* collection contains Raindrops that have been recently deleted.

    You won't use this class directly on behalf of individual Raindrops, rather, its definition is on behalf of
    a small set of simple "status" calls available from the Raindrop.io API, specifically `get_counts` and `get_meta`.
    """

    id: int = Field(None, alias="_id")
    count: NonNegativeInt
    title: str | None

    @root_validator(pre=False)
    def _validator(cls, values):  # noqa: N805
        """Map the hard-coded id's of the System Collections to the descriptions used on the UI."""
        _titles = {
            CollectionRef.Unsorted.id: "Unsorted",
            CollectionRef.All.id: "All",
            CollectionRef.Trash.id: "Trash",
        }
        values["title"] = _titles.get(values["id"])
        return values

    @classmethod
    def get_counts(cls, api: T_API) -> list[Collection]:
        """Get the count of Raindrops in each of the 3 *system* collections."""
        items = api.get(URL.format(path="user/stats")).json()["items"]
        return [cls(**item) for item in items]

    @classmethod
    def get_meta(cls, api: T_API) -> dict:
        """Get the 'meta' slug from the root/system Collection.

        Contains information about:

        - Last date/time any bookmark was changed.

        - The number of broken links in bookmarks.

        - If your account is a "pro" level.
        """
        return api.get(URL.format(path="user/stats")).json()["meta"]


class File(BaseModel):
    """Represents the attributes associated with a file within a document-based Raindrop."""

    name: str
    size: PositiveInt
    type: str


class Cache(BaseModel):
    """Represents the cache information of Raindrop."""

    # Per issue #5, we can't rely on Raindrop to always return a non-zero value for `size`, thus
    # instead of `PositiveInt`, we use `int`.
    status: CacheStatus
    size: int | None = None
    created: datetime | None = None


class Raindrop(BaseModel):
    """Core class of a Raindrop bookmark 'item'.

    A Raindrop/bookmark can be of two major types:

    - A **link-based** one, ie. a standard "bookmark" that points to a specific URL (in the link attribute).

    - A **file-based** one, into which a file (of the approved type) is uploaded and stored on the
      Raindrop service (details of which are in the file attribute).

    Attributes:
        id: The id of the Raindrop.
        collection: Collection (or CollectionRef) this Raindrop currently resides in.
        cover: The URL of the Raindrop's cover.
        created: The creation datetime of the Raindrop.
        domain: Hostname of a link, ie. if a Raindrop has link: `https://www.google.com?search=SomeThing`,
          domain is `www.google.com`.
        excerpt: Description associated with this Raindrop (maximum length: 10k!)
        last_update: When this Raindrop was last updated.
        link: For a link-based Raindrop, the full URL.
        media: Covers list.
        tags: A list of Tags associated with the Raindrop.
        title: The title of the Raindrop (maximum length: 1k).
        type: The type of the Raindrop, e.g. *link*, *document* (I haven't tested other types)
        user: The user who created the Raindrop.
        broken: True of the link associated with the Raindrop is not reachable anymore.
        cache: Details of the permanent cache associated with the Raindrop.
        file: Details of the file associated with a **file** based Raindrop.
        important: True if this Raindrop is marked as a **Favorite**.
        other: All other attributes received from Raindrop's API.

    Warning:
        Attributes in `other` are NOT OFFICIALLY SUPPORTED!.
    """

    # "Main" fields (per https://developer.raindrop.io/v1/raindrops)
    id: int = Field(None, alias="_id")
    collection: Collection | CollectionRef = CollectionRef.Unsorted
    cover: str | None
    created: datetime | None
    domain: str | None
    excerpt: str | None  # aka 'Description' on the Raindrop UI.
    last_update: datetime | None = Field(None, alias="lastUpdate")
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

    # Per API Doc: "Our API response could contain other fields, not described above.
    # It's unsafe to use them in your integration! They could be removed or renamed at any time."
    other: dict[str, Any] = {}

    @root_validator(pre=True)
    def _validator(cls, v):  # noqa: N805
        """Gather all non-recognised/unofficial attributes into a single attribute."""
        return _collect_other_attributes(cls, v)

    @classmethod
    def get(cls, api: T_API, id: int) -> Raindrop:
        """Return a Raindrop bookmark based on it's id."""
        item = api.get(URL.format(path=f"{id}")).json()["item"]
        return cls(**item)

    @classmethod
    def create_link(
        cls,
        api: T_API,
        link: str,
        collection: (Collection | CollectionRef, int) | None = None,
        cover: str | None = None,
        excerpt: str | None = None,
        important: bool | None = None,
        media: list[dict[str, Any]] | None = None,
        order: int | None = None,
        please_parse: bool = False,  # If set, asks API to automatically parse metadata in the background
        tags: list[str] | None = None,
        title: str | None = None,
    ) -> Raindrop:
        """Create a new link-type Raindrop bookmark.

        Args:
            api: API Handle to use for the request.

            link: Required, URL to associate with this Raindrop.

            collection: Optional, Collection (or CollectionRef) to place this Raindrop "into".
              If not specified, new Raindrop will be in system Collection "Unsorted".

            cover: Optional, URL of the Raindrop's "cover".

            excerpt: Optional, long description for the Raindrop (internally, Raindrop call's
              it an *excerpt* but on the UI it's *Description*). Maximum length is 10k characters.

            important: Optional, Flag to indicate if this Raindrop should be considered important nee a favorite.

            media: Optional, List of media dictionaries (consult RaindropIO's API for somewhat more information.

            order: Optional, Order of Raindrop in respective collection, ie. set to 0 to make Raindrop first.

            please_parse: Optional, Flag that asks API to automatically parse metadata in the background
              (not exactly sure which this implies, message me if you know! ;-)

            tags: Optional, List of tags to associated with this Raindrop.

            title: Optional, Title to associated with this Raindrop.

        Returns:
            ``Raindrop`` instance created.

        Note:
            We don't allow you to set either ``created`` or ``last_update`` attributes. They will be
            set appropriately by the RaindropIO service on your behalf.
        """
        # Setup the args that will be passed to the underlying Raindrop API, only link is
        # absolutely required, rest are optional!
        args: dict[str, Any] = dict(type=RaindropType.link, link=link)

        if please_parse:
            args["please_parse"] = {}

        for attr in [
            "cover",
            "excerpt",
            "important",
            "media",
            "order",
            "tags",
            "title",
        ]:
            if (value := locals().get(attr)) is not None:
                args[attr] = value

        if collection is not None:
            # <collection> arg could be **either** an actual collection
            # or simply an int collection "id" already, handle either:
            if isinstance(collection, Collection | CollectionRef):
                args["collection"] = {"$id": collection.id}
            else:
                args["collection"] = {"$id": collection}
        url = URL.format(path="raindrop")
        item = api.post(url, json=args).json()["item"]
        return cls(**item)

    @classmethod
    def create_file(
        cls,
        api: T_API,
        path: Path,
        content_type: str,
        collection: (Collection | CollectionRef, int) | None = CollectionRef.Unsorted,
        tags: list[str] | None = None,
        title: str | None = None,
    ) -> Raindrop:
        """Create a new file-based Raindrop bookmark.

        Args:
            api: API Handle to use for the request.

            path: Required, python Path to file to be uploaded.

            content_type: Required, mime-type associated with the file.

            collection: Optional, Collection (or CollectionRef) to place this Raindrop "into".
              If not specified, new Raindrop will be in system Collection *Unsorted*.

            tags: Optional, List of tags to associated with this Raindrop.

            title: Optional, Title to associated with this Raindrop.

        Returns:
            ``Raindrop`` instance created.

        Note:
            Only a limited number of file-types are supported by RaindropIO (minimally, "application/pdf"),
            specifically (as of 2023-02):

            - Images (jpeg, gif, png, webp, heic)

            - Videos (mp4, mov, wmv, webm)

            - Books (epub)

            - Documents (pdf, md, txt)
        """
        # Uses a different URL for file uploading..
        url = URL.format(path="raindrop/file")

        # NOTE: "put_file" arguments and structure here confirmed through communication
        #       with RustemM on 2022-11-29 and his subsequent update to API docs.
        if isinstance(collection, Collection | CollectionRef):
            data = {"collectionId": str(collection.id)}
        else:
            data = {"collectionId": str(collection)}

        with open(path, "rb") as fh_:
            files = {"file": (path.name, fh_, content_type)}
            item = api.put_file(url, path, data, files).json()["item"]
            raindrop = cls(**item)

        # Raindrop's "Create Raindrop From File" does not allow us to set other attributes,
        # thus, we need to check if any of the possible attributes need to be set and do so
        # explicitly with another call to "update" the Raindrop we just created.
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
        api: T_API,
        id: int,
        collection: (Collection | CollectionRef, int) | None = None,
        cover: str | None = None,
        excerpt: str | None = None,
        important: bool | None = None,
        link: str | None = None,
        media: list[dict[str, Any]] | None = None,
        order: int | None = None,
        please_parse: bool | None = False,
        tags: list[str] | None = None,
        title: str | None = None,
    ) -> Raindrop:
        """Update an existing Raindrop bookmark, setting any of the attribute values provided.

        Args:
            api: API Handle to use for the request.

            id: Required id of Raindrop to be updated.

            collection: Optional, Collection (or CollectionRef) to move this Raindrop "into". If not specified,
                Raindrop will remain in the same collection as it was.

            cover: Optional, new URL to set as the Raindrop's "cover".

            excerpt: Optional, new long description for the Raindrop. Maximum length is 10,000 characters.

            important: Optional, Flag to indicate if this Raindrop should be considered important nee a favorite.

            link: Required, New URL to associate with this Raindrop.

            media: Optional, Updated list of media dictionaries (consult RaindropIO's API for somewhat more information.

            order: Optional, Change order of Raindrop in respective collection.

            please_parse: Optional, Flag that asks API to automatically parse metadata in the background
                (not exactly sure which this implies, message me if you know! ;-)

            tags: Optional, New list of tags to associate with this Raindrop.

            title: Optional, New title for this Raindrop.

        Returns:
            ``Raindrop`` instance that was updated.
        """
        # Setup the args that will be passed to the underlying Raindrop API
        args: dict[str, Any] = {}

        if please_parse:
            args["please_parse"] = {}

        for attr in [
            "cover",
            "excerpt",
            "important",
            "link",
            "media",
            "order",
            "tags",
            "title",
        ]:
            if (value := locals().get(attr)) is not None:
                args[attr] = value

        if collection is not None:
            # <collection> arg could be **either** an actual collection
            # or simply an int collection "id" already, handle either:
            if isinstance(collection, Collection | CollectionRef):
                args["collection"] = collection.id
            else:
                args["collection"] = collection

        url = URL.format(path=f"raindrop/{id}")
        item = api.put(url, json=args).json()["item"]
        return cls(**item)

    @classmethod
    def delete(cls, api: T_API, id: int) -> None:
        """Delete a Raindrop bookmark.

        Args:
            api: API Handle to use for the request.

            id: Required id of Raindrop to be deleted.

        Returns:
            None.
        """
        api.delete(URL.format(path=f"raindrop/{id}"), json={})

    @classmethod
    def _search_paged(
        cls,
        api: T_API,
        collection: CollectionRef = CollectionRef.All,
        search: str | None = None,
        page: int = 0,
        perpage: int = 50,
    ) -> list[Raindrop]:
        """Lower-level search for bookmarks on a "paged" basis.

        Raindrop's search API works on a "paged" basis. This method implements the underlying
        search reflecting paging (while the primary ``search`` method below hides it
        completely).
        """
        params = {"perpage": perpage, "page": page}
        if search:
            params["search"] = search
        url = URL.format(path=f"raindrops/{collection.id}")
        results = api.get(url, params=params).json()
        return [cls(**item) for item in results["items"]]

    @classmethod
    def search(
        cls,
        api: T_API,
        collection: Collection | CollectionRef = CollectionRef.All,
        search: str | None = None,
    ) -> list[Raindrop]:
        """Search for Raindrops.

        Args:
            api: API Handle to use for the request.

            collection: Optional, ``Collection`` (or ``CollectionRef``) to search over.
                Defaults to ``CollectionRef.All``.

            search: Optional, search string to search Raindrops for (see
                `Raindrop.io Search Help <https://help.raindrop.io/using-search#operators>`_ for more information.

        Returns:
            A (potentially empty) list of Raindrops that match the search criteria provided.
        """
        page = 0
        results = list()
        while raindrops := Raindrop._search_paged(
            api,
            collection,
            page=page,
            search=search,
        ):
            results.extend(raindrops)
            page += 1
        return results


class Tag(BaseModel):
    """Represents existing Tags, either all or just a specific collection."""

    tag: str = Field(None, alias="_id")
    count: int

    @classmethod
    def get(cls, api: T_API, collection_id: int | None = None) -> list[Tag]:
        """Get all the tags currently defined, either in a specific collections or across all collections.

        Args:
            api: API Handle to use for the request.

            collection_id: Optional, Id of specific collection to limit search for all tags.

        Returns:
            List of ``Tag``.
        """
        url = URL.format(path="tags")
        if collection_id:
            url += "/" + str(collection_id)
        items = api.get(url).json()["items"]
        return [Tag(**item) for item in items]

    @classmethod
    def delete(cls, api: T_API, tags: list[str]) -> None:
        """Delete one or more Tags.

        Args:
            api: API Handle to use for the request.

            tags: List of tags to be deleted.

        Returns:
            None.
        """
        api.delete(URL.format(path="tags"), json={})
