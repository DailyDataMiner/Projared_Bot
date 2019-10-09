import configparser
import os
import json
import logging
from pathlib import Path
import sys

from JumJumJr import jumjumjr
from Diath import diath

def create_paths():

    ## Log Directory & File
    log_dir = Path.cwd() / 'logs'
    log_path = Path.cwd() / 'logs' / 'log.txt'
    os.makedirs(log_dir, exist_ok=True)

    ### No point in hosting this if the widget is just overwritten
    ## Status Directory & File
    # status_dir = Path.cwd() / 'status'
    # status_path = Path.cwd() / 'status' / 'status.json'
    # os.makedirs(status_dir, exist_ok=True)
    # return log_path, status_path

    return log_path

def read_previous_status(status_path):
    try:
        text_data = status_path.read_text()
        json_data = json.loads(text_data)

        return json_data
    except FileNotFoundError:
        ## If no file present, create one with default values.
        json_data = {'status': 'Offline'}
        text_data = json.dumps(json_data)
        status_path.write_text(text_data)
        return

def update_status(status_path, twitch_data):
    text_data = json.dumps(twitch_data)
    status_path.write_text(text_data)
    return

## Was used for thread purposes, but now not needed
# def compare_status(current_data, prev_data):
#     ## Need to worry about where the widget comes in 

#     if current_data['status'] == 'Offline' and prev_data['status'] == 'Offline' or current_data['status'] == 'Online' and prev_data['status'] == 'Online':
#         return diath.check()
#     elif current_data['status'] == 'Offline' and prev_data['status'] == 'Online':
#         # We need to check the latest post and ensure that he didn't go momentarily offline
#         return 1
#     elif current_data['status'] == 'Online' and prev_data['status'] == 'Offline':
#         # I dunno
#         return 2
#     else:
#         return 4

if __name__ == '__main__':
    log_path = create_paths()
    logging.FileHandler(filename=log_path, mode='a', encoding=None, delay=False)
    logging.basicConfig(filename=log_path, format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info('Starting script in ' + os.path.basename(__file__))

    ## Was used for comparing old vs new data, but the widget won't care about this.
    # current_twitch_data = jumjumjr.data()

    # prev_twitch_data = read_previous_status(status_path)

    # Should return back as 200
    status = diath.reddit_call(jumjumjr.data())

    if status != 200:
        logging.error('Issue occurred when making requests to reddit')

    ## Not needing this anymore
    # update_status(status_path, current_twitch_data)
    logging.info('Exiting ' + os.path.basename(__file__))

    logging.info('End of script.\n')
