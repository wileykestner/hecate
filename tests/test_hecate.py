# coding=utf-8

import hecate.runner as r
from hecate.hecate import Runner, AbnormalExit
import tempfile
import pytest
import sys
import os
import signal

Runner.print_on_exit = True


def test_can_launch_a_simple_program():
    f = tempfile.mktemp()
    with Runner("bash", "-c", "echo hello world > %s" % (f,)):
        return
    with open(f) as r:
        assert "Hello world" in r.read()


def test_can_kill_vim():
    with Runner("vim") as h:
        h.await_text("VIM")
        h.press(":")
        h.press("q")
        h.press("Enter")


def test_can_write_unicode():
    with Runner("cat") as h:
        h.write("☃")
        h.await_text("☃")


def test_can_run_vim():
    f = tempfile.mktemp()
    with Runner("/usr/bin/vim") as h:
        h.await_text("VIM")
        h.press("i")
        h.write("Hello world")
        h.press("Enter")
        h.write("Goodbye world")
        h.press("Escape")
        h.write("dd")
        h.write(":w " + f)
        h.press("Enter")
        h.write(":q")
        h.press("Enter")
        # Second enter because if running with unset environment in tox it will
        # complain that it can't write viminfo and tell you to press enter to
        # continue.
        h.press("Enter")
        h.await_exit()
    with open(f) as r:
        text = r.read()
        assert "Hello world" in text
        assert "Goodbye world" not in text


def test_can_send_enter():
    with Runner("cat") as h:
        h.write("hi")
        h.press("Enter")
        h.write("there")
        h.await_text("there")
        assert "hi\nthere" in h.screenshot()


def test_reports_abnormal_exit():
    with pytest.raises(AbnormalExit):
        with Runner("cat", "/does/not/exist/no/really"):
            pass


def test_can_send_eof():
    with Runner("cat") as h:
        h.press("C-d")
        h.await_exit()


def test_sets_the_console_size_appropriately():
    with Runner("cat", width=10, height=100) as h:
        h.write("." * 100)
        h.press("Enter")
        h.write("Squirrel")
        h.await_text("Squirrel")
        assert "." * 10 + "\n" + "." * 10 in h.screenshot()
        h.press("Enter")
        h.press("C-d")
        h.await_exit()


PRINTER = os.path.join(
    os.path.abspath(
        os.path.dirname(__file__)), "..", "scripts", "sigprinter.py")


def test_can_send_signals_to_child():
    with pytest.raises(AbnormalExit):
        with Runner(sys.executable, PRINTER) as h:
            for s in ["SIGTERM", "SIGUSR1", "SIGQUIT"]:
                h.kill(s)
                h.await_text(s)


def test_uses_last_screenshot_if_server_goes_away():
    with Runner("cat") as h:
        h.write("Hello")
        h.await_text("Hello")
        h.kill("SIGKILL")
        with pytest.raises(AbnormalExit):
            h.await_exit()
        controller = h.report_variables()[r.CONTROLLER]
        os.kill(controller, signal.SIGKILL)
        assert "Hello" in h.screenshot()


def test_can_capture_curses_hline_and_vline_characters():
    with Runner("./tests/fixtures/box.py") as h:
        h.await_text("┌──────────┐")
        h.await_text("│I am a box│")
        h.await_text("└──────────┘")
        h.press("q")
        h.await_exit()
