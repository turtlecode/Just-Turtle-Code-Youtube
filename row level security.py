
import psycopg2
import polars as pl

TARGET_USER = "user_one"  
TARGET_PASSWORD = "password123"
DATABASE_NAME = "postgres" 

def get_db_connection(user, password, dbname):
    """Establishes a direct connection to PostgreSQL for the configured user."""
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"[!] Connection failed for user '{user}': {e}")
        return None
    
def execute_vault_query(connection):
    """Executes the direct SELECT query under the current user session."""
    if not connection:
        return

    sql_query = "SELECT * FROM user_vault;"
    
    try:
        result_df = pl.read_database(sql_query, connection=connection)
        
        print("\n======================================")
        print(f"DATABASE OUTPUT FOR: {TARGET_USER.upper()}")
        print("======================================")
        
        if result_df.is_empty():
            print("No data rows returned.")
        else:
            print(result_df)
            
    except Exception as e:
        print(f"[!] SQL Execution Error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    print(f"[Starting] Initiating session for database user: '{TARGET_USER}'")

    session_conn = get_db_connection(TARGET_USER, TARGET_PASSWORD, DATABASE_NAME)

    execute_vault_query(session_conn)


    '''
    
    -- 1. Create two distinct database users
CREATE ROLE user_one WITH LOGIN PASSWORD 'password123';
CREATE ROLE user_two WITH LOGIN PASSWORD 'password123';

-- 2. Create the target table
CREATE TABLE user_vault (
    id SERIAL PRIMARY KEY,
    owner_name VARCHAR(50) NOT NULL,
    secret_data TEXT NOT NULL
);

-- 3. Insert sample data for both users
INSERT INTO user_vault (owner_name, secret_data) VALUES
('user_one', 'Financial report Q1'),
('user_one', 'API Keys for Project Alpha'),
('user_two', 'Marketing strategy 2026'),
('user_two', 'Customer feedback raw data');

-- 4. Enable Row Level Security on the table
ALTER TABLE user_vault DISABLE ROW LEVEL SECURITY;

-- 5. Create the Policy (The core of RLS)
-- This policy states: A user can only SELECT rows where the 'owner_name' matches their database username (current_user)
 
 CREATE POLICY enforce_user_isolation ON user_vault
    FOR SELECT
    USING (owner_name = current_user);

-- 6. Grant basic SELECT permissions to the users
-- (Without this, RLS won't matter because they won't have access to the table at all)
GRANT SELECT ON user_vault TO user_one, user_two;

select * from user_vault;


   SELECT * FROM user_vault
   WHERE owner_name = current_user_id;









    
    '''