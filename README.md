# myworld

## Background

Having useful fakedata sources can be problematic. It is my aim to create a useful, multifaceted data source that holds synthetic data for a large enough group of people to be relatively representative.

This project generates synthetic demographic data for testing, development, and analytical purposes. It models fully complete households—including accurate geographic and address data, household compositions (e.g., married couples with children, lone parents), and specific individuals matching those compositions with realistic demographic attributes.

## Architecture and Flow

The application executes data generation in a single pass:

1. **Single-Pass Data Generation (`make_household.py`)**
   - The script processes a list of postcodes (from `test_data/postcodes-04`).
   - It looks up each postcode using an external/local Postcode API (`http://localhost:8000/postcodes/`) to gather geographical (latitude/longitude) and administrative (LSOA code) data.
   - It gracefully falls back to generating mock coordinate and district data if the API is unavailable.
   - It randomly assigns a "Household Type" (e.g., "Married couple: Two or more dependent children") based on predefined weights in `household/__init__.py`.
   - It calculates the precise count of household members by age category and gender.
   - Using the `PeopleGenerator` from `make_people.py`, it generates realistic individuals to match the household composition, generating accurate dates of birth relative to today, and assigning matching last names to families.
   - Both the generated `Household` and associated `Person` entities are persisted to the PostgreSQL database in a single pass using **Pony ORM**.

## Technologies Used
- **Python**: Primary language.
- **Pony ORM**: For database modeling and mapping.
- **PostgreSQL**: Standard, authoritative backend database.
- **Faker**: To generate realistic names and dates.
- **Requests**: To query the postcode API.

## Setup Instructions

1. **Database Configuration**
   Ensure PostgreSQL is installed and running. Create a user and database matching the credentials specified in `models.py`:
   ```sql
   CREATE USER chris WITH PASSWORD 'neurologywidget';
   CREATE DATABASE test OWNER chris;
   ALTER USER chris CREATEDB;
   ```
   Alternatively, you can spin up the environment using Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. **Python Environment**
   Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements/requirements.txt
   ```

3. **Running Generation Scripts**
   Ensure your local postcode API is running on port 8000.
   ```bash
   # Generate households and populate individuals in a single pass
   python3 make_household.py
   ```

## Known Improvements and Future Solutions

The codebase implements a functional approach to generating structured synthetic data, but there are several architectural improvements and alternative solutions that could be introduced:

1. **Enhancing the Domain Model**
   - Move away from procedural mapping statements and string comparisons (`res == "One family only..."`) toward object-oriented Factories or the Strategy pattern to encapsulate household structures.
   - Expand `Person` demographic mapping to include constraints, like occupation matching the employment state and realistic household income modeling.
