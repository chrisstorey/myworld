from datetime import datetime
from pony.orm import Database, Required, Optional, Set, PrimaryKey, commit, db_session, select

# Initialize Database object
db = Database()

# Database binding (configure as per your project's settings)
db.bind(
    provider="postgres",
    user="chris",  # Replace with your actual username from main.py or config
    password="neurologywidget",  # Replace with your actual password
    host="localhost",
    database="test",  # Replace with your actual database name
)

# Entity definitions
class Person(db.Entity):  # type: ignore
    _table_ = "person"
    person_UUID = PrimaryKey(str)
    first_name = Optional(str)
    last_name = Optional(str)
    gender = Optional(str)
    is_adult = Optional(bool)
    date_of_birth = Optional(datetime) # Ensure this is datetime
    age = Optional(int)
    married_to_UUID = Optional(str) # This can be an ID of another Person
    nationality = Optional(str)
    is_claimant = Optional(bool)
    # household_UUID = Optional(str) # Removed as per instructions
    household = Required("Household")  # Changed to Required


class Household(db.Entity):  # type: ignore
    _table_ = "household" # Explicit table name
    household_UUID = PrimaryKey(str)
    postcode = Optional(str)
    lat = Optional(float)
    long = Optional(float)
    admin_district = Optional(str)
    cd_lsoa = Optional(str) # LSOA code
    type = Optional(str) # Household type description
    adults_total = Optional(int)
    adults_m = Optional(int)
    adults_f = Optional(int)
    adults_65 = Optional(int)
    married = Optional(bool)
    children_total = Optional(int)
    non_dep = Optional(int)
    persons = Set(Person)

# Generate mapping and create tables if they don't exist
# This should be called once after all entities are defined and db is bound.
db.generate_mapping(create_tables=True)
