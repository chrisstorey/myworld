import pytest
from datetime import date, datetime
import collections # For checking list contents if needed

# Functions/modules to test
from people import age as people_age
from household import household as household_module # household is a function and a module name
from people import nationality as people_nationality

def calculate_age_for_test(born: date) -> int:
    today = date.today()
    # Subtract 1 if today's month/day is before birth month/day
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

# Test for dob_under18
def test_dob_under18():
    for _ in range(20): # Test a few samples
        dob, age = people_age.dob_under18()
        assert isinstance(dob, date)
        assert isinstance(age, int)
        assert 0 <= age <= 17
        assert age == calculate_age_for_test(dob), f"Failed for DoB: {dob}, Calculated Age: {calculate_age_for_test(dob)}, Reported Age: {age}"

# Test for dob_working_age
def test_dob_working_age():
    for _ in range(20):
        dob, age = people_age.dob_working_age()
        assert isinstance(dob, date)
        assert isinstance(age, int)
        assert 18 <= age <= 64 # Assuming working age is 18-64
        assert age == calculate_age_for_test(dob), f"Failed for DoB: {dob}, Calculated Age: {calculate_age_for_test(dob)}, Reported Age: {age}"

# Test for dob_over65
def test_dob_over65():
    for _ in range(20):
        dob, age = people_age.dob_over65()
        assert isinstance(dob, date)
        assert isinstance(age, int)
        assert age >= 65
        assert age == calculate_age_for_test(dob), f"Failed for DoB: {dob}, Calculated Age: {calculate_age_for_test(dob)}, Reported Age: {age}"

# Test for dob_non_dep (Non-Dependent)
def test_dob_non_dep():
    # Based on age_non_dep_names = ["16", "17"] in people/age.py
    expected_ages = {16, 17}
    for _ in range(20):
        dob, age = people_age.dob_non_dep()
        assert isinstance(dob, date)
        assert isinstance(age, int)
        assert age in expected_ages
        assert age == calculate_age_for_test(dob), f"Failed for DoB: {dob}, Calculated Age: {calculate_age_for_test(dob)}, Reported Age: {age}"

# Test for dob_over18 (general over 18, can include over 65)
def test_dob_over18():
    for _ in range(20):
        dob, age = people_age.dob_over18()
        assert isinstance(dob, date)
        assert isinstance(age, int)
        assert age >= 18
        assert age == calculate_age_for_test(dob), f"Failed for DoB: {dob}, Calculated Age: {calculate_age_for_test(dob)}, Reported Age: {age}"

# Test for household.household()
def test_household_type_selection():
    # household_module is the module, household_module.household is the function
    household_types_list = household_module.household()
    assert isinstance(household_types_list, list)
    # The function household.household() returns k=100 samples
    assert len(household_types_list) == 100

    # Check if all returned types are valid options
    # household_module.household_options is the list of options in household/__init__.py
    valid_options = set(household_module.household_options)
    for ht_type in household_types_list:
        assert ht_type in valid_options

# Test for people.nationality.country_name()
def test_nationality_country_name_selection():
    for _ in range(20): # Test a few samples
        country = people_nationality.country_name()
        assert isinstance(country, str)
        assert country in people_nationality.country_names, f"Unexpected country: {country}"
