import numpy as np
import pandas as pd
from tqdm import tqdm
import random
import sqlite3


def update_admin_district(conn,table,job):
    """
    update description
    :param conn:
    :table:
    :job
        :admin_district
        :id
    """
    sql = ''' UPDATE ''' + table + ''' SET admin_district = ? WHERE id = ? '''
    cur = conn.cursor()
    cur.execute(sql, job)
    conn.commit()



con = sqlite3.connect("data/household_composition.db")
areadata = pd.read_sql_query("SELECT * from area_totals",con)
print("Area total dataframe is : ",len(areadata), " records")

probabilitydata =  pd.read_sql_query("SELECT * from probability_data",con)
print("probability data dataframe is : ",len(probabilitydata), " records")

for index in probabilitydata.iterrows():
    print(probabilitydata['prob'][index])
    # print(areadata.query('geogcode == i["geogcode"]')['value'])
    # print(areadata['value'].where(areadata['geogcode'] == i['geogcode']))
    # probabilitydata['prob'][row] = probabilitydata['value'][row]/areadata.loc[areadata['value'] == probabilitydata['value'][row]]
    # print(row, probabilitydata['prob'][row])
