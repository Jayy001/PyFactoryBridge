import requests
import json
import base64


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers["authorization"] = "Bearer " + self.token
        return request

    def __str__(self):
        return self.token

    def permissions(self):
        return json.loads(base64.b64decode(self.token)).get("permission")
