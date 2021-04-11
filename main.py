import numpy as np
import pandas as pd
import requests
import yaml
from faker import Faker
from tqdm import tqdm

from sql_helpers import create_connection

# Get config details

Faker.seed(0)
fake = Faker(['en-GB'])

with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
DATABASE = cfg["database"]["db"]
GENERAL_TABLE = cfg["database"]["general_table"]
IF_EXISTS = cfg["database"]["if_exists"]
TOTAL_RECORDS = cfg["total_records"]

# Create DB connection
conn1 = create_connection(DATABASE)

df = pd.DataFrame(index=range(0, TOTAL_RECORDS), columns=[
    'My_World_premise_UUID',
    "postcode",
    "quality",
    "eastings",
    "northings",
    "country",
    "nhs_ha",
    "longitude",
    "latitude",
    "primary_care_trust",
    "region",
    "lsoa",
    "msoa",
    "incode",
    "outcode",
    "parliamentary_constituency",
    "admin_district",
    "parish",
    "admin_county",
    "admin_ward",
    "ced",
    "ccg",
    "nuts",
    "cd_admin_district",
    "cd_admin_county",
    "cd_admin_ward",
    "cd_parish",
    "cd_parliamentary_constituency",
    "cd_ccg",
    "cd_ccg_id",
    "cd_ced",
    "cd_nuts",
    "cd_lsoa",
    "cd_msoa",
    "cd_lau2"])

for i in tqdm(np.arange(0, TOTAL_RECORDS)):
    r = requests.get('http://localhost:8000/random/postcodes')
    data = r.json()
    df._set_value(i,'My_World_premise_UUID', fake.uuid4())
    df._set_value(i,'postcode', data['result']['postcode'])
    df._set_value(i,'quality', data['result']['quality'])
    df._set_value(i,'eastings', data['result']['eastings'])
    df._set_value(i,'northings', data['result']['northings'])
    df._set_value(i,'country', data['result']['country'])
    df._set_value(i, 'nhs_ha', data['result']['nhs_ha'])
    df._set_value(i, 'longitude', data['result']['longitude'])
    df._set_value(i, 'latitude', data['result']['latitude'])
    df._set_value(i, 'primary_care_trust', data['result']['primary_care_trust'])
    df._set_value(i, 'region', data['result']['region'])
    df._set_value(i, 'lsoa', data['result']['lsoa'])
    df._set_value(i, 'msoa', data['result']['msoa'])
    df._set_value(i, 'incode', data['result']['incode'])
    df._set_value(i, 'outcode', data['result']['outcode'])
    df._set_value(i, 'parliamentary_constituency', data['result']['parliamentary_constituency'])
    df._set_value(i, 'admin_district', data['result']['admin_district'])
    df._set_value(i, 'parish', data['result']['parish'])
    df._set_value(i, 'admin_county', data['result']['admin_county'])
    df._set_value(i, 'admin_ward', data['result']['admin_ward'])
    df._set_value(i, 'ced', data['result']['ced'])
    df._set_value(i, 'ccg', data['result']['ccg'])
    df._set_value(i, 'nuts', data['result']['nuts'])
    df._set_value(i, 'cd_admin_district', data['result']['codes']['admin_district'])
    df._set_value(i, 'cd_admin_county', data['result']['codes']['admin_county'])
    df._set_value(i, 'cd_admin_ward', data['result']['codes']['admin_ward'])
    df._set_value(i, 'cd_parish', data['result']['codes']['parish'])
    df._set_value(i, 'cd_parliamentary_constituency', data['result']['codes']['parliamentary_constituency'])
    df._set_value(i, 'cd_ccg', data['result']['codes']['ccg'])
    df._set_value(i, 'cd_ccg_id', data['result']['codes']['ccg_id'])
    df._set_value(i, 'cd_ced', data['result']['codes']['ced'])
    df._set_value(i, 'cd_nuts', data['result']['codes']['nuts'])
    df._set_value(i, 'cd_lsoa', data['result']['codes']['lsoa'])
    df._set_value(i, 'cd_msoa', data['result']['codes']['msoa'])
    df._set_value(i, 'cd_lau2', data['result']['codes']['lau2'])

df.to_sql(GENERAL_TABLE,conn1,if_exists=IF_EXISTS,index=False)


