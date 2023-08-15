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

with open("config/config.yml", "r", encoding='UTF-8') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
DATABASE = cfg["database"]["db"]
GENERAL_TABLE = cfg["database"]["general_table"]
PEOPLE_TABLE = cfg["database"]["people_table"]





def create_first_name(nationality: str, gender: str):
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


def create_person(my_world_premise_id: str, type_of_person: str, gender: str, married_surname: str = None) -> object:
    my_world_premise_id = my_world_premise_id
    my_world_person_id = str(uuid.uuid4())
    nationality = people.nationality.country_name()
    first_name = create_first_name(nationality, gender)
    if married_surname != None:
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
    return my_world_premise_id, my_world_person_id, nationality, first_name, last_name, \
           type_of_person, dob, adult, married_surname


# main function
household_data = create_connection(DATABASE)
household_dataframe = pd.read_sql_query("""SELECT * from """ + GENERAL_TABLE, household_data)
print("Length of dataframe : ", len(household_dataframe))

people_dataframe.DataFrame(columns=[
    'My_World_person_UUID',
    "first_name",
    "last_name",
    "gender",
    "adult",
    "date_of_birth",
    "age",
    "married_to_UUID",
    "nationality_for_name",
    "is_claimant",
    'My_World_premise_UUID'])
for i in tqdm(range(len(household_dataframe))):
    print(i, household_dataframe.My_World_premise_UUID[i],
          household_dataframe.household_type[i],
          "Adults =", household_dataframe.adults_total[i],
          "+65 =", household_dataframe.adults_over65[i],
          "Male Adults =", household_dataframe.adult_m[i],
          "Female Adults =", household_dataframe.adult_f[i],
          "Is married =", household_dataframe.married[i],
          "Total Children =", household_dataframe.children_total[i],
          "Non-Deps =", household_dataframe.non_dep[i], people.nationality.country_name()
          )

    for male in range(household_dataframe.adult_m[i]):
        create_person(my_world_premise_id[i], "Adult", "Male")
        people_dataframe.append(
            'My_World_person_UUID',
            "first_name",
            "last_name",
            "gender",
            "adult",
            "date_of_birth",
            "age",
            "married_to_UUID",
            "nationality_for_name",
            "is_claimant",
            'My_World_premise_UUID')
        for female adults
            if married:
                create_person(my_world_premise_id[i], "Adult", "Female", last_name)
            elif:
                create_person(my_world_premise_id[i], "Adult", "Female")

        for children
            create_person(my_world_premise_id[i], "child", random.choice(["Male", "Female"]), last_name)

        for maleover65
        create_person(my_world_premise_id[i], "65", "Male")

        for femaleover65
        create_person(my_world_premise_id[i], "65", "Female")



        # test_nat = people.nationality.country_name()[0]
        test_gender = people.gender.gender()[0]
        # print(test_nat)
        # print(create_first_name(test_nat, test_gender))
        # print(create_last_name(test_nat))

        person = create_person("bf6c4706-3f78-4748-944f-71566009cb72", "adult", test_gender, True)
        print(person)

# for i in tqdm(range(len(household_dataframe))):
#     household_dataframe['outcode'][i] = data['result'][0]['outcode']
#     household_dataframe['admin_district'][i] = data['result'][0]['admin_district']
#     update_outcode(household_data,
#                    GENERAL_TABLE, (household_dataframe['outcode'][i],
#                                    household_dataframe['id'][i]))
#     update_admin_district(household_data, GENERAL_TABLE,
#                          (household_dataframe['admin_district'][i], household_dataframe['id'][i]))
