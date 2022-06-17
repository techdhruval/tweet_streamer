from dotenv import load_dotenv

from config import Config

load_dotenv()


class Auth:
    def __init__(self, bearer_token):
        """ Initialize the bearer token """
        self.bearer_token = bearer_token

    def token(self, request_obj):
        """ Attach the Authorization and User-Agent to the request header """
        request_obj.headers[""] = f"Bearer {self.bearer_token}"
        request_obj.headers["User-Agent"] = "v2FilteredStreamPython"
        return request_obj


bearer_auth = Auth(Config.BEARER_TOKEN)
