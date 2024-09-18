**You can find the frontend repo [here](https://github.com/Ohtu-Tyoturvallisuus/TTS-frontend)**

# PostgreSQL Setup and Database Initialization Guide

## Starting PostgreSQL

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

## Creating a Database

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

## Applying the Schema

1. **Run the Schema File**:
   - Execute the SQL commands in `schema.sql` to set up the database schema:
     ```bash
     \i path/to/schema.sql
     ```
2. **(Optional: Populate with populate_data.sql=**:
   ```bash
     \i path/to/populate_data.sql
     ```

## Verification

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


## Setting Up Django with PostgreSQL

1. **Set Up Virtual Environment**:
   - Create and activate a virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```

2. **Install Dependencies**:
   - Use pip to install the dependencies listed in `requirements.txt`:
     ```bash
     pip install -r requirements.txt
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
     python manage.py migrate
     ```

5. **Start the Server**:
   - Run the Django development server:
     ```bash
     python manage.py runserver
     ```
