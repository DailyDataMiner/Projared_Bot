import os;
import json;
import logging;
from pathlib import Path
import sys;

from JumJumJr import jumjumjr;


def create_paths():

    ## Log Directory & File
    log_dir = Path.cwd() / "logs";
    log_path = Path.cwd() / "logs" / "log.txt";
    os.makedirs(log_dir, exist_ok=True);

    ## Status Directory & File
    status_dir = Path.cwd() / "status";
    status_path = Path.cwd() / "status" / "status.json";
    os.makedirs(status_dir, exist_ok=True);

    return log_path, status_path;


def read_previous_status(status_path):
    try:
        text_data = status_path.read_text();
        json_data = json.loads(text_data);

        return json_data
    except FileNotFoundError:
        ## If no file present, create one with default values.
        json_data = {"status": "Offline"};
        text_data = json.dumps(json_data);
        status_path.write_text(text_data);
        logging.info("Status file created. Stopping script prematurely.");
        sys.exit(0);


def update_status(status_path, twitch_data):
    text_data = json.dumps(twitch_data);
    status_path.write_text(text_data);
    return;


def compare_status(current_data, prev_data):
    ## Just access keys directly and not loop through them
    if current_data["status"] == "Offline" and prev_data["status"] == "Offline":
        print("Do nothing!");
    elif current_data["status"] == "Offline" and prev_data["status"] == "Online":
        print("We're going live!");
    elif current_data["status"] == "Online" and prev_data["status"] == "Offline":
        print("He's done for the day");
    else:
        print("Probably hosting.");
    return;


if __name__ == "__main__":
    log_path, status_path = create_paths();
    logging.FileHandler(filename=log_path, mode="a", encoding=None, delay=False);
    logging.basicConfig(filename=log_path, format="%(asctime)s - %(message)s", level=logging.INFO);
    logging.info("Starting script in " + os.path.basename(__file__));

    current_twitch_data = jumjumjr.data();
    prev_twitch_data = read_previous_status(status_path);

    update_status(status_path, current_twitch_data);
    compare_status(current_twitch_data, prev_twitch_data);
    logging.info("Exiting " + os.path.basename(__file__));

    logging.info("End of script.\n");
