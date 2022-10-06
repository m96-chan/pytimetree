import functools

import requests
from requests import HTTPError


def triable_request(f):
    @functools.wraps(f)
    def deco_wrap(*args, **kwargs):
        print(f"{f.__name__} called.")
        res = None
        try:
            res = f(*args, **kwargs)
            # success only
            return res.json()
        except HTTPError as e:
            print(f"{res.status_code}:{e.response.text}")
            raise e

    return deco_wrap


class TimeTreeRequest:
    BASE_URI = "https://timetreeapis.com"
    TOKEN = ""

    @classmethod
    def no_body_request(cls, method, endpoint, **kwargs):
        url = f"{cls.BASE_URI}{endpoint}"
        arg_dict = {**kwargs, **{
            "headers": {
                "Authorization": f"Bearer {cls.TOKEN}",
                "Accept": "application/vnd.timetree.v1+json"
            }
        }}
        return requests.request(method, url, **arg_dict)

    @classmethod
    @triable_request
    def get_request(cls, endpoint, **kwargs):
        return cls.no_body_request('GET', endpoint, **kwargs)

    @classmethod
    @triable_request
    def delete_request(cls, endpoint, **kwargs):
        return cls.no_body_request('DELETE', endpoint, **kwargs)

    @classmethod
    def body_request(cls, method: str, endpoint: str, body: dict, **kwargs):
        url = f"{cls.BASE_URI}{endpoint}"
        arg_dict = {**kwargs, **{
            "headers": {
                "Authorization": f"Bearer {cls.TOKEN}",
                "Accept": "application/vnd.timetree.v1+json",
                "Content-Type": "application/json",
            }, **{
                "json": body
            }
        }}
        return requests.request(method, url, **arg_dict)

    @classmethod
    @triable_request
    def post_request(cls, endpoint: str, json: dict, **kwargs):
        return cls.body_request('POST', endpoint, json, **kwargs)

    @classmethod
    @triable_request
    def put_request(cls, endpoint: str, json: dict, **kwargs):
        return cls.body_request('PUT', endpoint, json, **kwargs)