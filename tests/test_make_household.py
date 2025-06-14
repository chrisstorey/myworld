import pytest
from unittest.mock import patch, MagicMock
from uuid import UUID # For checking UUID format

# Path adjustments may be needed if 'models' or 'make_household' are not directly importable.
# This assumes the project root is in sys.path when pytest runs.
from models import db, Household
from pony.orm import db_session, select, count

# Import the refactored function
# Note: 'gender' from make_household is also imported as it's used in its demographic logic.
# If 'gender' or other helpers like 'two_or_three_and_more_children' were part of the class
# or not globally accessible, this import might need adjustment or mocking.
from make_household import process_and_create_household_orm, gender as make_household_gender

# Test database session fixture
@pytest.fixture(scope="function")
def setup_db_for_test():
    # This fixture can be used for test-specific database setup or cleanup if needed.
    # Since process_and_create_household_orm is @db_session decorated, it manages its own session.
    # This fixture is more for ensuring a clean state or for test-side queries.
    with db_session:
        # Example: Clear relevant data before a test, or ensure specific preconditions.
        # For this test suite, cleanup is handled within each test that creates data.
        pass

def test_create_married_couple_no_children(setup_db_for_test):
    test_postcode_str = "TESTPOST1"
    mock_api_result_data = {
        "postcode": "TESTPOST1",
        "latitude": 51.5000,
        "longitude": -0.1000,
        "admin_district": "Test District",
        "codes": {"lsoa": "TestLSOA"},
        # Ensure all fields accessed by process_and_create_household_orm from api_result_data are here
        # e.g., api_result_data.get("codes", {}).get("lsoa")
    }
    selected_household_type = "One family only: Married couple: No children"

    # Call the refactored function. It handles its own @db_session.
    created_hh_obj = process_and_create_household_orm(test_postcode_str, mock_api_result_data, selected_household_type)

    assert created_hh_obj is not None, "Household object should have been created"
    assert created_hh_obj.type == selected_household_type
    assert created_hh_obj.postcode == mock_api_result_data["postcode"]
    assert created_hh_obj.lat == mock_api_result_data["latitude"]

    # Based on the logic in process_and_create_household_orm for this type:
    assert created_hh_obj.adults_total == 2 # This refers to working age adults for make_people
    assert created_hh_obj.adults_m == 1
    assert created_hh_obj.adults_f == 1
    assert created_hh_obj.married is True
    assert created_hh_obj.children_total == 0
    assert created_hh_obj.adults_65 == 0
    assert created_hh_obj.non_dep == 0

    try:
        UUID(created_hh_obj.household_UUID, version=4)
    except ValueError:
        pytest.fail(f"Generated household_UUID {created_hh_obj.household_UUID} is not a valid UUID4")

    # Verify it's in the database by querying using its UUID
    with db_session:
        retrieved_hh = Household.get(household_UUID=created_hh_obj.household_UUID)
        assert retrieved_hh is not None
        assert retrieved_hh.type == selected_household_type

        # Clean up the created record
        if retrieved_hh:
            retrieved_hh.delete()

def test_skip_other_household_type(setup_db_for_test):
    test_postcode_str = "SKIPPOST1"
    mock_api_result_data = {
        "postcode": "SKIPPOST1", "latitude": 52.0, "longitude": 0.0,
        "admin_district": "Skip District", "codes": {"lsoa": "SkipLSOA"}
    }
    selected_household_type = "Other household types: Other" # This type should be skipped

    initial_count = 0
    with db_session:
        initial_count = count(h for h in Household)

    # Call the refactored function
    created_hh_obj = process_and_create_household_orm(test_postcode_str, mock_api_result_data, selected_household_type)

    assert created_hh_obj is None, "Household object should NOT be created for 'Other household types: Other'"

    with db_session:
        final_count = count(h for h in Household)
        assert final_count == initial_count, "Database count should not change for skipped type"

# Example of how to test a type that involves random choices for demographics,
# requiring mocking of those choices.
@patch('make_household.two_or_three_and_more_children', return_value=3) # Mock the choice to be 3 children
@patch('make_household.gender') # Mock gender if its output affects logic for a specific type significantly
def test_create_married_couple_three_children(mock_gender, mock_children_choice, setup_db_for_test):
    # Mock gender if needed for a specific path in the logic, e.g. for same-sex couples.
    # For "Married couple: Two or more dependent children", gender of parents is fixed M/F.
    # mock_gender.return_value = "Male" # Example, not strictly needed for this type

    test_postcode_str = "TESTPOST2"
    mock_api_result_data = {
        "postcode": "TESTPOST2", "latitude": 51.0, "longitude": -0.2,
        "admin_district": "Test District 2", "codes": {"lsoa": "TestLSOA2"}
    }
    selected_household_type = "One family only: Married couple: Two or more dependent children"

    created_hh_obj = process_and_create_household_orm(test_postcode_str, mock_api_result_data, selected_household_type)

    assert created_hh_obj is not None
    assert created_hh_obj.type == selected_household_type
    assert created_hh_obj.adults_total == 2
    assert created_hh_obj.adults_m == 1
    assert created_hh_obj.adults_f == 1
    assert created_hh_obj.married is True
    assert created_hh_obj.children_total == 3 # Asserting based on the mocked return_value
    assert created_hh_obj.adults_65 == 0
    assert created_hh_obj.non_dep == 0

    with db_session:
        retrieved_hh = Household.get(household_UUID=created_hh_obj.household_UUID)
        assert retrieved_hh is not None
        assert retrieved_hh.children_total == 3
        if retrieved_hh:
            retrieved_hh.delete()

# Add more tests for other household types, especially those with different logic paths
# or those that use the other random choice functions like `dep_children`.
# For example, a test for "One person household: Aged 65 and over":
def test_create_one_person_over65(setup_db_for_test):
    test_postcode_str = "TESTPOST_O65"
    mock_api_result_data = {
        "postcode": "TESTPOST_O65", "latitude": 51.1, "longitude": -0.3,
        "admin_district": "Test District O65", "codes": {"lsoa": "TestLSOAO65"}
    }
    # The gender of the >65 person is determined by `make_household.gender()` within
    # `process_and_create_household_orm` if the original logic for setting adults_m/f for >65s was kept.
    # However, the refactored logic in the prompt sets adults_m=0, adults_f=0 for this type,
    # deferring gender assignment of the >65 person to make_people.py.
    # So, we don't need to mock gender here for asserting adults_m/f.
    selected_household_type = "One person household: Aged 65 and over"

    created_hh_obj = process_and_create_household_orm(test_postcode_str, mock_api_result_data, selected_household_type)

    assert created_hh_obj is not None
    assert created_hh_obj.type == selected_household_type
    assert created_hh_obj.adults_total == 0 # No working age adults
    assert created_hh_obj.adults_m == 0 # No working age adult males
    assert created_hh_obj.adults_f == 0 # No working age adult females
    assert created_hh_obj.adults_65 == 1 # One adult over 65
    assert created_hh_obj.married is False
    assert created_hh_obj.children_total == 0
    assert created_hh_obj.non_dep == 0

    with db_session:
        retrieved_hh = Household.get(household_UUID=created_hh_obj.household_UUID)
        assert retrieved_hh is not None
        assert retrieved_hh.adults_65 == 1
        if retrieved_hh:
            retrieved_hh.delete()

# (Add more tests as needed to cover different household types and logic paths)
