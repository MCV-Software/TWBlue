# -*- coding: utf-8 -*-
import pytest
import gettext
import datetime
gettext.install("test")
from unittest import mock
from sessions.twitter import templates

def test_default_values():
    """ Tests wheter default values are the expected ones.
    This might be useful so we will have this failing when we update anything from those values.
    As TWBlue might be using those from other dialogs.
    """
    assert templates.tweet_variables == ["date", "display_name", "screen_name", "source", "lang", "text", "image_descriptions"]
    assert templates.dm_variables == ["date", "sender_display_name", "sender_screen_name", "recipient_display_name", "recipient_display_name", "text"]
    assert templates.person_variables == ["display_name", "screen_name", "location", "description", "followers", "following", "listed", "likes", "tweets", "created_at"]

@pytest.mark.parametrize("offset, language, expected_result", [
    (0, "en_US", "Wednesday, October 10, 2018 20:19:24"),
    (-21600, "en_US", "Wednesday, October 10, 2018 14:19:24"),
    (7200, "en_US", "Wednesday, October 10, 2018 22:19:24"),
    (0, "es_ES", "miércoles, octubre 10, 2018 20:19:24"),
    (-21600, "es_ES", "miércoles, octubre 10, 2018 14:19:24"),
    (7200, "es_ES", "miércoles, octubre 10, 2018 22:19:24"),
    (18000, "es_ES", "jueves, octubre 11, 2018 1:19:24"),
])
def test_process_date_absolute_time(offset, language, expected_result):
    """ Tests date processing function for tweets, when relative_times is set to False. """
    # Date representation used by twitter, converted to datetime object, as tweepy already does this.
    # Original date was Wed Oct 10 20:19:24 +0000 2018
    date_field = datetime.datetime(2018, 10, 10, 20, 19, 24)
    with mock.patch("languageHandler.curLang", new=language):
        processed_date = templates.process_date(date_field, relative_times=False, offset_seconds=offset)
        assert processed_date == expected_result

def test_process_date_relative_time():
    date_field = datetime.datetime(2018, 10, 10, 20, 19, 24)
    with mock.patch("languageHandler.curLang", new="es_ES"):
        processed_date = templates.process_date(date_field, relative_times=True, offset_seconds=7200)
        # As this depends in relative times and this is subject to change, let's do some light checks here and hope the string is going to be valid.
        assert isinstance(processed_date, str)
        assert "hace" in processed_date and "años" in processed_date

def test_process_text_basic_tweet(basic_tweet):
    expected_result = "Changes in projects for next year https://manuelcortez.net/blog/changes-in-projects-for-next-year/#.YdMQQU6t1FI.twitter"
    text = templates.process_text(basic_tweet)
    assert text == expected_result