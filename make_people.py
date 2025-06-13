#!/usr/bin/env python3
# System imports
import uuid
import random
from datetime import datetime

# Third party imports
import yaml # For config, if still needed for other params
from faker import Faker
from tqdm import tqdm

# Pony ORM imports
from pony.orm import db_session, select, commit

# Local Modules
# Assuming main.py contains db, Household, Person entities
# Adjust path if needed, e.g., from ..main import db, Household, Person
from models import db, Household, Person # Changed from 'main' to 'models'
import people.age
import people.nationality
# people.gender might be used if it offers more than random.choice

# Load config if any parameters are still needed (e.g., Faker seed, specific behaviors)
# For now, we are removing database config from here.
# with open("config/config.yml", "r", encoding="UTF-8") as ymlfile:
# cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
# DATABASE = cfg["database"]["db"] # Removed
# GENERAL_TABLE = cfg["database"]["general_table"] # Removed
# PEOPLE_TABLE = cfg["database"]["people_table"] # Removed

# Initialize Faker outside function if using a global seed or specific locales often
# Faker.seed(0) # Example if a global seed is desired

def create_person_entity(
    household_orm_obj: Household,
    person_type_tag: str, # e.g., "Adult", "Child", "Over65", "NonDependentAdult"
    gender: str,
    person_nationality: str,
    is_adult_person: bool,
    dob_age_tuple: tuple,
    common_last_name: str = None,
) -> Person:
    """
    Creates a Person ORM entity instance, but does not commit it.
    Commit should be handled by the calling db_session.
    """
    # Faker can be initialized per call if nationality changes frequently,
    # or initialized once with a list of locales if that's more efficient.
    faker = Faker(person_nationality) # Or use a pre-initialized 'fake' object

    person_uuid = str(uuid.uuid4())

    if gender == "Female":
        first_name = faker.first_name_female()
    elif gender == "Male":
        first_name = faker.first_name_male()
    else: # Fallback for other gender inputs, though current script uses M/F
        first_name = faker.first_name_nonbinary() if hasattr(faker, 'first_name_nonbinary') else faker.first_name()


    if common_last_name:
        last_name = common_last_name
    else:
        last_name = faker.last_name()

    date_of_birth, age = dob_age_tuple

    # Ensure date_of_birth is a date object, then combine with min time for Pony DateTime
    # people.age functions are assumed to return date objects for date_of_birth
    if not isinstance(date_of_birth, datetime.date.__class__): # Check if it's a date object
        # This is a safeguard; ideally dob_age_tuple provides a date object
        # If it's a string, parse it: datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        # For now, assuming it's a date object from people.age
        pass

    # Pony ORM DateTime fields require datetime objects, not just date objects.
    final_date_of_birth = datetime.combine(date_of_birth, datetime.min.time())


    # Create the Person ORM object (it's added to the session automatically by Pony)
    new_person = Person(
        person_UUID=person_uuid,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        is_adult=is_adult_person,
        date_of_birth=final_date_of_birth,
        age=age,
        nationality=person_nationality, # Store the string used for Faker locale
        household=household_orm_obj, # Link to the Household ORM instance
        household_UUID=household_orm_obj.household_UUID, # For potential direct FK reference
        is_claimant=False, # Default, can be updated later if needed
        # married_to_UUID is more complex and would require finding the spouse's ORM object or UUID
    )
    return new_person


