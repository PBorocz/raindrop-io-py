from typing import Final, Optional

from prompt_toolkit.completion import WordCompleter

from raindroppy.cli import PROMPT_STYLE, cli_prompt
from raindroppy.cli.cli import CLI


def get_from_list(cli: CLI, prompt_s: tuple[str], options: tuple[str]) -> Optional[str]:
    completer: Final = WordCompleter(options)
    while True:
        try:
            response = cli.session.prompt(
                cli_prompt(prompt_s),  # ("create", "url", f"{prompt}?"))
                completer=completer,
                style=PROMPT_STYLE,
                complete_while_typing=True,
                enable_history_search=False,
            )
            if response == "?":
                cli.console.print(", ".join(options))
            else:
                break
        except (KeyboardInterrupt, EOFError):
            return None

    return response
