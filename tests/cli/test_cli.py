"""Test our CLI prompt environment on a read-only basis (ie. no actual create or search)."""
import pexpect
import pytest


@pytest.fixture
def child():
    """Return pexpect library against our executable in testing mode."""
    with open("/tmp/test_pexpect.log", "w") as fh_pexpect:
        child = pexpect.spawn(
            "python raindropiopy/cli/cli.py --testing",
            encoding="utf-8",
            logfile=fh_pexpect,
        )
        yield child
    child.terminate()


def _sl(child, text):
    """Wrap pexpect sendline that also logs to console."""
    child.sendline(text)
    print(f"sendline  : {text}", flush=True)


def _ee(child, text):
    """Wrap pexpect expect that also logs to console."""
    print(f"expecting : {text}...", flush=True, end="")
    child.expect_exact(text)
    print("✔")


def test_cli_root(child):
    """Test top-level prompt."""
    _ee(child, "(s)earch, (c)reate, (m)anage, (e)xit")
    _ee(child, ">")


def test_cli_manage(child):
    """Test manage tree."""
    _sl(child, "manage")
    _ee(child, "(s)tatus, (c)ollections, (t)ags, (r)efresh,")
    _ee(child, "manage>")

    _sl(child, "status")
    _ee(child, "Active User")
    _ee(child, "Raindrops")
    _ee(child, "Collections")
    _ee(child, "As Of")

    _sl(child, "collections")
    _ee(child, "manage>")

    _sl(child, "tags")
    _ee(child, "manage>")

    _sl(child, ".")
    _ee(child, "(s)earch, (c)reate, (m)anage, (e)xit")
    _ee(child, ">")


def test_cli_create(child):
    """Test create tree."""
    _sl(child, "create")
    _ee(child, "create>")

    _sl(child, "url")
    _ee(child, "url?")

    _sl(child, "https://www.python.org")
    _ee(child, "title?")

    _sl(child, "aTitle")
    _ee(child, "description?")

    _sl(child, "aDescription")
    _ee(child, "collection?")

    _sl(child, "")
    _ee(child, "tag(s)")

    _sl(child, "")
    _ee(child, "Is this correct?")

    _sl(child, "no")
    _ee(child, "create>")

    _sl(child, "b")
    _ee(child, "bulk upload file?>")

    _sl(child, ".")
    _ee(child, "create>")

    _sl(child, ".")
    _ee(child, "(s)earch, (c)reate, (m)anage, (e)xit")
    _ee(child, ">")


def test_cli_search(child):
    """Test search tree."""
    _sl(child, "search")
    _ee(child, "search term(s)?>")

    _sl(child, "Sample")
    _ee(child, "collection(s)?>")

    _sl(child, ".")
    _ee(child, "(s)earch, (c)reate, (m)anage, (e)xit")
    _ee(child, ">")
