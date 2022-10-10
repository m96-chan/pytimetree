from __future__ import annotations

import datetime
from dataclasses import dataclass

import pytz

from pytimetree.time_tree_request import TimeTreeRequest


@dataclass
class TimeTreeEventAttributes:
    title: str
    category: str
    all_day: bool
    start_at: datetime.datetime
    end_at: datetime.datetime
    start_timezone: str = "Asia/Tokyo"
    end_timezone: str = "Asia/Tokyo"
    description: str | None = None
    location: str | None = None
    url: str | None = None

    @property
    def start_at_iso8601(self):
        if self.all_day:
            tmp = datetime.datetime.combine(self.start_at.date(), datetime.datetime.min.time())
            return pytz.timezone(self.start_timezone).localize(tmp).isoformat()
        return pytz.timezone(self.start_timezone).localize(self.start_at).isoformat()

    @property
    def end_at_iso8601(self):
        if self.all_day:
            tmp = datetime.datetime.combine(self.end_at.date(), datetime.datetime.min.time())
            return pytz.timezone(self.end_timezone).localize(tmp).isoformat()
        return pytz.timezone(self.end_timezone).localize(self.end_at).isoformat()

    @property
    def dict(self) -> dict:
        dic = {k: v for k, v in self.__dict__.items() if v is not None}
        return {
            **dic, **{
                "start_at": self.start_at_iso8601,
                "end_at": self.end_at_iso8601
            }
        }

    @classmethod
    def form_dict(cls, dic: dict) -> TimeTreeEventAttributes:
        return cls(
            dic['title'],
            dic['category'],
            dic['all_day'],
            dic['start_at'],
            dic['end_at'],
            dic['start_timezone'],
            dic['end_timezone'],
            dic.get('description'),
            dic.get('location'),
            dic.get('url')
        )


@dataclass
class TimeTreeLabelAttributes:
    name: str
    color: str

    @property
    def dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, dic) -> TimeTreeLabelAttributes:
        return TimeTreeLabelAttributes(dic['name'], dic['color'])


@dataclass
class TimeTreeLabel(TimeTreeRequest):
    id: str
    attributes: TimeTreeLabelAttributes | None = None

    def __eq__(self, other):
        if isinstance(other, TimeTreeLabel):
            return self.id == other.id
        return False

    @property
    def type(self):
        return "label"

    @property
    def dict(self):
        return {
            "id": self.id,
            "type": self.type
        }

    @property
    def full_dict(self):
        return {**self.dict, **{"attributes": self.attributes.dict}}

    @classmethod
    def from_dict(cls, dic) -> TimeTreeLabel:
        return cls(
            dic['id'],
            TimeTreeLabelAttributes.from_dict(dic['attributes']) if dic.get('attributes') else None
        )


@dataclass
class TimeTreeMemberAttributes:
    name: str
    description: str
    image_url: str

    @property
    def dict(self) -> dict:
        return self.__dict__

    @classmethod
    def from_dict(cls, dic) -> TimeTreeMemberAttributes:
        return TimeTreeMemberAttributes(dic['name'], dic['description'], dic['image_url'])


@dataclass
class TimeTreeMember:
    id: str
    attributes: TimeTreeMemberAttributes | None = None

    def __eq__(self, other):
        if isinstance(other, TimeTreeMember):
            return self.id == other.id
        return False

    @property
    def type(self):
        return "user"

    @property
    def dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type
        }

    @property
    def full_dict(self):
        return {**self.dict, **{"attributes": self.attributes.dict}}

    @classmethod
    def from_dict(cls, dic: dict) -> TimeTreeMember:
        return TimeTreeMember(
            dic['id'],
            TimeTreeMemberAttributes.from_dict(dic["attributes"]) if dic.get('attributes') else None
        )


@dataclass
class TimeTreeEventRelationships:
    label: TimeTreeLabel
    attendees: list[TimeTreeMember]
    creator: TimeTreeMember | None = None

    @property
    def dict(self):
        return {
            "label": {
                "data": self.label.dict
            },
            "attendees": {
                "data": [a.dict for a in self.attendees]
            }
        }

    @classmethod
    def from_dict(cls, dic: dict) -> TimeTreeEventRelationships:
        return cls(
            TimeTreeLabel.from_dict(dic["label"]["data"]),
            [TimeTreeMember.from_dict(m) for m in dic["attendees"]["data"]],
            TimeTreeMember.from_dict(dic["creator"]["data"]) if dic.get("creator") else None
        )


