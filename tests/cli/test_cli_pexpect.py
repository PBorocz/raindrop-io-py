"""Starting point to test our CLI interactions (on a pre-recorded basis!)."""
import pexpect


def sl(child, text):
    """Send a line of test AND log action."""
    child.sendline(text)
    print(f"sendline: {text}", flush=True)


def test_cli_traversal():
    """Test ability to traverse the entire menu tree successfully."""
    with open("/tmp/test_pexpect.out", "w") as fh_out:
        child = pexpect.spawn(
            "python raindropiopy/cli/cli.py --testing",
            encoding="utf-8",
        )
        child.logfile = fh_out
        child.expect_exact("(s)earch")

        sl(child, "manage")
        child.expect_exact("(s)tatus")

        sl(child, "status")
        child.expect_exact("Active User")
        child.expect_exact("Raindrops")
        child.expect_exact("Collections")
        child.expect_exact("As Of")

        sl(child, ".")
        sl(child, "create")

        child.expect_exact("create")
        sl(child, "url")

        child.expect_exact("url?")
        sl(child, "https://www.python.org")

        child.expect_exact("title?")
        sl(child, "aTitle")

        child.expect_exact("description?")
        sl(child, "aDescription")

        child.expect_exact("collection?")
        sl(child, "")

        child.expect_exact("tag(s)")
        sl(child, "")

        child.expect_exact("Is this correct?")
        sl(child, "y")

        sl(child, "quit")

        child.terminate()
