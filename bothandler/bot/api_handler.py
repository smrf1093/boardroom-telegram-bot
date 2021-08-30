import requests
import json

class BroadroomAPIHandler():
    BASE_BROADROOM_API_URL = 'https://api.boardroom.info/v1/'

    def get_protocols(self):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}protocols')
        json_response = json.loads(response.content)
        return json_response

    def get_single_protocol(self, cname):
        response = requests.get(f"{BroadroomAPIHandler.BASE_BROADROOM_API_URL}protocols/{cname}")
        json_response = json.loads(response.content)
        return json_response
    
    def get_proposals(self):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}proposals')
        json_response = json.loads(response.content)
        return json_response

    def get_protocol_proposals(self, cname):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}protocols/{cname}/proposals')
        json_response = json.loads(response.content)
        return json_response
    
    def get_single_proposal(self, refId):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}proposals/{refId}')
        json_response = json.loads(response.content)
        return json_response

    def get_proposal_votes(self, refId):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}proposals/{refId}/votes')
        json_response = json.loads(response.content)
        return json_response

    def get_votes_by_voters(self, address):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}voters/{address}/votes')
        json_response = json.loads(response.content)
        return json_response
    
    def get_protocol_voters(self, cname):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}protocols/{cname}/voters')
        json_response = json.loads(response.content)
        return json_response
    
    def get_voters(self):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}voters')
        json_response = json.loads(response.content)
        return json_response
    
    def get_single_voter(self, address):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}voters/{address}')
        json_response = json.loads(response.content)
        return json_response
    
    def get_stat(self):
        response = requests.get(f'{BroadroomAPIHandler.BASE_BROADROOM_API_URL}stats')
        json_response = json.loads(response.content)
        return json_response

