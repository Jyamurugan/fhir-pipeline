import sqlite3
import logging
from config import SQLITE_DATABASE_PATH as DATABASE_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

create_claims_table_query = """
CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    patient_key TEXT,
    billable_period_start TEXT,
    billable_period_end TEXT,
    provider_key TEXT,
    facility_key TEXT,
    primary_insurer TEXT,
    secondary_insurer TEXT,
    primary_diagnosis TEXT,
    product_or_service TEXT,
    net REAL,
    currency TEXT
)
"""

insert_claim_query = """
INSERT OR REPLACE INTO claims (claim_id, patient_key, billable_period_start, billable_period_end, provider_key, facility_key, primary_insurer, secondary_insurer, primary_diagnosis, product_or_service, net, currency)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
"""

class SQLiteDatabase:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(DATABASE_PATH)
            self.cursor = self.connection.cursor()
            self.cursor.execute(create_claims_table_query)
            self.connection.commit()
            logging.info("Database connection successful")
        except sqlite3.Error as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                logging.info("Database connection closed")
            except sqlite3.Error as e:
                logging.error(f"Failed to close database connection: {e}")
    
    def add_claim(self, claim):
        try:
            self.cursor.execute(insert_claim_query, (
                claim.claim_id,
                claim.patient_key,
                claim.billable_period_start,
                claim.billable_period_end,
                claim.provider_key,
                claim.facility_key,
                claim.primary_insurer,
                claim.secondary_insurer,
                claim.primary_diagnosis,
                claim.product_or_service,
                str(claim.net),
                claim.currency
            ))
            self.connection.commit()
            logging.info("Claim added successfully")
        except sqlite3.Error as e:
            logging.error(f"Failed to add claim: {e}")
            self.connection.rollback()
            raise

    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            logging.info("Query executed successfully")
        except sqlite3.Error as e:
            logging.error(f"Query execution failed: {e}")
            self.connection.rollback()
            raise

    def fetch_all(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            results = self.cursor.fetchall()
            logging.info("Data fetched successfully")
            return results
        except sqlite3.Error as e:
            logging.error(f"Fetching data failed: {e}")
            return None