import datetime

from model.time_tree_calender import *


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
