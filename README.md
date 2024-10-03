# Työturvallisuussovellus vaarojen tunnistamiseen työmaalla (HazardHunt)

<p align="center">
  <a href="https://github.com/Ohtu-Tyoturvallisuus/tts-backend/actions/workflows/main_tts-app.yml" alt="Continuous Integration">
    <img src="https://github.com/Ohtu-Tyoturvallisuus/tts-backend/actions/workflows/main_tts-app.yml/badge.svg"/>
  </a>
  <a href="https://codecov.io/github/Ohtu-Tyoturvallisuus/TTS-backend" > 
    <img src="https://codecov.io/github/Ohtu-Tyoturvallisuus/TTS-backend/graph/badge.svg?token=AA5KQ8B86A"/> 
  </a>
  <a href="https://github.com/Ohtu-Tyoturvallisuus/tts-frontend/blob/main/LICENSE" alt="License">
    <img src="https://img.shields.io/github/license/Ohtu-Tyoturvallisuus/tts-frontend"/>
  </a>
</p>

This project is part of the autumn 2024 Software Engineering project course [TKT20007](https://github.com/HY-TKTL/TKT20007-Ohjelmistotuotantoprojekti/) at the University of Helsinki.

The project aims to develop a mobile application to increase worksite safety by identifying and analyzing possible hazards. This onsite last-minute assessment is meant to be done right before work is commenced and from the perspective of one's work and the work environment.

The [project team](https://github.com/orgs/Ohtu-Tyoturvallisuus/people?query=role%3Aowner) consists of five students.

This is the repository for the backend of this project.
#


## Development

### Links

- **Product Backlog**
  - [Story list](https://github.com/orgs/Ohtu-Tyoturvallisuus/projects/1/views/1)
  - [Task list](https://github.com/orgs/Ohtu-Tyoturvallisuus/projects/1/views/2)
- **Frontend [repository](https://github.com/Ohtu-Tyoturvallisuus/tts-frontend)**
- **[Timelogs](https://study.cs.helsinki.fi/projekti/timelogs)**

### Documentation
- **[Branching practices](https://github.com/Ohtu-Tyoturvallisuus/tts-frontend/blob/main/docs/branching-practices.md)**
- **[Commit practices](https://github.com/Ohtu-Tyoturvallisuus/tts-frontend/blob/main/docs/commit-practices.md)**
- **[Definition of Done](https://github.com/Ohtu-Tyoturvallisuus/tts-frontend/blob/main/docs/definition-of-done.md)**

### Installation and running instructions

#### PostgreSQL Setup and Database Initialization Guide

##### Starting PostgreSQL

Assuming PostgreSQL is installed successfully.

1. **Start PostgreSQL Server**:
   - **On Windows**: Should be running by default. If not open the Services app (`services.msc`), find `PostgreSQL`, and start the service.
   - **On macOS**: Use Homebrew services with the command:
     ```bash
     brew services start postgresql
     ```
   - **On Linux**: Use the system service manager:
     ```bash
     sudo systemctl start postgresql
     ```

##### Creating a Database

1. **Open PostgreSQL Command Line**:
   - Run `psql` in your terminal or command prompt:
     ```bash
     psql -U postgres
     ```

2. **Create the Database**:
   - Run the following SQL command to create the `tts_testing` database:
     ```sql
     CREATE DATABASE tts_testing;
     ```

3. **Connect to the Database**:
   - Connect to the `tts_testing` database:
     ```sql
     \c tts_testing
     ```

##### Applying the Schema

1. **Run the Schema File**:
   - Execute the SQL commands in `schema.sql` to set up the database schema:
     ```bash
     \i path/to/schema.sql
     ```
2. **(Optional: Populate with populate_data.sql=**:
   ```bash
     \i path/to/populate_data.sql
     ```

##### Verification

1. **Verify Tables**:
   - List tables in the `my_app` schema:
     ```bash
     \dt
     ```

2. **Check Table Structure**:
   - Describe a table structure:
     ```bash
     \d <table_name>
     ```

---


##### Setting Up Django with PostgreSQL

1. **Ensure Poetry is Installed**:
    - If you don't have Poetry installed, install it from the official Poetry website: [Poetry Installation](https://python-poetry.org/docs/).

2. **Install Dependencies Using Poetry**:
    - Install dependencies by running the command:
         ```bash
         poetry install
         ```
    - Move to virtual environment:
        ```bash
         poetry shell
         ```

3. **Set Up Environment Variables**:
   - Create a `.env` file in the root of your project with the following content (adjust values as needed):
     ```bash
     # .env
     SECRET_KEY=secret_key
     DB_NAME=tts_testing
     DB_USER=postgres
     DB_PASSWORD=your_password
     DB_HOST=localhost
     ```
   - To generate a new Django `SECRET_KEY`, run the following command:
     ```bash
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```
   
4. **Run Migrations**:
   - Apply the database migrations:
     ```bash
     poetry run invoke migrate
     ```

5. **Start the Server**:
   - Run the Django development server:
     ```bash
     poetry run invoke server
     ```
