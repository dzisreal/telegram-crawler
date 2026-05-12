"""Unit tests for progress reporter."""

from telegram_crawler.progress import ProgressReporter


def test_progress_reporter_init():
    reporter = ProgressReporter("testchannel")
    assert reporter.channel_name == "testchannel"
    assert reporter.count == 0


def test_progress_reporter_update():
    reporter = ProgressReporter("testchannel")
    reporter.update(100)
    assert reporter.count == 100
    reporter.update(50)
    assert reporter.count == 150


def test_progress_reporter_start(capsys):
    reporter = ProgressReporter("mychannel")
    reporter.start()
    # start() prints to console — just verify it doesn't crash


def test_progress_reporter_finish(capsys):
    reporter = ProgressReporter("mychannel")
    reporter.update(50)
    reporter.finish()
    # finish() prints summary — just verify it doesn't crash