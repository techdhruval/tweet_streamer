import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

bearer_token = os.environ.get("BEARER_TOKEN")


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(f"Cannot get rules (HTTP {response.status_code}): {response.text}")

    print(json.dumps(response.json()))
    return response.json()


def set_rules():
    """
    I am using the context operator here with the domain id and entity_id,
    To retrieve tweets of a specific person we can also specify that via "from" or "@" operator
    """
    sample_rules = [
        {"value": "context:165.1001503516555337728 -is:retweet", "tag": "Blockchain"},
        {"value": "context:131.1007360414114435072 OR context:174.1007360414114435072", "tag": "Bitcoin cryptocurrency"},
        {"value": "context:131.1007361429752594432 OR context:174.1007361429752594432", "tag": "Ethereum cryptocurrency"},
        {"value": "context:131.1293666530111008769 -is:retweet", "tag": "Instagram influencers"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(f"Cannot add rules (HTTP {response.status_code}): {response.text}")

    print(json.dumps(response.json()))


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(f"Cannot delete rules (HTTP {response.status_code}): {response.text}")

    print(json.dumps(response.json()))


def get_stream():
    params = {'tweet.fields': 'author_id'}
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True, params=params
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(f"Cannot get stream (HTTP {response.status_code}): {response.text}")

    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            json_object = json.dumps(json_response, indent=4, sort_keys=True)
            print(json_object)
            with open("tweets.json", "a") as f:
                f.write(json_object)
                f.write(',\n')


if __name__ == "__main__":
    # set_rules()
    # rules = get_rules()
    # delete_all_rules(rules)
    get_stream()
