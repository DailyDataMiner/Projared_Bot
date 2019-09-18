import os;
import json;
import sys;

from JumJumJr import jumjumjr;

def main():

    # Converts dict to str
    twitch_data = jumjumjr.exe();
    json_data = json.dumps(twitch_data);

    # Sets up pathing for status file
    current_directory = os.path.dirname(__file__);
    status_dir = os.path.join(current_directory, 'status');

    # Basically will make sure the status directory exists
    try:
        os.mkdir(status_dir);
    except Exception:
        print("Already exists...");

    # Used for creating/writing to file
    file_path = status_dir = os.path.join(status_dir, 'status.json');
    
    if not os.path.exists(file_path):
        # Will happen on first run
        with open(file_path, 'x') as f:
            f.write(json_data);
            sys.exit(0);
    else:
        with open(file_path, 'r') as f:
            dict = json.load(f);
            d_items = dict.items();

    twitch_items = twitch_data.items();

    # Just access keys directly and not loop through them
    
    
if __name__ == '__main__':
    main();
