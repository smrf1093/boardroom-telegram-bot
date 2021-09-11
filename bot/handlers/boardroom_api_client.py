from datetime import timedelta
import requests
import json


from functools import wraps
from .utils import cached

BASE_BROADROOM_API_URL = 'https://api.boardroom.info/v1/'

class BroadroomAPIClient:
    def __str__(self) -> str:
        return "boardroom"

    def get_protocols(self):
        response = requests.get(f'{BASE_BROADROOM_API_URL}protocols')
        json_response = json.loads(response.content)
        return json_response

    def get_single_protocol(self, cname):
        response = requests.get(f"{BASE_BROADROOM_API_URL}protocols/{cname}")
        json_response = json.loads(response.content)
        return json_response
    
    def get_proposals(self, next_cursor = None):
        url = f'{BASE_BROADROOM_API_URL}proposals'
        if next_cursor:
            url += f'?nextCurosor={next_cursor}'
        response = requests.get(url)
        json_response = json.loads(response.content)
        return json_response

    def get_protocol_proposals(self, cname):
        response = requests.get(f'{BASE_BROADROOM_API_URL}protocols/{cname}/proposals')
        json_response = json.loads(response.content)
        return json_response
    
    def get_single_proposal(self, refId):
        response = requests.get(f'{BASE_BROADROOM_API_URL}proposals/{refId}')
        json_response = json.loads(response.content)
        return json_response

    def get_proposal_votes(self, refId):
        response = requests.get(f'{BASE_BROADROOM_API_URL}proposals/{refId}/votes')
        json_response = json.loads(response.content)
        return json_response

    def get_votes_by_voters(self, address):
        response = requests.get(f'{BASE_BROADROOM_API_URL}voters/{address}/votes')
        json_response = json.loads(response.content)
        return json_response
    
    def get_protocol_voters(self, cname):
        response = requests.get(f'{BASE_BROADROOM_API_URL}protocols/{cname}/voters')
        json_response = json.loads(response.content)
        return json_response
    
    def get_voters(self):
        response = requests.get(f'{BASE_BROADROOM_API_URL}voters')
        json_response = json.loads(response.content)
        return json_response
    
    def get_single_voter(self, address):
        response = requests.get(f'{BASE_BROADROOM_API_URL}voters/{address}')
        json_response = json.loads(response.content)
        return json_response
    
    def get_stat(self):
        response = requests.get(f'{BASE_BROADROOM_API_URL}stats')
        json_response = json.loads(response.content)
        return json_response

    @cached(ttl_seconds=300)
    def get_protocols_cached(self):
        return self.get_protocols()

    @cached(ttl_seconds=60)
    def get_single_protocol_cached(self, cname):
        return self.get_single_protocol(cname)

    @cached(ttl_seconds=60)
    def get_proposals_cached(self):
        return self.get_proposals()

    @cached(ttl_seconds=60)
    def get_protocol_proposals_cached(self, cname):
        return self.get_protocol_proposals(cname)

    @cached(ttl_seconds=60)
    def get_single_proposal_cached(self, refId):
        return self.get_single_proposal(refId)

    @cached(ttl_seconds=60)
    def get_proposal_votes_cached(self, refId):
        return self.get_proposal_votes(refId)

    @cached(ttl_seconds=60)
    def get_votes_by_voters_cached(self, address):
        return self.get_votes_by_voters(address)

    @cached(ttl_seconds=60)
    def get_protocol_voters_cached(self, cname):
        return self.get_protocol_voters(cname)

    @cached(ttl_seconds=60)
    def get_voters_cached(self):
        return self.get_voters()

    @cached(ttl_seconds=60)
    def get_single_voter_cached(self, address):
        return self.get_single_voter(address)