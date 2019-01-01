#!/usr/bin/env python3
'''Label all unnamed nodes with an underscore + number.
'''

import argparse
import re
import sys
import os
import logging

top_level = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir)

sys.path.append(os.path.abspath(os.path.join(top_level, "models")))
from _OZglobals import src_flags, eol_inspect_via_flags, image_status_labels

default_appconfig_file = default_appconfig_file = "private/appconfig.ini"
parser = argparse.ArgumentParser(description='Transfer to new EoL V3')

args = parser.parse_args()

with open(os.path.join(top_level, default_appconfig_file)) as conf:
    conf_type=None
    for line in conf:
    #look for [db] line, followed by uri
        m = re.match(r'\[([^]]+)\]', line)
        if m:
            conf_type = m.group(1)
        if conf_type == 'db':
            m = re.match('uri\s*=\s*(\S+)', line)
            if m:
                args.database = m.group(1)
        elif conf_type == 'api':
            m = re.match('eol_api_key\s*=\s*(\S+)', line)
            if m:
                args.EOL_API_key = m.group(1)
            
if args.database.startswith("sqlite://"):
    from sqlite3 import dbapi2 as sqlite
    db_connection = sqlite.connect(os.path.relpath(args.database[len("sqlite://"):], args.treedir))
    datetime_now = "datetime('now')";
    subs="?"
    
elif args.database.startswith("mysql://"): #mysql://<mysql_user>:<mysql_password>@localhost/<mysql_database>
    import pymysql
    match = re.match(r'mysql://([^:]+):([^@]*)@([^/]+)/([^?]*)', args.database.strip())
    if match.group(2) == '':
        #enter password on the command line, if not given (more secure)
        if args.script:
            pw = input("pw: ")
        else:
            from getpass import getpass
            pw = getpass("Enter the sql database password: ")
    else:
        pw = match.group(2)
    db_connection = pymysql.connect(user=match.group(1), passwd=pw, host=match.group(3), db=match.group(4), port=3306, charset='utf8mb4')
    datetime_now = "NOW()"
    diff_minutes=lambda a,b: 'TIMESTAMPDIFF(MINUTE,{},{})'.format(a,b)
    subs="%s"



db_curs = db_connection.cursor()
#db_curs.execute("UPDATE images_by_ott SET src={} WHERE src=2".format(src_flags['eol_old']))
db_connection.commit()
db_curs.close()

pic_path = os.path.join(top_level, "static/FinalOutputs/pics")
img_path = os.path.join(top_level, "static/FinalOutputs/img/{}".format(src_flags['eol_old']))
#os.mkdir(img_path)

"""db_curs = db_connection.cursor()
batch_size = 200
db_curs.execute("SELECT src_id FROM images_by_ott WHERE src={}".format(src_flags['eol_old']))
while True:
    #get the rows in batches
    rows = db_curs.fetchmany(batch_size)
    if not rows:
        break
    for row in rows:
        src_id = str(row[0])
        subdir = os.path.join(img_path, src_id[-3:])
        os.makedirs(subdir, exist_ok=True)
        f = os.path.join(pic_path, src_id+".jpg")
        if os.path.isfile(f):
            os.rename(f, os.path.join(subdir, src_id+".jpg"))
db_curs.close()
"""

db_curs = db_connection.cursor()
sql = "UPDATE images_by_ott SET src={}, src_id=-src_id WHERE src=1 AND src_id < 0".format(src_flags['onezoom_bespoke'])
db_curs.execute(sql)
db_connection.commit()
db_curs.close()

img_path = os.path.join(top_level, "static/FinalOutputs/img/{}".format(src_flags['onezoom_bespoke']))
db_curs = db_connection.cursor()
batch_size = 200
db_curs.execute("SELECT src_id FROM images_by_ott WHERE src={}".format(src_flags['onezoom_bespoke']))
while True:
    #get the rows in batches
    rows = db_curs.fetchmany(batch_size)
    if not rows:
        break
    for row in rows:
        src_id = str(row[0])
        subdir = os.path.join(img_path, src_id[-3:])
        os.makedirs(subdir, exist_ok=True)
        f = os.path.join(pic_path, '-' + src_id+".jpg")
        if os.path.isfile(f):
            os.rename(f, os.path.join(subdir, src_id+".jpg"))
db_curs.close()

