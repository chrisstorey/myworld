import uuid
import random
from datetime import datetime

from faker import Faker
from tqdm import tqdm
from pony.orm import db_session, select

from models import db, Household, Person
import people.age
import people.nationality

class PeopleGenerator:
    def __init__(self):
        pass

    def create_person_entity(self, household_orm_obj: Household, person_type_tag: str, gender: str, person_nationality: str, is_adult_person: bool, dob_age_tuple: tuple, common_last_name: str = None) -> Person:
        faker = Faker(person_nationality)
        person_uuid = str(uuid.uuid4())

        if gender == "Female":
            first_name = faker.first_name_female()
        elif gender == "Male":
            first_name = faker.first_name_male()
        else:
            first_name = faker.first_name_nonbinary() if hasattr(faker, 'first_name_nonbinary') else faker.first_name()

        if common_last_name:
            last_name = common_last_name
        else:
            last_name = faker.last_name()

        date_of_birth, age = dob_age_tuple
        final_date_of_birth = datetime.combine(date_of_birth, datetime.min.time())

        new_person = Person(
            person_UUID=person_uuid,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            is_adult=is_adult_person,
            date_of_birth=final_date_of_birth,
            age=age,
            nationality=person_nationality,
            household=household_orm_obj,
            is_claimant=False,
        )
        return new_person

    def generate_people_for_household(self, hh_obj: Household):
        current_household_last_name = None
        num_male_adults_working_age = hh_obj.adults_m if hh_obj.adults_m is not None else 0
        num_female_adults_working_age = hh_obj.adults_f if hh_obj.adults_f is not None else 0
        num_adults_over65 = hh_obj.adults_65 if hh_obj.adults_65 is not None else 0
        num_children = hh_obj.children_total if hh_obj.children_total is not None else 0
        num_non_dependents = hh_obj.non_dep if hh_obj.non_dep is not None else 0

        if hh_obj.married and num_male_adults_working_age == 1 and num_female_adults_working_age == 1:
            nat_m = people.nationality.country_name()
            dob_age_m = people.age.dob_working_age()
            male_adult = self.create_person_entity(hh_obj, "Adult", "Male", nat_m, True, dob_age_m)
            current_household_last_name = male_adult.last_name

            nat_f = people.nationality.country_name()
            dob_age_f = people.age.dob_working_age()
            female_adult = self.create_person_entity(hh_obj, "Adult", "Female", nat_f, True, dob_age_f, common_last_name=current_household_last_name)
            num_male_adults_working_age = 0
            num_female_adults_working_age = 0

        for _ in range(num_male_adults_working_age):
            nat = people.nationality.country_name()
            dob_age = people.age.dob_working_age()
            temp_last_name = None
            if hh_obj.married and current_household_last_name:
                temp_last_name = current_household_last_name
            adult_male = self.create_person_entity(hh_obj, "Adult", "Male", nat, True, dob_age, common_last_name=temp_last_name)
            if hh_obj.married and current_household_last_name is None:
                current_household_last_name = adult_male.last_name

        for _ in range(num_female_adults_working_age):
            nat = people.nationality.country_name()
            dob_age = people.age.dob_working_age()
            temp_last_name = None
            if hh_obj.married and current_household_last_name:
                temp_last_name = current_household_last_name
            adult_female = self.create_person_entity(hh_obj, "Adult", "Female", nat, True, dob_age, common_last_name=temp_last_name)
            if hh_obj.married and current_household_last_name is None:
                 current_household_last_name = adult_female.last_name

        for _ in range(num_adults_over65):
            person_gender = random.choice(["Male", "Female"])
            nat = people.nationality.country_name()
            dob_age = people.age.dob_over65()
            self.create_person_entity(hh_obj, "Over65", person_gender, nat, True, dob_age, common_last_name=current_household_last_name if hh_obj.married else None)

        for _ in range(num_children):
            child_gender = random.choice(["Male", "Female"])
            nat = people.nationality.country_name()
            dob_age = people.age.dob_under18()
            self.create_person_entity(hh_obj, "Child", child_gender, nat, False, dob_age, common_last_name=current_household_last_name)

        for _ in range(num_non_dependents):
            person_gender = random.choice(["Male", "Female"])
            nat = people.nationality.country_name()
            dob_age = people.age.dob_working_age()
            self.create_person_entity(hh_obj, "NonDependentAdult", person_gender, nat, True, dob_age, common_last_name=None)
