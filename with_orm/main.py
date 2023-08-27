import random
from datetime import datetime
from uuid import uuid4

from faker import Faker
from pony.orm import *

import people.age

# Setup ORM and DB classes

db = Database()
db.bind(
    provider="postgres",
    user="chris",
    password="neurologywidget",
    host="localhost",
    database="test",
)


class Person(db.Entity):
    _table_ = "person"
    person_UUID = PrimaryKey(str)
    first_name = Optional(str)
    last_name = Optional(str)
    gender = Optional(str)
    is_adult = Optional(bool)
    date_of_birth = Optional(datetime)
    age = Optional(int)
    married_to_UUID = Optional(str)
    nationality = Optional(str)
    is_claimant = Optional(bool)
    household_UUID = Optional(str)
    household = Optional("Household")


class Household(db.Entity):
    household_UUID = PrimaryKey(str)
    postcode = Optional(str)
    lat = Optional(float)
    long = Optional(float)
    type = Optional(str)
    adults_total = Optional(int)
    adults_m = Optional(int)
    adults_f = Optional(int)
    adults_65 = Optional(int)
    married = Optional(bool)
    children_total = Optional(int)
    non_dep = Optional(int)
    persons = Set(Person)


# set_sql_debug(True)

db.generate_mapping(create_tables=True)

# Setup nationalities

country_names = [
    "en_GB",
    "en_IE",
    "en_IN",
    "ro_RO",
    "pl_PL",
    "lt_LT",
    "de_DE",
    "en_US",
    "zh_CN",
    "tw_GH",
]

country_names_weights = [840, 10, 61, 26, 24, 6, 6, 5, 4, 18]


def nationality_name():
    name = random.choices(country_names, weights=country_names_weights)
    return name[0]


def gender():
    gender = random.choices(["Male", "Female"], weights=[9767, 10000])
    return gender[0]


@db_session
def add_person(
    type_of_person: str,
    gender: str,
    nationality: str = "en_GB",
    is_claimant: bool = False,
    household_UUID: str = "",
    married_lastname: str = "",
):
    faker = Faker(nationality)

    if gender == "Female":
        first_name: str = faker.first_name_female()
    else:
        first_name: str = faker.first_name_male()

    if nationality == "zh_CN":
        first_name: str = faker.first_romanized_name()
        last_name: str = faker.last_romanized_name()
    else:
        if married_lastname != "":
            last_name = married_lastname
        else:
            last_name = faker.last_name()

    if type_of_person == "Non-Dep":
        date_of_birth, age = people.age.dob_non_dep()
        is_adult = False
    elif type_of_person == "Under18":
        date_of_birth, age = people.age.dob_under18()
        is_adult = False
    elif type_of_person == "Over65":
        date_of_birth, age = people.age.dob_over65()
        is_adult = True
    else:
        date_of_birth, age = people.age.dob_working_age()
        is_adult = True

    Person(
        person_UUID=str(uuid4()),
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        is_adult=is_adult,
        date_of_birth=datetime.combine(date_of_birth, datetime.min.time()),
        age=age,
        is_claimant=is_claimant,
        nationality=nationality,
        household_UUID=household_UUID,
    )


for x in range(10000):
    nationality = nationality_name()
    type_of_person = random.choices(["Adult", "Non-Dep", "Under18", "Over65"],[50,5,15,30])
    print(type_of_person)
    add_person(type_of_person[0], gender(), nationality)
