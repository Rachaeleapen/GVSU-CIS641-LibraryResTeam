
import os
import psycopg

def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname="library_reservation",
        user="postgres",
        password=os.environ["DB_PASSWORD"]
    )
