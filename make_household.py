import random
import requests
import yaml
from faker import Faker
from tqdm import tqdm
from uuid import uuid4

import household
from models import db, Household
from pony.orm import db_session
from make_people import PeopleGenerator

Faker.seed(0)
fake = Faker(["en-GB"])

with open("config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
TOTAL_RECORDS = cfg["total_records"]

class HouseholdGenerator:
    def __init__(self, postcode_api_url="http://localhost:8000/postcodes/"):
        self.postcode_api_url = postcode_api_url
        self.people_generator = PeopleGenerator()

    @staticmethod
    def two_or_three_and_more_children():
        return random.choices([2, 3], weights=[75, 25])[0]

    @staticmethod
    def dep_children():
        return random.choices([1, 2, 3], weights=[38, 46, 15])[0]

    @staticmethod
    def gender():
        return random.choice(["Male", "Female"])

    def parse_household_type(self, res: str):
        counts = {
            "adults_total": 0, "adults_over65": 0,
            "adult_m": 0, "adult_f": 0,
            "married": False, "children_total": 0, "non_dep": 0
        }

        if res == "One person household: Aged 65 and over":
            counts["adults_over65"] = 1
        elif res == "One person household: Other":
            counts["adults_total"] = 1
            if self.gender() == "Male": counts["adult_m"] = 1
            else: counts["adult_f"] = 1
        elif res == "One family only: All aged 65 and over":
            counts["adults_over65"] = 2
            counts["married"] = True
        elif res.startswith("One family only: Married couple:") or \
             res.startswith("One family only: Same-sex civil partnership couple:") or \
             res.startswith("One family only: Cohabiting couple:"):
            counts["adults_total"] = 2
            counts["married"] = not res.startswith("One family only: Cohabiting couple:")
            if res.startswith("One family only: Same-sex civil partnership couple:"):
                 if self.gender() == "Male": counts["adult_m"] = 2
                 else: counts["adult_f"] = 2
            else:
                 counts["adult_m"] = 1; counts["adult_f"] = 1

            if "No children" in res:
                pass
            elif "One dependent child" in res:
                counts["children_total"] = 1
            elif "Two or more dependent children" in res:
                counts["children_total"] = self.two_or_three_and_more_children()
            elif "All children non-dependent" in res:
                counts["non_dep"] = self.dep_children()

        elif res.startswith("One family only: Lone parent:"):
            counts["adults_total"] = 1
            if self.gender() == "Male": counts["adult_m"] = 1
            else: counts["adult_f"] = 1

            if "One dependent child" in res:
                counts["children_total"] = 1
            elif "Two or more dependent children" in res:
                counts["children_total"] = self.two_or_three_and_more_children()
            elif "All children non-dependent" in res:
                counts["non_dep"] = self.dep_children()

        elif res == "Other household types: All full-time students":
            counts["adults_total"] = random.randint(1,5)
            for _ in range(counts["adults_total"]):
                if self.gender() == "Male": counts["adult_m"] += 1
                else: counts["adult_f"] += 1
        elif res == "Other household types: All aged 65 and over":
            counts["adults_over65"] = random.randint(1,4)
        elif res.startswith("Other household types:"):
            return None

        return counts

    def fetch_postcode_data(self, postcode: str):
        try:
            r = requests.get(f"{self.postcode_api_url}{postcode}", timeout=2)
            r.raise_for_status()
            api_response_data = r.json()
            if not api_response_data or api_response_data.get("status") != 200 or not api_response_data.get("result"):
                raise ValueError("Invalid API response")
            return api_response_data["result"]
        except (requests.exceptions.RequestException, ValueError):
            return {
                "postcode": postcode,
                "latitude": round(random.uniform(50.0, 60.0), 6),
                "longitude": round(random.uniform(-5.0, 1.0), 6),
                "admin_district": "Mock District",
                "codes": {"lsoa": f"E010{random.randint(10000, 99999)}"}
            }

    @db_session
    def process_and_create_household_orm(self, postcode_to_lookup: str, household_type_string: str) -> Household | None:
        counts = self.parse_household_type(household_type_string)
        if counts is None:
            return None

        api_result_data = self.fetch_postcode_data(postcode_to_lookup)

        hh = Household(
            household_UUID=str(uuid4()),
            postcode=api_result_data.get("postcode"),
            lat=float(api_result_data["latitude"]) if api_result_data.get("latitude") is not None else None,
            long=float(api_result_data["longitude"]) if api_result_data.get("longitude") is not None else None,
            admin_district=api_result_data.get("admin_district"),
            cd_lsoa=api_result_data.get("codes", {}).get("lsoa"),
            type=household_type_string,
            adults_total=counts["adults_total"],
            adults_m=counts["adult_m"],
            adults_f=counts["adult_f"],
            adults_65=counts["adults_over65"],
            married=counts["married"],
            children_total=counts["children_total"],
            non_dep=counts["non_dep"],
        )
        self.people_generator.generate_people_for_household(hh)
        return hh

if __name__ == "__main__":
    try:
        import pandas as pd
        df_postcodelist_pd = pd.read_csv("test_data/postcodes-04")
        df_postcodelist = [row[0] for index, row in df_postcodelist_pd.head(200).iterrows()]
    except ImportError:
        print("Pandas not installed, using a mock postcode list. Functionality will be limited.")
        df_postcodelist = ["SW1A1AA", "PE356EB", "PL40DW"] * 2

    print("==============================")
    print(f"Total Postcodes to process = {len(df_postcodelist)}")
    print("==============================")

    generator = HouseholdGenerator()

    for postcode_str in tqdm(df_postcodelist):
        to_lookup = postcode_str.replace(" ", "")
        selected_household_type = household.household()[0]
        generator.process_and_create_household_orm(to_lookup, selected_household_type)

    print("==============================")
    print("Household generation script complete.")
    print("==============================")
