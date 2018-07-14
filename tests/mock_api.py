from httmock import all_requests


@all_requests
def non_json_episode_response(url, request):
    return {'status_code': 200, 'content': None}


@all_requests
def unauthorized_episode_response(url, request):
    return {'status_code': 401, 'content': '{"error": "access_denied", "error_message": "The resource owner or authorization server denied the request."}'}


@all_requests
def none_ok_episode_response(url, request):
    return {'status_code': 500, 'content': None}


@all_requests
def fail_get_token(url, request):
    return {'status_code': 401, 'content': '{"error":"invalid_client","error_message":"Client authentication failed."}'}


@all_requests
def non_json_repsonse_for_authentication(url, request):
    return {'status_code': 500, 'content': 'Something went wrong.'}


@all_requests
def test_forbidden_repsonse_for_authentication(url, request):
    return {'status_code': 403, 'content': '{"error": "access_denied"}'}
