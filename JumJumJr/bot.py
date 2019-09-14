import requests;
import configparser;
import json;
import csv;
import os;

if __name__ == '__main__':
    ## No point in running if it's missing the damn config.ini file...
    if not os.path.exists('../config.ini'):
        exit();

    ## Get Config info
    with open("../config.ini") as f:
        config = configparser.ConfigParser();
        config.read_file(f);

    ## API to get the current stream information
    URL = "https://api.twitch.tv/helix/streams?user_login=" + config['TwitchStream']['Name'];
    
    ## User-agent information
    headers = {'Client-ID':config['TwitchAuth']['ClientID']};

    print(headers);

    ## Base URL's
    game_URL = "https://api.twitch.tv/helix/games?id=";
    host_URL = "https://tmi.twitch.tv/hosts?include_logins=1&host="
    path_status = '../status/status.txt';

    ## Execution of GET call to Twitch
    response = requests.get(URL, headers=headers);
    json_data = json.loads(response.text);

    ## Deletes old status file so it can write a new one if need be
    if os.path.exists(path_status):
        os.remove(path_status);

    ## First will attempt to get his live data
    try:
        game_URL = game_URL + str(json_data['data'][0]['game_id']);
        response_game = requests.get(game_URL, headers=headers);
        game_json_data = json.loads(response_game.text);
        game = game_json_data['data'][0]['name'];
        viewer_count = json_data['data'][0]['viewer_count'];
        ## We now have the game he is playing and the viewer count of it.
        f = open(path_status, 'w');
        f.write("Status:Live\n");
        f.write("Game:" + game + "\n");
        f.write("Viewer_Count:" + str(viewer_count) + "\n");
        f.close();
        
    # Exception will occur if he is offline
    # Will now check if he is hosting
    except:
        try:
            ## Foreign API used to obtain hosting information
            host_URL = host_URL + str(json_data['data'][0]['id']);
            response_host = requests.get(host_URL);
            host_json_data = json.loads(response_host.text);
            target = host_json_data['hosts'][0]['target_login'];
            ## We now have the name of the streamer he is hosting.
            f = open(path_status, 'w');
            f.write("Status:Hosting\n");
            f.write("Hosting:" + target);
            f.close();
        ## An error here means Projared is asleep :)
        except:
            f = open(path_status, 'w');
            f.write("Status:asleep");
            f.close();
