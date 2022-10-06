from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pytz

from model.time_tree_request import TimeTreeRequest


@dataclass
class TimeTreeEventAttributes:
    title: str
    category: str
    all_day: bool
    start_at: datetime
    end_at: datetime
    label_id: str
    attendee_ids: list[str]
    start_timezone: str = "Asia/Tokyo"
    end_timezone: str = "Asia/Tokyo"
    description: str | None = None
    location: str | None = None
    url: str | None = None

    @property
    def start_at_iso8601(self):
        if self.all_day:
            tmp = datetime.combine(self.start_at.date(), datetime.min.time())
            return pytz.timezone(self.start_timezone).localize(tmp).isoformat()
        return pytz.timezone(self.start_timezone).localize(self.start_at).isoformat()

    @property
    def end_at_iso8601(self):
        if self.all_day:
            tmp = datetime.combine(self.end_at.date(), datetime.min.time())
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


@dataclass
class TimeTreeLabelAttributes:
    name: str
    color: str

    @property
    def dict(self):
        return self.__dict__


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


@dataclass
class TimeTreeEventMemberAttributes:
    name: str
    description: str
    image_url: str

    @property
    def dict(self) -> dict:
        return self.__dict__


@dataclass
class TimeTreeEventMember:
    id: str
    attributes: TimeTreeEventMemberAttributes | None = None

    def __eq__(self, other):
        if isinstance(other, TimeTreeEventMember):
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


@dataclass
class TimeTreeEventRelationships:
    label: TimeTreeLabel
    attendees: list[TimeTreeEventMember]
    creator: TimeTreeEventMember | None = None

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


@dataclass
class TimeTreeEventValue(TimeTreeRequest):
    calender_id: str
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

    def create_event(self) -> TimeTreeEvent:
        return self.post_request(f"/calendars/{self.calender_id}/events", self.dict)


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


@dataclass
class TimeTreeCalender(TimeTreeRequest):
    id: str
    name: str
    created_at: datetime
    description: str
    image_url: Optional[str]
    color: str
    order: int
    labels: list[TimeTreeLabel]
    members: list[TimeTreeEventMember]

    def __eq__(self, other):
        if isinstance(other, TimeTreeCalender):
            return self.id == other.id
        return False

    @classmethod
    def from_response(cls, json: dict) -> TimeTreeCalender:
        non_complete_calender = cls(
            id=json["id"],
            name=json["attributes"]["name"],
            created_at=datetime.fromisoformat(
                json["attributes"]["created_at"].replace('Z', '+00:00')),
            description=json["attributes"]["description"],
            image_url=json["attributes"]["image_url"] if json["attributes"]["image_url"] else None,
            color=json["attributes"]["color"],
            order=json["attributes"]["order"]
        )
        # completed!!!
        return non_complete_calender

    @classmethod
    def get_list(cls) -> list[TimeTreeCalender]:
        return [cls.from_response(j) for j in cls.get_request("/calendars?include=labels,members")["data"]]

    def get_upcoming_events(self, days: int = 1, timezone: str = "Asia/Tokyo") -> list[TimeTreeEvent]:
        # A range from 1 to 7 can be specified.
        if days not in range(1, 8):
            raise ValueError(f"days {days}: A range from 1 to 7 can be specified.")

        res = self.get_request(
            f"/calendars/{self.id}/upcoming_events?timezone={timezone}&days={days}"
        )["data"]
        return [TimeTreeEvent(
            _id=j['id'],
            title=j['attributes']['title'],
            all_day=j['attributes']['all_day'],
            start_at=datetime.fromisoformat(j["attributes"]["start_at"].replace('Z', '+00:00')),
            end_at=datetime.fromisoformat(j["attributes"]["end_at"].replace('Z', '+00:00')),
            label_id=j['relationships']['label']['data']['id'],
            attendee_ids=[attendee['id'] for attendee in j['relationships']['attendees']['data']],
            description=j['attributes']['description'],
            location=j['attributes']['location'],
            url=j['attributes'].get_request('url')
        ) for j in res]

    def create_event(self, attributes: TimeTreeEventAttributes, relationship: TimeTreeEventRelationships):
        return TimeTreeEventValue(self.id, attributes, relationship).create_event()
