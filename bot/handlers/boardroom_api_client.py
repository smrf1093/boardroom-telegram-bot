from functools import wraps
import json

import redis
import requests

from conf.settings import REDIS_URL

# Connect to our Redis instance
redis_instance = redis.StrictRedis.from_url(url=REDIS_URL, db=1)


def cached(ttl_seconds: int = None):
    """Decorator that caches the results of the function call.

    We use Redis in this example, but any cache (e.g. memcached) will
    work. We also assume that the result of the function can be
    seralized as JSON, which obviously will be untrue in many
    situations. Tweak as needed.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate the cache key from the function's arguments.
            key_parts = [func.__name__] + list(args[1:])
            key = "-".join([k if k else "none" for k in key_parts])
            result = redis_instance.get(key)

            if result is None:
                # Run the function and cache the result for next time.
                value = func(*args, **kwargs)
                value_json = json.dumps(value)
                redis_instance.set(key, value_json, ex=ttl_seconds)
            else:
                # Skip the function entirely and use the cached value instead.
                print("Cache hit!, loading from cache...")
                value_json = result.decode("utf-8")
                value = json.loads(value_json)

            return value

        return wrapper

    return decorator


BASE_BROADROOM_API_URL = "https://api.boardroom.info/v1/"


class BroadroomAPIClient:
    def __str__(self) -> str:
        return "boardroom"

    def get_protocols(self, next_cursor=None):
        url = f"{BASE_BROADROOM_API_URL}protocols"
        if next_cursor:
            url += f"?cursor={next_cursor}"
        response = requests.get(url)
        json_response = json.loads(response.content)
        return json_response

    def get_single_protocol(self, cname):
        response = requests.get(f"{BASE_BROADROOM_API_URL}protocols/{cname}")
        json_response = json.loads(response.content)
        return json_response

    def get_proposals(self, next_cursor=None):
        url = f"{BASE_BROADROOM_API_URL}proposals"
        if next_cursor:
            url += f"?cursor={next_cursor}"
        response = requests.get(url)
        json_response = json.loads(response.content)
        return json_response

    def get_protocol_proposals(self, cname, next_cursor=None):
        url = f"{BASE_BROADROOM_API_URL}protocols/{cname}/proposals"
        if next_cursor:
            url += f"?cursor={next_cursor}"
        response = requests.get(url)
        json_response = json.loads(response.content)
        return json_response

    def get_single_proposal(self, refId):
        response = requests.get(f"{BASE_BROADROOM_API_URL}proposals/{refId}")
        json_response = json.loads(response.content)
        return json_response

    def get_proposal_votes(self, refId, next_cursor=None):
        url = f"{BASE_BROADROOM_API_URL}proposals/{refId}/votes"
        if next_cursor:
            url += f"?cursor={next_cursor}"
        response = requests.get(url)
        json_response = json.loads(response.content)
        return json_response

    def get_votes_by_voters(self, address, next_cursor=None):
        url = f"{BASE_BROADROOM_API_URL}voters/{address}/votes"
        if next_cursor:
            url += f"?cursor={next_cursor}"
        response = requests.get(url)
        json_response = json.loads(response.content)
        return json_response

    def get_protocol_voters(self, cname, next_cursor=None):
        url = f"{BASE_BROADROOM_API_URL}protocols/{cname}/voters"
        if next_cursor:
            url += f"?cursor={next_cursor}"
        response = requests.get(url)
        json_response = json.loads(response.content)
        return json_response

    def get_voters(self, next_cursor=None):
        url = f"{BASE_BROADROOM_API_URL}voters"
        if next_cursor:
            url += f"?cursor={next_cursor}"
        response = requests.get(url)
        json_response = json.loads(response.content)
        return json_response

    def get_single_voter(self, address):
        response = requests.get(f"{BASE_BROADROOM_API_URL}voters/{address}")
        json_response = json.loads(response.content)
        return json_response

    def get_stat(self):
        response = requests.get(f"{BASE_BROADROOM_API_URL}stats")
        json_response = json.loads(response.content)
        return json_response

    @cached(ttl_seconds=300)
    def get_protocols_cached(self, next_cursor=None):
        return self.get_protocols(next_cursor)

    @cached(ttl_seconds=60)
    def get_single_protocol_cached(self, cname):
        return self.get_single_protocol(cname)

    @cached(ttl_seconds=60)
    def get_proposals_cached(self, next_cursor=None):
        return self.get_proposals(next_cursor)

    @cached(ttl_seconds=60)
    def get_protocol_proposals_cached(self, cname, next_cursor=None):
        return self.get_protocol_proposals(cname, next_cursor)

    @cached(ttl_seconds=60)
    def get_single_proposal_cached(self, refId):
        return self.get_single_proposal(refId)

    @cached(ttl_seconds=60)
    def get_proposal_votes_cached(self, refId, next_cursor=None):
        return self.get_proposal_votes(refId, next_cursor)

    @cached(ttl_seconds=60)
    def get_votes_by_voters_cached(self, address, next_cursor=None):
        return self.get_votes_by_voters(address, next_cursor)

    @cached(ttl_seconds=60)
    def get_protocol_voters_cached(self, cname, next_cursor=None):
        return self.get_protocol_voters(cname, next_cursor)

    @cached(ttl_seconds=60)
    def get_voters_cached(self, next_cursor=None):
        return self.get_voters(next_cursor)

    @cached(ttl_seconds=60)
    def get_single_voter_cached(self, address):
        return self.get_single_voter(address)
