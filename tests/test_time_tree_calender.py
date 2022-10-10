import os

import pytest

from pytimetree.time_tree_calender import *

TEST_TOKEN = os.getenv("TEST_TOKEN")
TEST_CALENDER_ID = os.getenv("TEST_CALENDER_ID")
TEST_SKIP_API_ACCESS = os.getenv("TEST_SKIP_API_ACCESS", True)


def test_TimeTreeEventAttributes():
    o = TimeTreeEventAttributes(
        title="title",
        category="category",
        all_day=False,
        start_at=datetime.datetime(2020, 1, 12, 9, 54, 32, 0),
        end_at=datetime.datetime(2021, 2, 23, 10, 43, 21, 0),
    )

    # testing default values
    assert o.start_timezone == "Asia/Tokyo"
    assert o.end_timezone == "Asia/Tokyo"
    assert o.description is None
    assert o.location is None
    assert o.url is None

    # testing start_at_iso8601
    o.all_day = False
    assert o.start_at_iso8601 == "2020-01-12T09:54:32+09:00"
    o.all_day = True
    assert o.start_at_iso8601 == "2020-01-12T00:00:00+09:00"

    # testing end_at_iso8601
    o.all_day = False
    assert o.end_at_iso8601 == "2021-02-23T10:43:21+09:00"
    o.all_day = True
    assert o.end_at_iso8601 == "2021-02-23T00:00:00+09:00"

    expect = {
        "title": "title",
        "category": "category",
        "all_day": True,
        "start_at": "2020-01-12T00:00:00+09:00",
        "end_at": "2021-02-23T00:00:00+09:00",
        "start_timezone": "Asia/Tokyo",
        "end_timezone": "Asia/Tokyo",
    }

    assert all(v == o.dict[k] for k, v in expect.items()) and len(o.dict) == len(expect)


@pytest.mark.skipif(TEST_SKIP_API_ACCESS, reason="Because this is API Request test.")
def test_TimeTreeCalender__get_by_id():
    TimeTreeCalender.TOKEN = TEST_TOKEN
    calender = TimeTreeCalender.get_by_id(TEST_CALENDER_ID)
    assert isinstance(calender, TimeTreeCalender)


@pytest.mark.skipif(TEST_SKIP_API_ACCESS, reason="Because this is API Request test.")
def test_TimeTreeCalender__get_list():
    TimeTreeCalender.TOKEN = TEST_TOKEN
    calenders = TimeTreeCalender.get_list()
    assert isinstance(calenders, list)
    assert all([isinstance(c, TimeTreeCalender) for c in calenders])


@pytest.mark.skipif(TEST_SKIP_API_ACCESS, reason="Because this is API Request test.")
def test_TimeTreeCalender__get_upcoming_events():
    TimeTreeCalender.TOKEN = TEST_TOKEN
    print(TEST_CALENDER_ID)
    events = TimeTreeCalender.get_by_id(TEST_CALENDER_ID).get_upcoming_events()
    assert all([isinstance(e, TimeTreeEvent) for e in events])
