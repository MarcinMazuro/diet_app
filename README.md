# diet_app

python -m venv venv
pip install -r requirements.txt

intall psql, nie pamietam jak, tym bardziej na windowsie

sudo -u postgres psql (nie wiem jak na windowsie)

i po kolei:
    CREATE DATABASE diet_db;
    CREATE USER diet_user WITH PASSWORD 'password';
    ALTER ROLE diet_user SET client_encoding TO 'utf8';
    ALTER ROLE diet_user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE diet_user SET timezone TO 'UTC';
    
    \c diet_db
    GRANT ALL ON SCHEMA public TO diet_user;
    GRANT ALL ON DATABASE diet_db TO diet_user;
    ctrl + d

python manage.py createsuperuser

python manage.py runserver
