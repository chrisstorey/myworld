#!/usr/bin/env python3
# System imports

import uuid

# Third party imports
import pandas as pd
import yaml
from faker import Faker
from tqdm import tqdm

import people.age
import people.gender
# Local Modules
import people.nationality
from sql_helpers import create_connection

with open("config/config.yml", "r", encoding="UTF-8") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
DATABASE = cfg["database"]["db"]
GENERAL_TABLE = cfg["database"]["general_table"]
PEOPLE_TABLE = cfg["database"]["people_table"]


def create_first_name(nationality: str, gender: str) -> str:
    fake = Faker(nationality)
    if gender == "Female":
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name_male()
    return first_name


def create_last_name(nationality: str):
    fake = Faker(nationality)
    last_name = fake.last_name()
    return last_name


def create_person(
    my_world_premise_id: str,
    type_of_person: str,
    gender: str,
    married_surname: str = None,
) -> object:
    my_world_premise_id = my_world_premise_id
    my_world_person_id = str(uuid.uuid4())
    nationality = people.nationality.country_name()
    first_name = create_first_name(nationality, gender)
    if married_surname is not None:
        last_name = married_surname
    else:
        last_name = create_last_name(nationality)

    if type_of_person == "lead-adult":
        adult = True
        dob = people.age.dob_working_age()
    elif type_of_person == "adult":
        adult = True
        dob = people.age.dob_over18()
    elif type_of_person == "65":
        adult = True
        dob = people.age.dob_over65()
    else:
        adult = False
        dob = people.age.dob_under18()
    return (
        my_world_premise_id,
        my_world_person_id,
        nationality,
        first_name,
        last_name,
        type_of_person,
        dob,
        adult,
        married_surname,
    )


# main function
household_data = create_connection(DATABASE)
household_dataframe = pd.read_sql_query(
    """SELECT * from """ + GENERAL_TABLE + """ WHERE adults_total IS NOT NULL""",
    household_data,
)
print("Length of dataframe : ", len(household_dataframe))

people_dataframe = pd.DataFrame(
    columns=[
        "My_World_person_UUID",
        "first_name",
        "last_name",
        "gender",
        "adult",
        "date_of_birth",
        "age",
        "married_to_UUID",
        "nationality_for_name",
        "is_claimant",
        "My_World_premise_UUID",
    ]
)


class My_World_premise_UUID:
    pass


for i in tqdm(range(len(household_dataframe))):
    print(
        i,
        household_dataframe.My_World_premise_UUID[i],
        household_dataframe.household_type[i],
        "Adults =",
        household_dataframe.adults_total[i],
        "+65 =",
        household_dataframe.adults_over65[i],
        "Male Adults =",
        household_dataframe.adult_m[i],
        "Female Adults =",
        household_dataframe.adult_f[i],
        "Is married =",
        household_dataframe.married[i],
        "Total Children =",
        household_dataframe.children_total[i],
        "Non-Deps =",
        household_dataframe.non_dep[i],
        people.nationality.country_name(),
    )

    for male in range(household_dataframe.adult_m[i]):
        person = create_person(My_World_premise_UUID, "Adult", "Male")
        print(person)
        person_My_World_person_UUID = My_World_premise_UUID
        person_first_name = person[3]
        person_last_name = person[8]
        person_gender = "Male"
        person_adult = person[5]
        person_date_of_birth = person[6]
        person_age = (0,)
        person_married_to_UUID = ("",)
        person_nationality_for_name = person[2]
        person_is_claimant = False
        person_My_World_premise_UUID = person[0]

        people_dataframe.append(
            {
                "My_World_person_UUID": My_World_premise_UUID,
                "first_name": person_first_name,
                "last_name": person_last_name,
                "gender": person_gender,
                "adult": person_adult,
                "date_of_birth": person_date_of_birth,
                "age": person_age,
                "married_to_UUID": person_married_to_UUID,
                "nationality_for_name": person_nationality_for_name,
                "is_claimant": person_is_claimant,
                "My_World_premise_UUID": person_My_World_premise_UUID,
            }
        )

    for female in range(household_dataframe.adult_f[i]):
        if household_dataframe.married[i]:
            create_person(My_World_premise_UUID[i], "Adult", "Female", last_name)
        else:
            create_person(My_World_premise_UUID[i], "Adult", "Female")

        people_dataframe.append(
            "My_World_person_UUID",
            "first_name",
            "last_name",
            "gender",
            "adult",
            "date_of_birth",
            "age",
            "married_to_UUID",
            "nationality_for_name",
            "is_claimant",
            "My_World_premise_UUID",
        )

        # for children
        #     create_person(My_World_premise_UUID[i], "child", random.choice(["Male", "Female"]), last_name)
        #
        # for maleover65
        #     create_person(My_World_premise_UUID[i], "65", "Male")
        #
        # for femaleover65
        #     create_person(My_World_premise_UUID[i], "65", "Female")
