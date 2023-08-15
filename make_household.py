import random

import pandas as pd
import requests
import yaml
from faker import Faker
from tqdm import tqdm

import household
from sql_helpers import create_connection

# Get config details

Faker.seed(0)
fake = Faker(['en-GB'])

with open("config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
DATABASE = cfg["database"]["db"]
GENERAL_TABLE = cfg["database"]["general_table"]
PEOPLE_TABLE = cfg["database"]["people_table"]
IF_EXISTS = cfg["database"]["if_exists"]
TOTAL_RECORDS = cfg["total_records"]


def two_or_three_and_more_children():
    children = random.choices([2, 3], weights=[75, 25])
    return children


def dep_children():
    children = random.choices([1, 2, 3], weights=[38, 46, 15])
    return children


def gender():
    gender = random.choices(["Male", "Female"], weights=[9767, 10000])
    return gender


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
    "cd_lau2",
    'IMD_2019',
    'household_type',
    'adults_total',
    'adults_over65',
    'adult_m',
    'adult_f',
    'married',
    'children_total',
    'non_dep'])


def create_house():
    return res, adults_total, adults_over65, adult_m, adult_f, married, children_total, non_dep


df_postcodelist = pd.read_csv('/home/chris/projects/myworld-1/appropriate_postcodes_sample.csv')
print("==============================")
print("Total Records = ", len(df_postcodelist))
print("==============================")

for i in tqdm(range(0, len(df_postcodelist))):
    to_lookup = df_postcodelist.iat[i, 0].replace(' ', '')
    print(to_lookup)
    r = requests.get('http://localhost:8000/postcodes/' + to_lookup)
    if r.status_code == 200:
        data = r.json()
    else:
        print(r.status_code)
        continue

    df._set_value(i, 'My_World_premise_UUID', fake.uuid4())
    df._set_value(i, 'postcode', data['result']['postcode'])
    df._set_value(i, 'quality', data['result']['quality'])
    df._set_value(i, 'eastings', data['result']['eastings'])
    df._set_value(i, 'northings', data['result']['northings'])
    df._set_value(i, 'country', data['result']['country'])
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

    res = household.household()[0]

    if res == "One person household: Aged 65 and over":
        adults_total = 0
        adults_over65 = 1
        if gender() == 'Male':
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = 0
        non_dep = 0

    if res == "One person household: Other":
        adults_total = 1
        adults_over65 = 0
        if gender == 'Male':
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = 0
        non_dep = 0

    if res == "One family only: All aged 65 and over":
        adults_total = 0
        adults_over65 = 2
        adult_m = 1
        adult_f = 1
        married = True
        children_total = 0
        non_dep = 0

    if res == "One family only: Married couple: No children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = True
        children_total = 0
        non_dep = 0

    if res == "One family only: Married couple: One dependent child":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = True
        children_total = 1
        non_dep = 0

    if res == "One family only: Married couple: Two or more dependent children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = True
        if two_or_three_and_more_children()[0] > 2:
            children_total = 3
        else:
            children_total = 2
        non_dep = 0

    if res == "One family only: Married couple: All children non-dependent":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = True
        children_total = 0
        non_dep = dep_children()[0]

    if res == "One family only: Same-sex civil partnership couple: No children":
        adults_total = 2
        adults_over65 = 0
        mm_or_ff = gender()
        if mm_or_ff == 'Male':
            adult_m = 2
            adult_f = 0
        else:
            adult_f = 2
            adult_m = 0
        married = False
        children_total = 0
        non_dep = 0

    if res == "One family only: Same-sex civil partnership couple: One dependent child":
        adults_total = 2
        adults_over65 = 0
        mm_or_ff = gender()
        if mm_or_ff == 'Male':
            adult_m = 2
            adult_f = 0
        else:
            adult_f = 2
            adult_m = 0
        married = False
        children_total = 1
        non_dep = 0

    if res == "One family only: Same-sex civil partnership couple: Two or more dependent children":
        adults_total = 2
        adults_over65 = 0
        mm_or_ff = gender()
        if mm_or_ff == 'Male':
            adult_m = 2
            adult_f = 0
        else:
            adult_f = 2
            adult_m = 0
        married = False
        if two_or_three_and_more_children()[0] > 2:
            children_total = 3
        else:
            children_total = 2
        non_dep = 0

    if res == "One family only: Same-sex civil partnership couple: All children non-dependent":
        adults_total = 2
        adults_over65 = 0
        mm_or_ff = gender()
        if mm_or_ff == 'Male':
            adult_m = 2
            adult_f = 0
        else:
            adult_f = 2
            adult_m = 0
        married = False
        children_total = 0
        non_dep = dep_children()[0]

    if res == "One family only: Cohabiting couple: No children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = False
        children_total = 0
        non_dep = 0

    if res == "One family only: Cohabiting couple: One dependent child":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = False
        children_total = 1
        non_dep = 0

    if res == "One family only: Cohabiting couple: Two or more dependent children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = False
        if two_or_three_and_more_children()[0] > 2:
            children_total = 3
        else:
            children_total = 2
        non_dep = 0

    if res == "One family only: Cohabiting couple: All children non-dependent":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = False
        children_total = 0
        non_dep = dep_children()[0]

    if res == "One family only: Lone parent: One dependent child":
        adults_total = 1
        adults_over65 = 0
        if gender() == 'Male':
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = 1
        non_dep = 0

    if res == "One family only: Lone parent: Two or more dependent children":
        adults_total = 1
        adults_over65 = 0
        if gender() == 'Male':
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        if two_or_three_and_more_children()[0] > 2:
            children_total = 3
        else:
            children_total = 2
        non_dep = 0

    if res == "One family only: Lone parent: All children non-dependent":
        adults_total = 1
        adults_over65 = 0
        if gender() == 'Male':
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = 0
        non_dep = dep_children()[0]

    if res == "Other household types: With one dependent child":
        print("edge case")
        continue

    if res == "Other household types: With two or more dependent children":
        print("edge case")
        continue

    if res == "Other household types: All full-time students":
        adults_total = 4
        adults_over65 = 0
        adult_m = 2
        adult_f = 2
        married = False
        children_total = 0
        non_dep = 0
        print("edge case")

    if res == "Other household types: All aged 65 and over":
        adults_total = 0
        adults_over65 = 3
        adult_m = 0
        adult_f = 0
        married = False
        children_total = 0
        non_dep = 0
        print("edge case")

    if res == "Other household types: Other":
        print("edge case")
        continue

    df._set_value(i, 'household_type', res)
    df._set_value(i, 'adults_total', adults_total)
    df._set_value(i, 'adults_over65', adults_over65)
    df._set_value(i, 'adult_m', adult_m)
    df._set_value(i, 'adult_f', adult_f)
    df._set_value(i, 'married', married)
    df._set_value(i, 'children_total', children_total)
    df._set_value(i, 'non_dep', non_dep)

    print(res, adults_total, adults_over65, adult_m, adult_f, married, children_total, non_dep)

df.dropna(axis=0, how='all', inplace=True)

df.to_sql(GENERAL_TABLE, conn1, if_exists=IF_EXISTS, index=False)
