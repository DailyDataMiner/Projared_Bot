import configparser;
import json;
import logging;
import os;
import requests;

def get_twitch_data(session, config):

    headers = {'Client-ID': config['TwitchAuth']['ClientID']};
    params = {'user_login': config['TwitchStream']['Name']};

    ## Base URL's
    stream_URL = 'https://api.twitch.tv/helix/streams';
    game_URL = 'https://api.twitch.tv/helix/games';
    host_URL = 'https://tmi.twitch.tv/hosts?include_logins=1&host=';
    twitch_url = 'https://twitch.tv/';

    ## Execution of GET call to Twitch
    response = session.get(stream_URL, params=params, headers=headers);

    if response.status_code == 200:
        logging.info("Request successful.");
    else:
        logging.error("Request failed. %s", response.json());

    ## First will attempt to get his live data
    try:
        ## Retrieves value from first GET that will fail if he is not streaming
        viewer_count = response.json()['data'][0]['viewer_count'];
        
        ## Gets game ID and prepares the GET call to retrieve game information
        game_id = response.json()['data'][0]['game_id'];
        game_params = {'id': game_id};
        response_game = session.get(game_URL, params=game_params, headers=headers);

        ## Retrieves values of game
        game_name = response_game.json()['data'][0]['name'];
        box_art_url_template = response_game.json()['data'][0]['box_art_url']
        box_art_url = box_art_url_template.format(width=100, height=100)
        # We now have stream information
        twitch_data = {'status': 'Online',
                       'url': twitch_url + config['TwitchStream']['Name'],
                       'game_name': game_name,
                       'game_box_art': box_art_url,
                       'viewer_count': viewer_count};
        return twitch_data;

    # Exception will occur if he is not streaming
    # Will now check if he is hosting
    except (IndexError, KeyError):
        try:
            host_params = {'include_logins': '1',
                           'host': response.json['data'][0]['id']};
            ## Foreign API used to obtain hosting information
            response_host = requests.get(host_URL, params=host_params);
            target = response_host.json()['hosts'][0]['target_login'];
            ## We now have the name of the streamer he is hosting.
            twitch_data == {'status': 'Hosting',
                           'host': target,
                           'url': twitch_url + target};
            return twitch_data;


        ## An error here means Projared is asleep :)
        except:
            twitch_data = {'status': 'Offline'};
            return twitch_data;

def exe():

    current_directory = os.path.dirname(__file__);
    parent_directory = os.path.split(current_directory)[0]
    file_path = os.path.join(parent_directory, 'config.ini');

    with open(file_path) as f:
        config = configparser.ConfigParser()
        config.read_file(f)

        session = requests.Session();
        
        twitch_data = get_twitch_data(config=config, session=session);
        
        return twitch_data;
        
if __name__ == '__main__':
    exe();

