"""Top level cli.commands dunder init, mostly common methods and data types."""
from typing import Final, Optional

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich import print

from raindropiopy.cli import WARNING, PROMPT_STYLE, prompt
from raindropiopy.cli.models.eventLoop import EventLoop


def is_int(string: str) -> bool:
    """Make (compound) conditionals easier."""
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_from_list(
    el: EventLoop,
    prompt_s: tuple[str],
    options: tuple[str],
) -> Optional[str]:
    """Mini-event loop to prompt for one or more selected options from the list provided."""
    completer: Final = WordCompleter(options)
    while True:
        response = el.session.prompt(
            prompt(prompt_s),  # ("create", "url", f"{prompt}?"))
            completer=completer,
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )
        if response == "?":
            el.console.print(", ".join(options))
        else:
            break
    return response


def get_title(el: EventLoop, prompts: list[str]) -> str | None:
    """Mini-event loop to prompt for a raindrop Title."""
    while True:
        title = el.session.prompt(prompt(prompts), style=PROMPT_STYLE)
        if title == "?":
            el.console.print(
                "We need a Raindrop title here, eg. 'Home Page for xxxyyy'",
            )
        elif title == "q":
            return None
        else:
            return title


def get_description(el: EventLoop, prompts: list[str]) -> str | None:
    """Mini-event loop to prompt for a raindrop Description (nee excerpt)."""
    while True:
        description = el.session.prompt(prompt(prompts), style=PROMPT_STYLE)
        if description == "?":
            el.console.print(
                "We need a Raindrop description here, eg. 'This was an interesting site.'",
            )
        elif description == "q":
            return None
        else:
            return description


def get_collection_s(el: EventLoop, prompts: list[str]) -> str | None:
    """Mini event-loop to prompt for one or many raindrop collections."""
    while True:
        collection_s = get_from_list(
            el,
            ("search", "collection(s)?"),
            el.state.get_collection_titles(exclude_unsorted=False),
        )
        if collection_s == ".":
            return None

        if collection_s:
            unrecognised_collections = list()
            current_collections = el.state.get_collection_titles(
                exclude_unsorted=True,
                casefold=True,
            )
            for collection in collection_s.split():
                if collection.casefold() not in current_collections:
                    unrecognised_collections.append(collection)
            if unrecognised_collections:
                print(
                    f"[{WARNING}]Sorry, collection(s) are NOT currently available: ",
                    end="",
                )
                print(", ".join(unrecognised_collections))
                print(
                    f"[{WARNING}]We're expecting either <blank> or one of one of: "
                    + ", ".join(el.state.get_collection_titles(exclude_unsorted=True)),
                )
                continue

        return collection_s


def get_confirmation(
    el: EventLoop,
    prompt: str,
    prompt_style: Style = PROMPT_STYLE,
) -> bool:
    """Ask the user for a confirmation to perform the specific prompt supplied."""
    el_prompt: Final = [("class:prompt", f"\n{prompt} ")]
    options: Final = ("yes", "Yes", "No", "no")
    completer: Final = WordCompleter(options)
    response = el.session.prompt(
        el_prompt,
        completer=completer,
        style=prompt_style,
        complete_while_typing=True,
        enable_history_search=False,
    )
    if response == "q":
        return None
    else:
        if response.lower() in ["yes", "y", "ye"]:
            return True
        return False
