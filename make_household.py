import random
import requests
import yaml
from faker import Faker
from tqdm import tqdm
from uuid import uuid4

import household
from models import db, Household # Changed from 'main' to 'models'
from pony.orm import db_session # commit is implicitly handled by @db_session or with db_session

# Get config details

Faker.seed(0)
fake = Faker(["en-GB"]) # Used for postcode API in original, but not directly in household creation logic now

# Config loading (only TOTAL_RECORDS seems used by the main execution part, if at all)
with open("config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
TOTAL_RECORDS = cfg["total_records"]


# Helper functions for demographic choices - these could also be part of the new function or remain global
def two_or_three_and_more_children():
    # This function was returning a list, e.g. [2] or [3].
    # The logic using it expected an int: `if two_or_three_and_more_children()[0] > 2:`
    # Correcting it to return an int.
    return random.choices([2, 3], weights=[75, 25])[0]


def dep_children():
    # Similar correction as above.
    return random.choices([1, 2, 3], weights=[38, 46, 15])[0]


def gender():
    return random.choice(["Male", "Female"])


@db_session
def process_and_create_household_orm(postcode_to_lookup: str, api_result_data: dict, household_type_string: str) -> Household | None:
    """
    Processes API data and household type to determine demographics,
    then creates and commits a Household ORM object.
    Returns the Household object or None if skipped.
    """

    # Initialize demographic variables
    adults_total = 0
    adults_over65 = 0
    adult_m = 0
    adult_f = 0
    married = False
    children_total = 0
    non_dep = 0

    res = household_type_string # Use the passed household type string

    # Determine household composition based on 'res'
    if res == "One person household: Aged 65 and over":
        adults_total = 1 # Corrected: one person implies 1 adult total in this context
        adults_over65 = 1
        if gender() == "Male":
            adult_m = 1; adult_f = 0
        else:
            adult_m = 0; adult_f = 1
        # adults_total is sum of adults_m, adults_f, adults_over65 not fitting m/f counts
        # For "One person household: Aged 65 and over", adults_m/f should reflect the over65 person.
        # The original script had adults_total = 0 which was confusing.
        # Let's assume adults_m/f are for <65 unless the type implies only >65.
        # If the person is over 65, adults_m/f (working age) should be 0.
        # The ORM model has adults_total, adults_m, adults_f, adults_65.
        # For clarity: adults_m/f for <65, adults_65 for >=65. adults_total = m+f+others_not_in_m_f_65
        # Re-evaluating logic for counts:
        # If type is "One person household: Aged 65 and over":
        # adults_total = 1 (this field in ORM seems to be total adults <65 from make_people.py context)
        # So, if person is >65: adults_total should be 0 if it means <65.
        # The original script set adults_total = 0 for this case. And adults_m/f were set for the >65 person.
        # This is ambiguous. Let's stick to what make_people expects:
        # adults_m, adults_f are for working age adults. adults_65 for elderly.
        # So for "One person household: Aged 65 and over":
        adults_total = 0 # Meaning number of working age adults
        adults_over65 = 1
        # For the over-65 person, we don't set adults_m/f, make_people handles gender for over_65s
        adult_m = 0
        adult_f = 0
        married = False
        children_total = 0
        non_dep = 0


    elif res == "One person household: Other":
        adults_total = 1 # This means one working-age adult
        adults_over65 = 0
        if gender() == "Male":
            adult_m = 1; adult_f = 0
        else:
            adult_m = 0; adult_f = 1
        married = False
        children_total = 0
        non_dep = 0

    elif res == "One family only: All aged 65 and over":
        adults_total = 0 # No working age
        adults_over65 = 2 # Number of over 65 adults
        adult_m = 0 # No working age males
        adult_f = 0 # No working age females
        married = True # Assuming the two >65 are married
        children_total = 0
        non_dep = 0

    elif res == "One family only: Married couple: No children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1; adult_f = 1
        married = True
        children_total = 0
        non_dep = 0

    elif res == "One family only: Married couple: One dependent child":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1; adult_f = 1
        married = True
        children_total = 1
        non_dep = 0

    elif res == "One family only: Married couple: Two or more dependent children":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1; adult_f = 1
        married = True
        children_total = two_or_three_and_more_children() # Now returns int
        non_dep = 0

    elif res == "One family only: Married couple: All children non-dependent":
        adults_total = 2
        adults_over65 = 0
        adult_m = 1; adult_f = 1
        married = True
        children_total = 0 # Non-dependent children are not counted in children_total
        non_dep = dep_children() # Now returns int

    elif res == "One family only: Same-sex civil partnership couple: No children":
        adults_total = 2
        adults_over65 = 0
        if gender() == "Male": # Gender of the couple
            adult_m = 2; adult_f = 0
        else:
            adult_m = 0; adult_f = 2
        married = True # Civil partnership often treated as married for data
        children_total = 0
        non_dep = 0

    elif res == "One family only: Same-sex civil partnership couple: One dependent child":
        adults_total = 2; adults_over65 = 0
        if gender() == "Male": adult_m = 2; adult_f = 0
        else: adult_m = 0; adult_f = 2
        married = True; children_total = 1; non_dep = 0

    elif res == "One family only: Same-sex civil partnership couple: Two or more dependent children":
        adults_total = 2; adults_over65 = 0
        if gender() == "Male": adult_m = 2; adult_f = 0
        else: adult_m = 0; adult_f = 2
        married = True; children_total = two_or_three_and_more_children(); non_dep = 0

    elif res == "One family only: Same-sex civil partnership couple: All children non-dependent":
        adults_total = 2; adults_over65 = 0
        if gender() == "Male": adult_m = 2; adult_f = 0
        else: adult_m = 0; adult_f = 2
        married = True; children_total = 0; non_dep = dep_children()

    elif res == "One family only: Cohabiting couple: No children":
        adults_total = 2; adults_over65 = 0; adult_m = 1; adult_f = 1
        married = False; children_total = 0; non_dep = 0

    elif res == "One family only: Cohabiting couple: One dependent child":
        adults_total = 2; adults_over65 = 0; adult_m = 1; adult_f = 1
        married = False; children_total = 1; non_dep = 0

    elif res == "One family only: Cohabiting couple: Two or more dependent children":
        adults_total = 2; adults_over65 = 0; adult_m = 1; adult_f = 1
        married = False; children_total = two_or_three_and_more_children(); non_dep = 0

    elif res == "One family only: Cohabiting couple: All children non-dependent":
        adults_total = 2; adults_over65 = 0; adult_m = 1; adult_f = 1
        married = False; children_total = 0; non_dep = dep_children()

    elif res == "One family only: Lone parent: One dependent child":
        adults_total = 1; adults_over65 = 0
        if gender() == "Male": adult_m = 1; adult_f = 0
        else: adult_m = 0; adult_f = 1
        married = False; children_total = 1; non_dep = 0

    elif res == "One family only: Lone parent: Two or more dependent children":
        adults_total = 1; adults_over65 = 0
        if gender() == "Male": adult_m = 1; adult_f = 0
        else: adult_m = 0; adult_f = 1
        married = False; children_total = two_or_three_and_more_children(); non_dep = 0

    elif res == "One family only: Lone parent: All children non-dependent":
        adults_total = 1; adults_over65 = 0
        if gender() == "Male": adult_m = 1; adult_f = 0
        else: adult_m = 0; adult_f = 1
        married = False; children_total = 0; non_dep = dep_children()

    elif res == "Other household types: With one dependent child":
        print(f"Postcode {postcode_to_lookup}: Edge case household type: {res}. Skipping.")
        return None

    elif res == "Other household types: With two or more dependent children":
        print(f"Postcode {postcode_to_lookup}: Edge case household type: {res}. Skipping.")
        return None

    elif res == "Other household types: All full-time students":
        adults_total = random.randint(1,5) # Example: 1-5 students
        adults_over65 = 0; temp_adult_m = 0; temp_adult_f = 0
        for _ in range(adults_total):
            if gender() == "Male": temp_adult_m +=1
            else: temp_adult_f +=1
        adult_m = temp_adult_m; adult_f = temp_adult_f
        married = False; children_total = 0; non_dep = 0
        # non_dep could be adults_total if they are all non-dependent students in a shared house
        print(f"Postcode {postcode_to_lookup}: Edge case household type (students): {res}. Processed with assumptions.")

    elif res == "Other household types: All aged 65 and over":
        adults_total = 0 # No working age
        adults_over65 = random.randint(1,4) # Example: 1-4 elderly people
        # Gender for these >65s will be handled by make_people.py
        adult_m = 0; adult_f = 0
        married = False # Could be a mix, default to False
        children_total = 0; non_dep = 0
        print(f"Postcode {postcode_to_lookup}: Edge case household type (all 65+): {res}. Processed with assumptions.")

    elif res == "Other household types: Other":
        print(f"Postcode {postcode_to_lookup}: Edge case household type: {res}. Skipping due to ambiguity.")
        return None
    else:
        # This case should ideally not be reached if household.household() only returns known types.
        print(f"Postcode {postcode_to_lookup}: Unknown household type: {res}. Skipping.")
        return None

    # Create Household ORM object
    # Note: api_result_data is data['result'] from the API call
    hh = Household(
        household_UUID=str(uuid4()),
        postcode=api_result_data.get("postcode"),
        lat=float(api_result_data["latitude"]) if api_result_data.get("latitude") is not None else None,
        long=float(api_result_data["longitude"]) if api_result_data.get("longitude") is not None else None,
        admin_district=api_result_data.get("admin_district"),
        cd_lsoa=api_result_data.get("codes", {}).get("lsoa"), # LSOA code
        type=res,
        adults_total=adults_total, # Number of working age adults for make_people
        adults_m=adult_m,
        adults_f=adult_f,
        adults_65=adults_over65,
        married=married,
        children_total=children_total,
        non_dep=non_dep,
    )
    # Commit is handled by @db_session decorator when function exits successfully
    return hh


# Main execution block
if __name__ == "__main__":
    # Load postcode list (current implementation)
    try:
        import pandas as pd
        df_postcodelist_pd = pd.read_csv("test_data/postcodes-04")
        # Limiting for faster testing, remove .head() for full run
        df_postcodelist = [row[0] for index, row in df_postcodelist_pd.head(200).iterrows()]
    except ImportError:
        print("Pandas not installed, using a mock postcode list. Functionality will be limited.")
        df_postcodelist = ["SW1A1AA", "PE356EB", "PL40DW"] * 2 # Short mock list for testing

    print("==============================")
    print(f"Total Postcodes to process = {len(df_postcodelist)}")
    print("==============================")

    for postcode_str in tqdm(df_postcodelist):
        to_lookup = postcode_str.replace(" ", "")
        # print(f"Looking up postcode: {to_lookup}") # tqdm provides progress

        try:
            r = requests.get(f"http://localhost:8000/postcodes/{to_lookup}", timeout=10)
            r.raise_for_status()
            api_response_data = r.json()
            if not api_response_data or api_response_data.get("status") != 200 or not api_response_data.get("result"):
                print(f"Postcode API returned non-200 or empty result for {to_lookup}. Skipping.")
                continue
            api_data_result = api_response_data["result"] # This is what process_and_create_household_orm expects
        except requests.exceptions.RequestException as e:
            print(f"Request failed for postcode {to_lookup}: {e}. Skipping.")
            continue
        except ValueError: # Includes JSONDecodeError
            print(f"Could not decode JSON response for {to_lookup}. Skipping.")
            continue

        selected_household_type = household.household()[0] # Get one household type string

        # Call the refactored processing and ORM creation function
        # @db_session is on the function, so it handles its own session and commit
        created_household = process_and_create_household_orm(to_lookup, api_data_result, selected_household_type)

        if created_household:
            print(
                f"Saved Postcode: {created_household.postcode}, Type: {created_household.type}, "
                f"ad_T:{created_household.adults_total}, ad_65:{created_household.adults_65}, "
                f"ad_M:{created_household.adults_m}, ad_F:{created_household.adults_f}, "
                f"marr:{created_household.married}, ch_T:{created_household.children_total}, non_D:{created_household.non_dep}"
            )
        # else: print or log that it was skipped if needed, though the function itself prints.

    print("==============================")
    print("Household generation script complete.")
    print("==============================")
