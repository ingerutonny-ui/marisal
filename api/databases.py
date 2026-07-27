import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://neondb_owner:npg_j9qwPYO4lHnM@ep-fragrant-base-axtstsvs-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
