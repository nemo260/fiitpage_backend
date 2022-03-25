import environ
import psycopg2

# .env file must be in api folder

env = environ.Env()
environ.Env.read_env()
conn = psycopg2.connect(database=env('db_name'), user=env('db_user'),
                        password=env('db_password'), host=env('db_host'),
                        port=env('db_port'))
cur = conn.cursor()