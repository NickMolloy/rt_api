import os
import sys

import pytest
import vcr
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rt_api import api, constants


@pytest.fixture(scope="class")
@vcr.use_cassette("tests/fixtures/vcr_cassettes/get_token.yaml")
def auth(request):
    client = BackendApplicationClient(client_id=constants.CLIENT_ID)
    oauth = OAuth2Session(client=client)
    oauth.fetch_token(token_url=constants.AUTH_URL, client_id=constants.CLIENT_ID,
                      client_secret=constants.CLIENT_SECRET)
    request.cls.auth = oauth
    yield
