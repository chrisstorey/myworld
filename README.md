# myworld

## Background

Having useful fakedata sources can be problematic. It is my aim to create a useful, multifaceted data source that holds synthetic data for a large enough group of people to be relatively representative.

This project generates synthetic demographic data for testing, development, and analytical purposes. It models fully complete households—including accurate geographic and address data, household compositions (e.g., married couples with children, lone parents), and specific individuals matching those compositions with realistic demographic attributes.

## Architecture and Flow

The application divides data generation into two primary steps:

1. **Household Generation (`make_household.py`)**
   - The script processes a list of postcodes (from `test_data/postcodes-04`).
   - It looks up each postcode using an external/local Postcode API (`http://localhost:8000/postcodes/`) to gather geographical (latitude/longitude) and administrative (LSOA code) data.
   - It randomly assigns a "Household Type" (e.g., "Married couple: Two or more dependent children") based on predefined weights in `household/__init__.py`.
   - It calculates the precise count of household members by age category and gender.
   - The resulting `Household` entity is persisted to a PostgreSQL database using **Pony ORM**.

2. **People Generation (`make_people.py`)**
   - This script reads the previously generated `Household` entities from the PostgreSQL database.
   - For each household, it iterates over the expected demographics (number of male/female adults, children, seniors, etc.).
   - It generates realistic attributes for each individual using the `Faker` library, including an accurate Date of Birth (`dob`) relative to today, nationality, and gender-appropriate names.
   - It correctly links family members (e.g., children and married couples share a common last name).
   - The resulting `Person` entities are linked to their parent `Household` and persisted back to the database.

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
   # Generate households
   python3 make_household.py

   # Populate individuals inside generated households
   python3 make_people.py
   ```

## Known Improvements and Future Solutions

The codebase implements a functional approach to generating structured synthetic data, but there are several architectural improvements and alternative solutions that could be introduced:

1. **Unified Configuration Management**
   - **Current State:** Configuration is fragmented between `models.py` (hardcoded credentials), `config/config.yml` (partially used), and `main.py`.
   - **Improvement:** Adopt a robust configuration system (like `pydantic-settings` or `python-decouple`) that manages environment variables via a `.env` file, allowing seamless switching between local, testing, and production PostgreSQL databases.

2. **Postcode API Dependency Refactoring**
   - **Current State:** `make_household.py` relies on a synchronous HTTP request to `http://localhost:8000` to fetch geolocation data per postcode. This significantly slows down generation and introduces an external point of failure.
   - **Alternative Solution:** Utilize a local CSV or SQLite database containing postcode mappings directly in the project. If an API is required, replace synchronous requests with asynchronous requests using `aiohttp` or `httpx` to speed up bulk generation.

3. **Single-Pass Data Generation**
   - **Current State:** Generation is decoupled into two scripts (`make_household` then `make_people`), meaning we query the API, insert households to Postgres, immediately read the same households back, and then insert individuals.
   - **Alternative Solution:** Use an integrated pipeline. Generate a household layout, immediately generate the corresponding individuals in memory, and commit the complete hierarchy to PostgreSQL in a single atomic database transaction. This ensures stronger referential integrity and reduces database roundtrips.

4. **Enhancing the Domain Model**
   - Move away from procedural mapping statements and string comparisons (`res == "One family only..."`) toward object-oriented Factories or the Strategy pattern to encapsulate household structures.
   - Expand `Person` demographic mapping to include constraints, like occupation matching the employment state and realistic household income modeling.
