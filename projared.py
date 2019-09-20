import os;
import json;
import logging;
import sys;

from JumJumJr import jumjumjr;

def current_directory():
    return os.path.dirname(__file__);

def log_validation():

    ## Log Directory & File
    log_dir = os.path.join(current_directory(), 'logs');
    log_path = os.path.join(log_dir, 'log.txt');

    ## Whole process to ensure that logging is possible
    if not os.path.exists(log_path):
        if not os.path.exists(log_dir):
            os.mkdir(log_dir);
        with open(log_path, 'x') as f:
            f.write("Beginning of log file.\n");
        logging.basicConfig(filename=log_path,format='%(asctime)s - %(message)s', level=logging.DEBUG);
        logging.info("Created by " + os.path.basename(__file__));
    else:
        logging.basicConfig(filename=log_path,format='%(asctime)s - %(message)s', level=logging.DEBUG);

    return;

def status_validation(twitch_data):

    ## Status Directory & File
    status_dir = os.path.join(current_directory(), 'status');
    status_path = os.path.join(status_dir, 'status.json');

    ## Whole process to ensure that status file is available
    if not os.path.exists(status_path):
        if not os.path.exists(status_dir):
            os.mkdir(status_dir);
            logging.info("Created status directory.");
        with open(status_path, 'x') as f:
            # Dumps latest Twitch API data into file
            # No point in continuing if that file was missing
            f.write(json.dumps(twitch_data));
        logging.info("Status file created. Stopping script prematurely.");
        sys.exit(0);
    else:
        with open(status_path, 'r') as f:
            try:
                prev = json.load(f);
            except:
                logging.info("Status file was unable to be read.");
        return prev;

def status_update(twitch_data):

    ## Status Directory & File
    status_dir = os.path.join(current_directory(), 'status');
    status_path = os.path.join(status_dir, 'status.json');
    
    with open(status_path, 'w') as q:
        json.dump(twitch_data, q);
    return;

def main():

    ## Ensures log directory and file is present
    log_validation();

    logging.info("Starting script in " + os.path.basename(__file__));

    ## Grabs latest Twitch API data
    twitch_data = jumjumjr.data();

    ## Ensures status directory and file is present
    prev_data = status_validation(twitch_data);

    ## Just access keys directly and not loop through them
    if twitch_data['status'] == 'Offline' and prev_data['status'] == 'Offline':
        print("Do nothing!");
    elif twitch_data['status'] == 'Offline' and prev_data['status'] == 'Online':
        print("We're going live!");
    elif twitch_data['status'] == 'Online' and prev_data['status'] == 'Offline':
        print("He's done for the day");
    else:
        print("Probably hosting.");

    ## Updating status file with new data
    status_update(twitch_data);

    logging.info("Exiting " + os.path.basename(__file__));

    return;

if __name__ == '__main__':
    main();
    logging.info("End of script.\n");
