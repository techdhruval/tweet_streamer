import json
from datetime import datetime

import requests
from dotenv import load_dotenv

from auth import bearer_auth
from config import Config
from constants import USE_SOCIAL_QUERY, LAST_SEVEN_DAYS_TOKEN_QUERY
from db_connection import db

load_dotenv()

# https://twittercommunity.com/t/all-of-my-searches-return-only-140-character-tweets/158449

db.execute_query(USE_SOCIAL_QUERY)

author_id_dict = {}


def get_rows():
    """
    This will fetch all the token from the last seven days
    :return:
    """
    return db.fetchall(LAST_SEVEN_DAYS_TOKEN_QUERY)


def get_recent_search(auth, params):
    """
    This will make request to the twitter's recent search API and return the response
    :param auth:
    :param params:
    :return:
    """
    response = requests.get("https://api.twitter.com/2/tweets/search/recent", auth=auth, params=params)
    return response.json()


def add_to_dict(response, symbol):
    """
    This function will add author data to the dictionary, increment the count id the author data is already available
    :param response:
    :param symbol:
    :return:
    """
    for data in response.get('data', []):
        if author_id_dict.get(data.get('author_id')):
            if symbol not in author_id_dict[data.get('author_id')]['tokens']:
                author_id_dict[data.get('author_id')]['tokens'].append(symbol)
            author_id_dict[data.get('author_id')]['count'] += 1
        else:
            author_id_dict[data.get('author_id')] = {'count': 1, 'tokens': []}
            author_id_dict[data.get('author_id')]['tokens'].append(symbol)


def fetch_tweets():
    """
    This will fetch the tweets data based in the query, start_time and end_time
    :return:
    """
    rows = get_rows()

    for row in rows:
        symbol = row[0].strip().replace(' ', '')
        name = row[1].strip().replace(' ', '')
        query_params = {'query': f'("#{symbol}" OR "#{name}" OR "${symbol}" OR "${name}") (context:165.1001503516555337728 OR context:131.1007361429752594432 OR context:174.1007361429752594432) -is:retweet',
                        'start_time': f"{datetime.fromtimestamp(int(row[2])).isoformat()}Z",
                        'end_time': f"{datetime.fromtimestamp(int(row[2]) + 3600).isoformat()}Z",
                        'tweet.fields': 'author_id,created_at,public_metrics',
                        'max_results': 100}
        response = get_recent_search(auth=bearer_auth.token, params=query_params)
        if response.get('errors'):
            if 'end_time' in str(response.get('errors')):
                query_params.pop('end_time')
            response = get_recent_search(auth=bearer_auth.token, params=query_params)

        add_to_dict(response, symbol)

        # Below code is commented temporarily, to not exhaust the monthly tweet quota, because it finds the next_token
        # from the response and fetches all the tweets that methods the query until

        # while response.get('meta').get('next_token'):
        #     query_params['next_token'] = response.get('meta').get('next_token')
        #     response = get_recent_search(auth=bearer_auth.token, params=query_params)
        #     add_to_dict(response, symbol)


def store_to_json(data):
    """
    This function stores the data to the json file to see the fetched data
    :param data:
    :return:
    """
    with open('author.json', 'w') as fp:
        json.dump(data, fp)


def get_alpha_hunter():
    """
    This function will call the fetch_tweet function and then call the store_to_json function and at last it loads the
    data from the json file and check for the alpha hunters based on the given criteria
    :return:
    """
    fetch_tweets()
    store_to_json(author_id_dict)
    with open('author.json', 'r') as file:
        json_data = json.load(file)
        return [data for data in json_data if len(json_data.get(data).get('tokens')) > Config.ALPHA_FINDER_CRITERIA]


if __name__ == "__main__":
    alpha_hunters = get_alpha_hunter()
