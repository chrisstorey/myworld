#!/usr/bin/env python3
# System imports
import sys
from datetime import datetime
import time
import sqlite3
from _sqlite3 import IntegrityError

# Third party imports
import pandas as pd 
import requests
import yaml
from tqdm import tqdm

# Local Modules
from sql_helpers import create_connection, update_outcode, update_admin_district

with open("de_dup_config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
DATABASE = cfg["database"]["db"]
GENERAL_TABLE = cfg["database"]["general_table"]

# main function
conn1 = create_connection(DATABASE)
data2 = pd.read_sql_query("""SELECT * from """ + GENERAL_TABLE + """ where admin_district is NULL """,conn1)
print("Length of dataframe : ",len(data2))
MISSED = 0
for i in tqdm(range(len(data2))):
    #time.sleep(0.1)
    if data2['latitude'][i] == None:
        update_admin_district(conn1, GENERAL_TABLE, ("no location - no coordinates (lat)", data2['id'][i]))
        continue
    if data2['longitude'][i] == None:
        update_admin_district(conn1, GENERAL_TABLE, ("no location - no coordinates (lon)", data2['id'][i]))
        continue
    payload = {'lat': data2['latitude'][i], 'lon': data2['longitude'][i],'radius': 2000}
    #print(i, "   ",data2['latitude'][i], data2['longitude'][i])
    r = requests.get('http://localhost:8000/postcodes', params=payload)
    data = r.json()
    if data['status'] == 400:
        update_admin_district(conn1, GENERAL_TABLE, ("no location - no coordinates (400)", data2['id'][i]))
        continue
#    print(data)
    if data['result'] == None:
        MISSED = MISSED + 1
    #    print("=================================== MISSED: ", MISSED, "so far")
        update_admin_district(conn1, GENERAL_TABLE, ("no location - missed", data2['id'][i]))
        continue
       
    data2['outcode'][i] = data['result'][0]['outcode']
    data2['admin_district'][i] = data['result'][0]['admin_district']
    update_outcode(conn1, GENERAL_TABLE, (data2['outcode'][i], data2['id'][i]))
    update_admin_district(conn1, GENERAL_TABLE, (data2['admin_district'][i], data2['id'][i]))
