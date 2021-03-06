# whid API

[![Maintainability](https://api.codeclimate.com/v1/badges/8ecac46265974fd06f52/maintainability)](https://codeclimate.com/github/benrucker/whid-api/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/8ecac46265974fd06f52/test_coverage)](https://codeclimate.com/github/benrucker/whid-api/test_coverage)
![action](https://github.com/benrucker/whid-api/actions/workflows/main.yml/badge.svg)
[![Known Vulnerabilities](https://snyk.io/test/github/benrucker/whid-api/badge.svg)](https://snyk.io/test/github/benrucker/whid-api/)

This project is a secret API.

# Usage

1. Install Python 3.10 or higher
2. Install `pip` if you don't have it
3. Open a terminal and clone this repo
```sh
git clone https://github.com/benrucker/whid-api
```
4. `cd` into the repo
```sh
cd whid-api
```
5. Create and activate a virtual environment
```ps
# Windows:
python -m pip install venv
python -m venv .venv
.\\.venv\\Scripts\\activate
```
```sh
# Mac and Linux:
python3 -m pip install venv
python3 -m venv .venv
. .venv/bin/activate
```
6. Install the requirements
```sh
python -m pip install -r requirements.txt
```
7. Create a file named `.env` in the root directory of the repo
8. Add in values for `DB_URL` and `API_TOKENS`. For example:
```
DB_URL="sqlite:///./sql_app.db"
API_TOKENS=["hello"]
```
9. Run the app
```sh
# dev
uvicorn api.main:app --reload
```
```sh
# production
./run
```
10. View the documentation at http://127.0.0.1:8000/docs

## Using `alembic`

When a change has been made to the DB schema, you need to use `alembic` to update the production database. To do this:

1. `cd` to the project folder
2. `git pull` or run `./update`
3. Generate a new almebic checkpoint: `alembic revision --autogenerate -m "<What was changed>"`
4. Update the db: `alembic upgrade head`
    - If you get an error with null values, update the revision script like this:
    ```py
    # old:
    op.add_column('channel', sa.Column('type', sa.String(), nullable=True))
    ```
    ```py
    # fixed:
    op.add_column('channel', sa.Column('type', sa.String()))
    op.execute('update channel set type = \'text\'')
    op.alter_column('channel', 'type', nullable=False)
    ```
    - Rerun the update command
5. If not done already, `HUP` the running process with `./update`