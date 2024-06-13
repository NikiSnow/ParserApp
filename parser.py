import csv
import copy
import json
import glob
import sqlite3
import argparse
import datetime


FIELD_MAP = {
    '%h': 'ip',
    '%l': 'logname',
    '%u': 'user',
    '%t': ('time', 'timezone'),
    '%r': 'request',
    '%>s': 'status',
    '%b': 'size',
}
TABLE_NAME = 'accesslog'
CONFIG_DEFAULTS = {
    'file_glob': '*.log',
    'logformat': '%h %l %t "%r" %>s %b',
}


def parse_log(filename, field_names):
    res = []
    with open(filename) as fh:
        reader = csv.reader(fh, delimiter=' ')
        for record in reader:
            data = {}
            for name, item in zip(field_names, record):
                data[name] = item.strip('[]')
                if name == 'time':
                    data[name] = datetime.datetime.strptime(data[name], '%d/%b/%Y:%H:%M:%S')                
            res.append(data)    
    return res

def logformat2names(logformat):
    res = []
    for item in logformat.split():
        item = item.strip('"')
        field = FIELD_MAP.get(item, item)
        if isinstance(field, str):
            res.append(field)
        elif isinstance(field, tuple):
            res.extend(field)
    return res

def save2db(records, db_name, field_names):
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    try:
        cur.execute(f'DROP TABLE {TABLE_NAME}')
    except sqlite3.OperationalError:
        pass
    cur.execute(f'CREATE TABLE {TABLE_NAME} ({", ".join(field_names)})')
    data = []
    for rec in records:
        data.append(tuple(rec[name] for name in field_names))
    filler = ','.join(['?'] * len(field_names))                       
    cur.executemany(f'INSERT INTO {TABLE_NAME} VALUES({filler})', data)
    db.commit()
    db.close()


def select_from_db(db_name, field_names, ip=None, start_time=None, end_time=None):
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    cond = []
    if ip is not None:
        cond.append(f'ip = "{ip}"')
    if start_time is not None:
        cond.append(f'time >= "{start_time}"')
    if end_time:
        cond.append(f'time <= "{end_time}"')
    req_str = f'SELECT * FROM {TABLE_NAME}'
    if cond:
        req_str += ' WHERE ' + ' and '.join(cond)
    req = cur.execute(req_str) 
    res = []
    for rec in req.fetchall():
        res.append(dict(zip(field_names, rec)))
    return res


def print_result(data):
    print(json.dumps(data, indent=4))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=('parse', 'get'))
    parser.add_argument('-c', '--config', help='path to configuration file', default='parser.ini')
    parser.add_argument('-d', '--db', help='path to db file', default='parser.db')
    parser.add_argument('--ip', help='host ip filter (only for get command)')
    parser.add_argument('--start-time', help='start time (only for get command)', type=datetime.datetime.fromisoformat)
    parser.add_argument('--end-time', help='stop time (only for get command)', type=datetime.datetime.fromisoformat)
    return parser.parse_args()


def parse_config(config_path):
    config = copy.copy(CONFIG_DEFAULTS)
    with open(config_path) as fh:
        for line in fh:
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()
    return config

def main():
    args = parse_args()
    db_name = args.db
    config = parse_config(args.config)
    field_names = logformat2names(config['logformat'])
    if args.command == 'parse':
        records = []
        for filename in glob.glob(config['files_glob']):
            print('Parsing file', filename)
            records.extend(parse_log(filename, field_names))
        save2db(records, db_name, field_names)
    elif args.command == 'get':
        data = select_from_db(db_name, field_names, ip=args.ip, start_time=args.start_time, end_time=args.end_time)
        print_result(data)


if __name__ == '__main__':
    main()
