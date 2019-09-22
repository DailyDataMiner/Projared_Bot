import configparser
import json
import logging
import os
import requests
import sys

def get_twitch_data(session, config):

    ## Basic stats
    file_name = 'jumjumjr.py'

    ## Sets up pathing for log file
    current_directory = os.path.dirname(__file__)
    parent = os.path.dirname(current_directory)
    home_dir = os.path.join(parent, 'logs')
    log_path = os.path.join(home_dir, 'log.txt')

    logging.info("Entering " + file_name)

    ## Base headers
    headers = {'Client-ID': config['TwitchAuth']['ClientID']}
    params = {'user_login': config['TwitchStream']['Name']}
    params_host = {'login': config['TwitchStream']['Name']}

    ## Base URLs
    stream_URL = 'https://api.twitch.tv/helix/streams'
    ID_URL = 'https://api.twitch.tv/helix/users'
    game_URL = 'https://api.twitch.tv/helix/games'
    host_URL = 'https://tmi.twitch.tv/hosts'
    twitch_url = 'https://twitch.tv/'

    ## Get request to Twitch. Will return null if not streaming
    response = session.get(stream_URL, params=params, headers=headers)

    ## Who doesn't like a good logging?
    if response.status_code == 200:
        logging.info("Request successful.")
    else:
        logging.error("Request failed. %s", response.json())

    ## First will attempt to get his live data
    try:
        ## Retrieves value from first GET that will fail if he is not streaming
        viewer_count = response.json()['data'][0]['viewer_count']

        ## Gets game ID and prepares the GET call to retrieve game information
        game_id = response.json()['data'][0]['game_id']
        game_params = {'id': game_id}
        response_game = session.get(game_URL, params=game_params, headers=headers)
        ## Retrieves values of game
        game_name = response_game.json()['data'][0]['name']
        box_art_url_template = response_game.json()['data'][0]['box_art_url']
        box_art_url = box_art_url_template.format(width=100, height=100)
        # We now have stream information
        twitch_data = {'status': 'Online',
                       'url': twitch_url + config['TwitchStream']['Name'],
                       'game_name': game_name,
                       'game_box_art': box_art_url,
                       'viewer_count': viewer_count}

    # Exception will occur if he is not streaming
    # Will now check if he is hosting
    except (IndexError, KeyError):
        try:

            ## Have to now retrieve his ID
            response_host = session.get(ID_URL, params=params_host, headers=headers)
            streamer_id = response_host.json()['data'][0]['id']

            host_params = {'include_logins': '1',
                       'host': streamer_id}

            # Foreign API used to obtain hosting information
            response_host = session.get(host_URL, params=host_params)

            if response_host.status_code == 200:
                logging.info("Request successful.")
            else:
                logging.error("Request failed. %s", response_host.json())

            target = response_host.json()['hosts'][0]['target_login']

            # We now have the name of the streamer he is hosting.
            twitch_data = {'status': 'Hosting',
                           'host': target,
                           'url': twitch_url + target}

        ## An error here means Projared is asleep :)
        except:
            twitch_data = {'status': 'Offline'}

    logging.info("Exiting " + file_name)

    return twitch_data

def data():

    current_directory = os.path.dirname(__file__)
    parent_directory = os.path.split(current_directory)[0]
    file_path = os.path.join(parent_directory, 'config.ini')

    with open(file_path) as f:
        config = configparser.ConfigParser()
        config.read_file(f)

        session = requests.Session()

        twitch_data = get_twitch_data(config=config, session=session)

        return twitch_data

if __name__ == '__main__':
    data()
