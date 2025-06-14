import pytest
from unittest.mock import patch, MagicMock, call
from uuid import uuid4
from datetime import date, datetime

from models import db, Household, Person
from pony.orm import db_session, select, count, commit

# Import the function to test
from make_people import populate_people, create_person_entity
# We might also test create_person_entity directly for finer-grained unit tests later if needed

# Simplified DB fixture, assumes DB is set up by models.py
# Tests should clean up their own created data.
@pytest.fixture(scope="function")
def db_cleanup():
    # Yield and then clean up. This ensures cleanup even if test fails.
    # Store IDs of created households and persons to delete them specifically.
    created_household_ids = []
    created_person_ids = []
    yield created_household_ids, created_person_ids # Test can append IDs here
    # Cleanup
    with db_session:
        # Delete persons first due to foreign key constraints
        # Iterate a few times in case of complex relationships or if order matters and is not explicit
        for _ in range(2): # Simple retry mechanism for deletion
            persons_to_delete = Person.select(lambda p: p.person_UUID in created_person_ids)
            if not persons_to_delete.exists():
                break
            for p_obj in list(persons_to_delete): # Convert to list before iterating and deleting
                 p_obj.delete()
            commit()

        for hid in created_household_ids:
            h = Household.get(household_UUID=hid)
            if h:
                # Ensure related persons are deleted before deleting household
                persons_in_hh = Person.select(lambda p: p.household.household_UUID == hid)
                for p_obj in list(persons_in_hh):
                     p_obj.delete()
                commit()
                h.delete()
        commit() # Ensure deletions are committed

@patch('people.nationality.country_name', return_value='en_GB') # Mock nationality
@patch('people.age.dob_working_age', side_effect=[(date(1990, 1, 1), 34), (date(1992, 1, 1), 32)]) # Mock ages
def test_populate_married_couple_no_children(mock_dob_working_age, mock_nationality, db_cleanup):
    created_h_ids, created_p_ids = db_cleanup
    household_id = str(uuid4())
    created_h_ids.append(household_id)

    with db_session:
        test_hh = Household(
            household_UUID=household_id,
            type="One family only: Married couple: No children",
            adults_m=1, adults_f=1, adults_65=0, children_total=0, non_dep=0, married=True,
            postcode="MCNCTEST", lat=50.0, long=0.0, admin_district="Test", cd_lsoa="TestLSOA"
        )
        # commit() # commit is implicit with db_session at the end of the block if not using with existing objects

    # Run the person population logic
    populate_people()

    with db_session:
        persons_in_hh = list(Person.select(lambda p: p.household.household_UUID == household_id))
        created_p_ids.extend([p.person_UUID for p in persons_in_hh]) # For cleanup

        assert len(persons_in_hh) == 2

        male_adults = [p for p in persons_in_hh if p.gender == "Male" and p.is_adult]
        female_adults = [p for p in persons_in_hh if p.gender == "Female" and p.is_adult]

        assert len(male_adults) == 1
        assert len(female_adults) == 1

        # Check if they share a last name
        assert male_adults[0].last_name == female_adults[0].last_name
        assert male_adults[0].age == 34 # From mock
        assert female_adults[0].age == 32 # From mock
        assert male_adults[0].household.household_UUID == household_id
        assert female_adults[0].household.household_UUID == household_id

# Mocking random.choice for gender of children, and other necessary mocks
@patch('random.choice', side_effect=['Male', 'Female']) # Child1=Male, Child2=Female
@patch('people.nationality.country_name', return_value='en_US')
@patch('people.age.dob_working_age', side_effect=[(date(1988, 5, 5), 36), (date(1989, 6, 6), 35)])
@patch('people.age.dob_under18', side_effect=[(date(2010, 7, 7), 14), (date(2012, 8, 8), 12)])
def test_populate_couple_with_children(mock_dob_u18, mock_dob_wa, mock_nat, mock_rand_choice, db_cleanup):
    created_h_ids, created_p_ids = db_cleanup
    household_id = str(uuid4())
    created_h_ids.append(household_id)

    with db_session:
        test_hh = Household(
            household_UUID=household_id,
            type="One family only: Married couple: Two or more dependent children",
            adults_m=1, adults_f=1, adults_65=0, children_total=2, non_dep=0, married=True,
            postcode="CWCTEST", lat=51.0, long=0.1, admin_district="TestC", cd_lsoa="TestLSOAC"
        )
        # commit()

    populate_people()

    with db_session:
        persons_in_hh = list(Person.select(lambda p: p.household.household_UUID == household_id))
        created_p_ids.extend([p.person_UUID for p in persons_in_hh])

        assert len(persons_in_hh) == 4 # 2 adults + 2 children

        adults = [p for p in persons_in_hh if p.is_adult]
        children = [p for p in persons_in_hh if not p.is_adult]

        assert len(adults) == 2
        assert len(children) == 2

        # Assuming adults share a last name, and children inherit it
        family_last_name = adults[0].last_name
        assert all(p.last_name == family_last_name for p in persons_in_hh)

        assert children[0].gender == 'Male' # From mock_rand_choice
        assert children[1].gender == 'Female'# From mock_rand_choice
        assert children[0].age == 14 # From mock_dob_u18
        assert children[1].age == 12 # From mock_dob_u18

