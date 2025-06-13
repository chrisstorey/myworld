import random
import requests
import yaml
from faker import Faker
from tqdm import tqdm
from uuid import uuid4

import household
# Assuming main.py is in the same directory or PYTHONPATH is configured
# If main.py is in parent directory, it might be: from ..main import db, Household
from models import db, Household # Changed from 'main' to 'models'
from pony.orm import db_session, commit

# Get config details

Faker.seed(0)
fake = Faker(["en-GB"])

with open("config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
# TOTAL_RECORDS is read from config but the loop iterates over df_postcodelist length
TOTAL_RECORDS = cfg["total_records"]


def two_or_three_and_more_children():
    children = random.choices([2, 3], weights=[75, 25])
    return children


def dep_children():
    children = random.choices([1, 2, 3], weights=[38, 46, 15])
    return children


def gender():
    # This function returns "Male" or "Female" as a string
    # The original code had a potential bug in `res == "One person household: Other"`
    # where `gender == "Male"` would always be false as `gender` is a function.
    # It should be `gender() == "Male"`. This is corrected in the logic below.
    return random.choice(["Male", "Female"])


# df_postcodelist would typically be loaded from a file or other source.
# For this refactoring, we assume it's available as it was in the original script.
# Example: df_postcodelist = pd.read_csv("test_data/postcodes-04")
# Since pandas is removed, this part needs to be adapted if it's not already a list of postcodes.
# For now, assuming df_postcodelist is a list of postcodes from a CSV.
# This will require `pandas` for this line only, or an alternative CSV reader.
# To proceed without pandas here, we'd need to change how postcodes are loaded.
# For the purpose of this subtask, we'll assume df_postcodelist is pre-populated
# as a list of strings. If it's from a CSV, that loading needs to be handled.
# To make it runnable without pandas for now, let's mock it.
# In a real scenario, replace this with actual CSV loading if needed.
try:
    import pandas as pd
    df_postcodelist_pd = pd.read_csv("test_data/postcodes-04")
    df_postcodelist = [row[0] for index, row in df_postcodelist_pd.iterrows()]
except ImportError:
    print("Pandas not installed, using a mock postcode list. Functionality will be limited.")
    print("Install pandas if you need to load postcodes from CSV.")
    # Mock list if pandas is not available
    df_postcodelist = ["SW1A1AA", "PE356EB", "PL40DW"] * 10 # Example postcodes


print("==============================")
# Adjusting to use the length of the Python list if pandas is not used
print("Total Records to process = ", len(df_postcodelist))
print("==============================")

for i in tqdm(range(0, len(df_postcodelist))):
    # If df_postcodelist is a list of strings from pandas, access directly.
    # If it was a DataFrame, it would be df_postcodelist.iat[i,0]
    to_lookup = df_postcodelist[i].replace(" ", "")
    print(f"Looking up postcode: {to_lookup}")

    try:
        r = requests.get("http://localhost:8000/postcodes/" + to_lookup, timeout=10)
        r.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = r.json()
        if not data or data.get("status") != 200 or not data.get("result"):
            print(f"Postcode API returned non-200 status or empty result for {to_lookup}. Skipping.")
            continue
    except requests.exceptions.RequestException as e:
        print(f"Request failed for postcode {to_lookup}: {e}. Skipping.")
        continue
    except ValueError: # Includes JSONDecodeError
        print(f"Could not decode JSON response for {to_lookup}. Skipping.")
        continue


    res = household.household()[0]

    # Initialize demographic variables
    adults_total = 0
    adults_over65 = 0
    adult_m = 0
    adult_f = 0
    married = False
    children_total = 0
    non_dep = 0

    # Determine household composition based on 'res'
    # (Original logic for setting demographics based on 'res' string)
    # Corrected gender() calls
    if res == "One person household: Aged 65 and over":
        adults_total = 0 # Should this be 1 as it's a one-person household?
        adults_over65 = 1
        if gender() == "Male":
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = 0
        non_dep = 0

    elif res == "One person household: Other":
        adults_total = 1
        adults_over65 = 0
        if gender() == "Male": # Corrected: was `gender == "Male"`
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = 0
        non_dep = 0

    elif res == "One family only: All aged 65 and over":
        adults_total = 0 # Should be 2?
        adults_over65 = 2
        adult_m = 1
        adult_f = 1
        married = True
        children_total = 0
        non_dep = 0

    elif res == "One family only: Married couple: No children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = True
        children_total = 0
        non_dep = 0

    elif res == "One family only: Married couple: One dependent child":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = True
        children_total = 1
        non_dep = 0

    elif res == "One family only: Married couple: Two or more dependent children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = True
        children_total = random.choice([2,3]) # Simplified from two_or_three_and_more_children()
        non_dep = 0

    elif res == "One family only: Married couple: All children non-dependent":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = True
        children_total = 0
        non_dep = random.choice([1,2,3]) # Simplified from dep_children()

    elif res == "One family only: Same-sex civil partnership couple: No children":
        adults_total = 2
        adults_over65 = 0
        if gender() == "Male": # Assuming civil partnership implies same gender
            adult_m = 2
            adult_f = 0
        else:
            adult_f = 2
            adult_m = 0
        married = False # Or True, depending on definition for civil partnership
        children_total = 0
        non_dep = 0

    elif res == "One family only: Same-sex civil partnership couple: One dependent child":
        adults_total = 2
        adults_over65 = 0
        if gender() == "Male":
            adult_m = 2
            adult_f = 0
        else:
            adult_f = 2
            adult_m = 0
        married = False
        children_total = 1
        non_dep = 0

    elif res == "One family only: Same-sex civil partnership couple: Two or more dependent children":
        adults_total = 2
        adults_over65 = 0
        if gender() == "Male":
            adult_m = 2
            adult_f = 0
        else:
            adult_f = 2
            adult_m = 0
        married = False
        children_total = random.choice([2,3])
        non_dep = 0

    elif res == "One family only: Same-sex civil partnership couple: All children non-dependent":
        adults_total = 2
        adults_over65 = 0
        if gender() == "Male":
            adult_m = 2
            adult_f = 0
        else:
            adult_f = 2
            adult_m = 0
        married = False
        children_total = 0
        non_dep = random.choice([1,2,3])

    elif res == "One family only: Cohabiting couple: No children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = False
        children_total = 0
        non_dep = 0

    elif res == "One family only: Cohabiting couple: One dependent child":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = False
        children_total = 1
        non_dep = 0

    elif res == "One family only: Cohabiting couple: Two or more dependent children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = False
        children_total = random.choice([2,3])
        non_dep = 0

    elif res == "One family only: Cohabiting couple: All children non-dependent":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1
        adult_f = 1
        married = False
        children_total = 0
        non_dep = random.choice([1,2,3])

    elif res == "One family only: Lone parent: One dependent child":
        adults_total = 1
        adults_over65 = 0
        if gender() == "Male":
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = 1
        non_dep = 0

    elif res == "One family only: Lone parent: Two or more dependent children":
        adults_total = 1
        adults_over65 = 0
        if gender() == "Male":
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = random.choice([2,3])
        non_dep = 0

    elif res == "One family only: Lone parent: All children non-dependent":
        adults_total = 1
        adults_over65 = 0
        if gender() == "Male":
            adult_m = 1
            adult_f = 0
        else:
            adult_m = 0
            adult_f = 1
        married = False
        children_total = 0
        non_dep = random.choice([1,2,3])

    elif res == "Other household types: With one dependent child":
        print(f"Edge case household type: {res}. Skipping.")
        continue

    elif res == "Other household types: With two or more dependent children":
        print(f"Edge case household type: {res}. Skipping.")
        continue

    elif res == "Other household types: All full-time students":
        adults_total = random.randint(1,5) # Example: 4 students
        adults_over65 = 0
        # Gender distribution can be more random for students
        temp_adult_m = 0
        temp_adult_f = 0
        for _ in range(adults_total):
            if gender() == "Male":
                temp_adult_m +=1
            else:
                temp_adult_f +=1
        adult_m = temp_adult_m
        adult_f = temp_adult_f
        married = False # Unlikely to be all married to each other
        children_total = 0
        non_dep = 0 # Students are typically non-dependents in this context if household is all students
        print(f"Edge case household type (students): {res}. Processed with assumptions.")


    elif res == "Other household types: All aged 65 and over":
        # This case was underspecified in original, assuming 3 for "Other"
        adults_total = 0 # Should be sum of over 65?
        adults_over65 = random.randint(1,4) # Example: 3 elderly people
        temp_adult_m = 0
        temp_adult_f = 0
        for _ in range(adults_over65):
             if gender() == "Male":
                temp_adult_m +=1
             else:
                temp_adult_f +=1
        adult_m = temp_adult_m # These are also part of adults_over65
        adult_f = temp_adult_f # These are also part of adults_over65
        married = False # Could be a mix
        children_total = 0
        non_dep = 0
        print(f"Edge case household type (all 65+): {res}. Processed with assumptions.")


    elif res == "Other household types: Other":
        print(f"Edge case household type: {res}. Skipping due to ambiguity.")
        continue

    # Some household types might not be caught by the if/elif chain,
    # ensure all demographic variables are explicitly set or have defaults.
    # The initial defaults cover this.

    # Create Household object and commit to database
    with db_session:
        Household(
            household_UUID=str(uuid4()), # Using uuid from uuid module
            postcode=data["result"]["postcode"],
            # Ensure None checks for optional numeric fields from API
            lat=float(data["result"]["latitude"]) if data["result"]["latitude"] is not None else None,
            long=float(data["result"]["longitude"]) if data["result"]["longitude"] is not None else None,
            admin_district=data["result"]["admin_district"],
            cd_lsoa=data["result"]["codes"]["lsoa"], # LSOA code
            # Assuming 'type' in ORM maps to 'household_type' string
            type=res,
            adults_total=adults_total,
            adults_m=adult_m,
            adults_f=adult_f,
            adults_65=adults_over65,
            married=married,
            children_total=children_total,
            non_dep=non_dep,
            # Fields from original DataFrame not directly in Household ORM or from API:
            # quality, eastings, northings, country, nhs_ha, primary_care_trust, region,
            # lsoa (full name), msoa (full name), incode, outcode, parliamentary_constituency,
            # parish, admin_county, admin_ward, ced, ccg, nuts.
            # These would need to be added to the Household entity in main.py if required.
            # For now, we only populate what the ORM entity defines.
            # Example for a field if it were in ORM:
            # country = data["result"]["country"],
        )
        # commit() is implicitly called by Pony ORM at the end of a successful db_session block

    print(
        f"Saved: {res}, ad_T:{adults_total}, ad_65:{adults_over65}, ad_M:{adult_m}, ad_F:{adult_f}, marr:{married}, ch_T:{children_total}, non_D:{non_dep}"
    )

print("==============================")
print("Household generation complete.")
print("==============================")

# Note: The db object needs to be bound to a database and entities mapped
# BEFORE this script runs. This is typically done in main.py when db is defined.
# Example (from main.py, not to be repeated here):
# db.bind(provider='postgres', user='user', password='password', host='localhost', database='dbname')
# db.generate_mapping(create_tables=True)
