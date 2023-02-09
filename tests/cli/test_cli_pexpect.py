"""Starting point to test our CLI interactions (on a pre-recorded basis!)."""
import pexpect


def sl(child, text):
    """Send a line of test AND log action."""
    child.sendline(text)
    print(f"sendline  : {text}", flush=True)


def ee(child, text):
    """Expect some text AND log it."""
    print(f"expecting : {text}...", flush=True, end="")
    child.expect_exact(text)
    print("✔")


def test_cli_traversal():
    """Test ability to traverse the entire menu tree successfully."""
    with open("/tmp/test_pexpect.out", "w") as fh_out:
        child = pexpect.spawn(
            "python raindropiopy/cli/cli.py --testing",
            encoding="utf-8",
        )
        child.logfile = fh_out

        # Confirm top-level prompt
        ee(child, "(s)earch, (c)reate, (m)anage, (e)xit")
        ee(child, ">")

        ################################################################################
        # Manage
        ################################################################################
        sl(child, "manage")
        ee(child, "(s)tatus, (c)ollections, (t)ags, (r)efresh,")
        ee(child, "manage>")

        sl(child, "status")
        ee(child, "Active User")
        ee(child, "Raindrops")
        ee(child, "Collections")
        ee(child, "As Of")

        sl(child, "collections")
        ee(child, "manage>")

        sl(child, "tags")
        ee(child, "manage>")

        sl(child, ".")
        ee(child, "(s)earch, (c)reate, (m)anage, (e)xit")
        ee(child, ">")

        ################################################################################
        # Create
        ################################################################################
        sl(child, "create")
        ee(child, "create>")

        sl(child, "url")
        ee(child, "url?")

        sl(child, "https://www.python.org")
        ee(child, "title?")

        sl(child, "aTitle")
        ee(child, "description?")

        sl(child, "aDescription")
        ee(child, "collection?")

        sl(child, "")
        ee(child, "tag(s)")

        sl(child, "")
        ee(child, "Is this correct?")

        sl(child, "no")
        ee(child, "create>")

        sl(child, "b")
        ee(child, "bulk upload file?>")

        sl(child, ".")
        ee(child, "create>")

        sl(child, ".")
        ee(child, "(s)earch, (c)reate, (m)anage, (e)xit")
        ee(child, ">")

        ################################################################################
        # Search
        ################################################################################
        sl(child, "search")
        ee(child, "search term(s)?>")

        sl(child, "Sample")
        ee(child, "collection(s)?>")

        sl(child, ".")
        ee(child, "(s)earch, (c)reate, (m)anage, (e)xit")
        ee(child, ">")

        child.terminate()
