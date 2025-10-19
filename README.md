# diet_app

Prosty backend Django do zarządzania danymi dietetycznymi.

## Wymagania

- Python 3.x
- PostgreSQL (psql)

## Instalacja

Utwórz środowisko wirtualne i zainstaluj zależności:

```
python -m venv venv
pip install -r requirements.txt
```

## PostgreSQL — szybka konfiguracja

```
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
```


## Uruchomienie aplikacji

Po skonfigurowaniu bazy danych stwórz superużytkownika i uruchom serwer deweloperski:

```
python manage.py createsuperuser

python manage.py runserver
```

## Endpointy i testy

Endpointy są zdefiniowane w `accounts/urls.py`. Duża część logiki została pokryta testami w `accounts/tests.py`.

---