@patch('people.nationality.country_name', return_value='de_DE')
@patch('people.age.dob_over65', side_effect=[(date(1950, 1, 1), 74), (date(1945,1,1), 79)]) # 2 over 65
@patch('people.age.dob_working_age', return_value=(date(1995, 1, 1), 29)) # For non-dependent
@patch('random.choice', side_effect=['Female', 'Male', 'Female']) # Genders for over65s then non-dep
def test_populate_complex_household_over65_nondep(mock_rand_choice_gender, mock_dob_wa_nd, mock_dob_o65, mock_nat_co, db_cleanup):
    created_h_ids, created_p_ids = db_cleanup
    household_id = str(uuid4())
    created_h_ids.append(household_id)

    with db_session:
        # A household with only over-65s and one non-dependent adult (e.g. a carer)
        test_hh = Household(
            household_UUID=household_id,
            type="Mixed: Over 65 and Non-Dependent", # This type string is for test description, not specific logic in make_people
            adults_m=0, adults_f=0, adults_65=2, children_total=0, non_dep=1, married=False, # Not married
            postcode="MIXTEST", lat=52.0, long=0.2, admin_district="TestM", cd_lsoa="TestLSOAM"
        )
        # commit()

    populate_people()

    with db_session:
        persons_in_hh = list(Person.select(lambda p: p.household.household_UUID == household_id))
        created_p_ids.extend([p.person_UUID for p in persons_in_hh])

        assert len(persons_in_hh) == 3 # 2 over-65 + 1 non-dependent

        over_65s = sorted([p for p in persons_in_hh if p.age >= 65], key=lambda x: x.date_of_birth) # sort to match side_effect order
        non_deps = [p for p in persons_in_hh if 18 <= p.age < 65]

        assert len(over_65s) == 2
        assert len(non_deps) == 1

        # Note: The order of generation for over_65s is not guaranteed if not sorted.
        # random.choice is mocked for gender. The order of gender assignment will match the side_effect list.
        # First over_65 generated gets gender 'Female', second gets 'Male'.

        # To make assertions reliable, we should sort the persons list or assign specific characteristics
        # if the generation order within the loop for over_65s in populate_people isn't fixed.
        # For now, assuming generate_persons_for_household processes them in a consistent order or that the mocks line up.
        # Let's ensure genders match the mocked `random.choice` sequence.
        # The mock `random.choice` is called for each over-65, then for each non-dependent.

        # Check over_65s based on their mocked DoB/age and assigned gender
        # side_effect for dob_over65 was [(1950 (74yo), (1945 (79yo))]
        # side_effect for random.choice (gender) was ['Female', 'Male', 'Female']
        # So, 74yo should be Female, 79yo should be Male.

        person_74 = next(p for p in over_65s if p.age == 74)
        person_79 = next(p for p in over_65s if p.age == 79)

        assert person_74.gender == 'Female'
        assert person_79.gender == 'Male'

        assert non_deps[0].gender == 'Female' # Third gender from mock_rand_choice_gender
        assert non_deps[0].age == 29

        # Check if surnames are different (as married=False, and non-dep is separate)
        # The logic in make_people for common_last_name for over_65s if married=False is None.
        # Non-dependents also get common_last_name=None.
        # So all 3 should have different last names.
        surnames = {p.last_name for p in persons_in_hh}
        assert len(surnames) == 3, f"Expected 3 different surnames, got {len(surnames)}: {surnames}"

def test_populate_people_with_no_households(db_cleanup):
    # db_cleanup ensures tables are clean or test data is managed
    # No households are created for this test.

    # Ensure no households exist that match populate_people's criteria.
    # The populate_people function queries for households with `h.type != None and h.type != ""`.
    # So, a completely empty Household table, or households with type=None or type="" will satisfy this.
    # The db_cleanup fixture should ensure previous test data is removed.
    # For safety, we can explicitly delete any remaining households if necessary,
    # but typically tests should be independent.
    with db_session:
        # Optional: Explicitly delete any households that might linger if cleanup failed or wasn't thorough.
        # Household.select().delete(bulk=True)
        # commit()
        pass


    initial_person_count = 0
    with db_session:
        initial_person_count = count(p for p in Person)

    # Run the person population logic
    populate_people() # Should not find any households to process

    with db_session:
        final_person_count = count(p for p in Person)
        assert final_person_count == initial_person_count, "No persons should be created if there are no households"