@dataclass
class TimeTreeEventValue(TimeTreeRequest):
    attributes: TimeTreeEventAttributes
    relationships: TimeTreeEventRelationships

    @property
    def dict(self):
        return {
            "data": {
                "attributes": self.attributes.dict,
                "relationships": self.relationships.dict
            }
        }


@dataclass
class TimeTreeEvent(TimeTreeEventValue):
    id: str

    def __eq__(self, other):
        if isinstance(other, TimeTreeEvent):
            if self.id and other.id:
                return self.id == TimeTreeEvent.id
        return False

    def update_event(self):
        return self.put_request(f"/calendar/events/{self.id}", self.dict)

    def delete_event(self):
        return self.delete_request(f"/calendar/events/{self.id}")

    @classmethod
    def from_dict(cls, dic: dict) -> TimeTreeEvent:
        return cls(
            TimeTreeEventAttributes.form_dict(dic["attributes"]),
            TimeTreeEventRelationships.from_dict(dic["relationships"]), dic['id'])


@dataclass
class TimeTreeCalenderAttributes:
    name: str
    created_at: datetime
    description: str
    image_url: str | None
    color: str
    order: int

    @classmethod
    def from_dict(cls, dic) -> TimeTreeCalenderAttributes:
        return TimeTreeCalenderAttributes(
            dic['name'],
            datetime.datetime.fromisoformat(dic['created_at'].replace('Z', '+00:00')),
            dic['description'],
            dic.get('image_url'),
            dic['color'],
            dic['order'],
        )


@dataclass
class TimeTreeCalender(TimeTreeRequest):
    id: str
    attributes: TimeTreeCalenderAttributes
    _labels: list[TimeTreeLabel] | None = None
    _members: list[TimeTreeMember] | None = None

    def __eq__(self, other):
        if isinstance(other, TimeTreeCalender):
            return self.id == other.id
        return False

    @classmethod
    def from_dict(cls, dic: dict) -> TimeTreeCalender:
        return TimeTreeCalender(
            dic['id'], TimeTreeCalenderAttributes.from_dict(dic['attributes'])
        )

    @property
    def labels(self) -> list[TimeTreeLabel]:
        if self._labels is None:
            res = self.get_request(f"/calendars/{self.id}/labels")
            self._labels = [TimeTreeLabel.from_dict(l) for l in res['data']]
        return self._labels

    @property
    def members(self) -> list[TimeTreeMember]:
        if self._members is None:
            res = self.get_request(f"/calendars/{self.id}/members")
            self._members = [TimeTreeMember.from_dict(m) for m in res['data']]
        return self._members

    @classmethod
    def get_list(cls) -> list[TimeTreeCalender]:
        return [cls.from_dict(j) for j in cls.get_request("/calendars")["data"]]

    @classmethod
    def get_by_id(cls, calender_id: str) -> TimeTreeCalender:
        return cls.from_dict(cls.get_request(f"/calendars/{calender_id}/")["data"])

    def get_upcoming_events(self, days: int = 1, timezone: str = "Asia/Tokyo") -> list[TimeTreeEvent]:
        # A range from 1 to 7 can be specified.
        if days not in range(1, 8):
            raise ValueError(f"days {days}: A range from 1 to 7 can be specified.")
        res = self.get_request(
            f"/calendars/{self.id}/upcoming_events?timezone={timezone}&days={days}"
        )["data"]
        return [TimeTreeEvent.from_dict(e) for e in res]

    def create_event(self, ev: TimeTreeEventValue) -> TimeTreeEvent:
        return TimeTreeEvent.from_dict(self.post_request(f"/calendars/{self.id}/events", ev.dict))

    def update_event(self, ev: TimeTreeEvent) -> TimeTreeEvent:
        return TimeTreeEvent.from_dict(self.put_request(f"/calendars/{self.id}/events/{ev.id}", ev.dict))

    def delete_event(self, ev: TimeTreeEvent) -> None:
        self.delete_request(f"/calendars/{self.id}/events/{ev.id}")
