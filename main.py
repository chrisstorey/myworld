import random
from datetime import datetime # Kept for potential use if add_person or similar is ever uncommented
from uuid import uuid4 # Kept for potential use

import pyroscope
from faker import Faker # Kept for potential use
# from pony.orm import * # Avoid wildcard imports if possible
# Specific Pony ORM imports might be needed if functions using db_session are uncommented
# For now, assuming db_session is not directly used in the active parts of main.py
# from pony.orm import db_session # Example if add_person was to be restored

import people # This import seems related to the commented out dob functions.

# Import db object and entities from models.py
from models import db, Person, Household

pyroscope.configure(
    application_name="my-world-1",
    server_address="https://profiles-prod-003.grafana.net",
    basic_auth_username="157601",
    basic_auth_password="glc_eyJvIjoiNDQ1Mzc4IiwibiI6InN0YWNrLTE1NzYwMS1ocC1jaHJpcyIsImsiOiJnNDRhSTYzRExoOTAwYTE1Zkx4R2VINngiLCJtIjp7InIiOiJ1cyJ9fQ==",
)
# Database setup (db object, binding, entity definitions, and mapping)
# has been moved to models.py. Importing 'db' from models.py makes the
# configured db object available and ensures generate_mapping was called.


# set_sql_debug(True) # This can be called on the imported db object if needed:
# import models
# models.db.set_sql_debug(True)


# The following functions and loop were used for generating standalone persons.
# This functionality is now superseded by make_people.py, which generates persons within households.
# These are commented out to avoid creating orphaned person records.
# Setup nationalities

# country_names = [
    "en_GB",
    "en_IE",
    "en_IN",
    "ro_RO",
    "pl_PL",
    "lt_LT",
    "de_DE",
    "en_US",
    "zh_CN",
#     "tw_GH",
# ]

# country_names_weights = [840, 10, 61, 26, 24, 6, 6, 5, 4, 18]


# def nationality_name():
#     name = random.choices(country_names, weights=country_names_weights)
#     return name[0]


# def gender():
#     _gender = random.choices(["Male", "Female"], weights=[9767, 10000])
#     return _gender[0]


# @db_session
# def add_person(
#     _type_of_person: str,
#     _gender: str,
#     _nationality: str = "en_GB",
#     is_claimant: bool = False,
#     household_uuid: str = "",
#     married_lastname: str = "",
# ):
#     with pyroscope.tag_wrapper({"person": _type_of_person}):
#         faker = Faker(_nationality)

#         if _gender == "Female":
#             first_name: str = faker.first_name_female()
#         else:
#             first_name: str = faker.first_name_male()  # type: ignore

#         if _nationality == "zh_CN":
#             first_name: str = faker.first_romanized_name()  # type: ignore
#             last_name: str = faker.last_romanized_name()
#         else:
#             if married_lastname != "":
#                 last_name = married_lastname
#             else:
#                 last_name = faker.last_name()

#         if _type_of_person == "Non-Dep":
#             date_of_birth, age = people.dob_non_dep()
#             is_adult = False
#         elif _type_of_person == "Under18":
#             date_of_birth, age = people.dob_under18()
#             is_adult = False
#         elif _type_of_person == "Over65":
#             date_of_birth, age = people.dob_over65()
#             is_adult = True
#         else:
#             date_of_birth, age = people.dob_working_age()
#             is_adult = True

#         Person(
#             person_UUID=str(uuid4()),
#             first_name=first_name,
#             last_name=last_name,
#             gender=_gender,
#             is_adult=is_adult,
#             date_of_birth=datetime.combine(date_of_birth, datetime.min.time()),
#             age=age,
#             is_claimant=is_claimant,
#             nationality=_nationality,
#             household_UUID=household_uuid,
#         )


# # -----------------------------------------
# # Main loop
# # -----------------------------------------

# for x in range(10000):
#     nationality = nationality_name()
#     type_of_person = random.choices(
#         ["Adult", "Non-Dep", "Under18", "Over65"], [47, 2, 16, 35]
#     )
#     add_person(type_of_person[0], gender(), nationality)


# with db_session:
#     result = select(h for h in Household if h.type == "One person household: Other")
#     for h in result:
#         print(result)
