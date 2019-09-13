import datetime;
import os;

path_status = '../status/status.txt';
path_logs = '../logs/Nuptup ' + str(datetime.datetime.now()) + '.txt';

if os.path.exists(path_status):
    pass;
else:
    f = open(path_logs, 'w');
    f.write("Error: Status file not found!");
    f.close();