# Main data processing logic
def populate_people():
    print("Starting person generation...")
    with db_session: # Manages the database session, commits at the end if no errors
        # Fetch all household objects that have a type (i.e., are valid for person generation)
        # Adjust filter as necessary, e.g., if some households shouldn't have people.
        all_households_query = select(h for h in Household if h.type != None and h.type != "")

        # Convert query to list to get a count for tqdm and iterate
        households_to_process = list(all_households_query)
        print(f"Found {len(households_to_process)} households to populate.")

        for hh_obj in tqdm(households_to_process):
            current_household_last_name = None

            # Determine number of adults to create (distinguishing working age from over 65)
            # These counts come directly from the Household object's fields
            num_male_adults_working_age = hh_obj.adults_m if hh_obj.adults_m is not None else 0
            num_female_adults_working_age = hh_obj.adults_f if hh_obj.adults_f is not None else 0
            num_adults_over65 = hh_obj.adults_65 if hh_obj.adults_65 is not None else 0
            num_children = hh_obj.children_total if hh_obj.children_total is not None else 0
            num_non_dependents = hh_obj.non_dep if hh_obj.non_dep is not None else 0

            # --- Generate Adults (Working Age) ---
            # Special handling for married couples to share a last name
            if hh_obj.married and num_male_adults_working_age == 1 and num_female_adults_working_age == 1:
                nat_m = people.nationality.country_name()
                dob_age_m = people.age.dob_working_age()
                male_adult = create_person_entity(hh_obj, "Adult", "Male", nat_m, True, dob_age_m)
                current_household_last_name = male_adult.last_name # First adult sets the surname

                nat_f = people.nationality.country_name()
                dob_age_f = people.age.dob_working_age()
                # Female adult takes the male_adult's last name
                female_adult = create_person_entity(hh_obj, "Adult", "Female", nat_f, True, dob_age_f, common_last_name=current_household_last_name)

                # Logic to link married_to_UUID if Person entity has it
                # male_adult.married_to_UUID = female_adult.person_UUID
                # female_adult.married_to_UUID = male_adult.person_UUID

                # Decrement counters as these specific adults are created
                num_male_adults_working_age = 0
                num_female_adults_working_age = 0


            # Generate remaining male working-age adults (e.g. non-married, or other compositions)
            for _ in range(num_male_adults_working_age):
                nat = people.nationality.country_name()
                dob_age = people.age.dob_working_age()
                # If household is marked as married and a surname is set, other adults might share it (e.g. polygamous context, though rare in UK)
                # For simplicity, only the primary married couple (if M/F=1/1) explicitly shares. Others get own names unless logic is expanded.
                # If current_household_last_name is None and hh_obj.married, this could be the first adult to set it.
                temp_last_name = None
                if hh_obj.married and current_household_last_name is None:
                     # This adult will set the surname if not already set by M/F pair
                     # For now, let them get a random surname, then children will pick it up if set
                     pass # Fall through to default surname generation for this adult
                elif hh_obj.married and current_household_last_name:
                    temp_last_name = current_household_last_name

                adult_male = create_person_entity(hh_obj, "Adult", "Male", nat, True, dob_age, common_last_name=temp_last_name)
                if hh_obj.married and current_household_last_name is None:
                    current_household_last_name = adult_male.last_name


            # Generate remaining female working-age adults
            for _ in range(num_female_adults_working_age):
                nat = people.nationality.country_name()
                dob_age = people.age.dob_working_age()
                temp_last_name = None
                if hh_obj.married and current_household_last_name is None:
                    pass
                elif hh_obj.married and current_household_last_name:
                    temp_last_name = current_household_last_name

                adult_female = create_person_entity(hh_obj, "Adult", "Female", nat, True, dob_age, common_last_name=temp_last_name)
                if hh_obj.married and current_household_last_name is None:
                     current_household_last_name = adult_female.last_name


            # --- Generate Over-65 Adults ---
            for _ in range(num_adults_over65):
                person_gender = random.choice(["Male", "Female"]) # Or use people.gender if available
                nat = people.nationality.country_name()
                dob_age = people.age.dob_over65()
                # Elderly might share surname if part of the core married family, or have their own.
                # Defaulting to sharing if household is married and surname is set.
                create_person_entity(hh_obj, "Over65", person_gender, nat, True, dob_age, common_last_name=current_household_last_name if hh_obj.married else None)

            # --- Generate Children ---
            for _ in range(num_children):
                child_gender = random.choice(["Male", "Female"]) # Or use people.gender
                nat = people.nationality.country_name()
                dob_age = people.age.dob_under18()
                # Children typically take the household's common last name if set
                create_person_entity(hh_obj, "Child", child_gender, nat, False, dob_age, common_last_name=current_household_last_name)

            # --- Generate Non-Dependents ---
            # Non-dependents are assumed to be adults and typically have their own surnames.
            for _ in range(num_non_dependents):
                person_gender = random.choice(["Male", "Female"]) # Or use people.gender
                nat = people.nationality.country_name()
                # Non-dependents could be working age or older, using working age as default
                dob_age = people.age.dob_working_age() # Or people.age.dob_over18()
                create_person_entity(hh_obj, "NonDependentAdult", person_gender, nat, True, dob_age, common_last_name=None)

        # commit() is implicitly called here by Pony ORM at the end of the db_session block
        # if no exceptions were raised.

    print("Person generation complete.")

if __name__ == "__main__":
    # This ensures that the script can be run directly.
    # The database connection and mappings must be established before populate_people() is called.
    # This is typically done when main.py (or wherever db is defined and bound) is imported.
    # If db is not bound, this script will fail.

    # Example of how db might be initialized (should be in main.py or equivalent setup script):
    # from main import db  # db object
    # db.bind(provider='postgres', user='your_user', password='your_password', host='localhost', database='your_db')
    # db.generate_mapping(create_tables=True) # Or False if tables exist

    populate_people()
