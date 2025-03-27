import psycopg2
import psycopg2.extras
from flask import current_app
from datetime import datetime

def get_db_connection():
    """
    Create a direct connection to the PostgreSQL database.
    This bypasses Flask-SQLAlchemy completely to avoid app context issues.
    """
    # Get the DB connection parameters from the environment variable
    # In Docker, this will use the container-network connection
    host = "db"  # Container name from docker-compose
    port = 5432  # Default PostgreSQL port
    user = "admin"
    password = "dpSVtoZUjmyXAXWo6LfLe3NgzZQHPqvt3POhmMPTU2U"
    database = "database"
    
    # Create and return the connection
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    
    # Set the connection to automatically convert PostgreSQL arrays to Python lists
    psycopg2.extras.register_default_jsonb(globally=True, loads=lambda x: x)
    
    # Return a connection with a DictCursor for easier column access
    return connection, connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

def close_connection(connection, cursor):
    """Safely close a database connection and cursor."""
    if cursor:
        cursor.close()
    if connection:
        connection.close()

def get_report(report_id):
    """Get a report by ID using direct database access."""
    conn, cursor = get_db_connection()
    try:
        cursor.execute(
            "SELECT id, patient_id, filepath, filetype, summary FROM reports WHERE id = %s",
            (report_id,)
        )
        report = cursor.fetchone()
        return report
    finally:
        close_connection(conn, cursor)

def update_report_summary(report_id, summary):
    """Update a report's summary using direct database access."""
    conn, cursor = get_db_connection()
    try:
        cursor.execute(
            "UPDATE reports SET summary = %s WHERE id = %s",
            (summary, report_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error updating report summary: {str(e)}")
        return False
    finally:
        close_connection(conn, cursor)

def store_seizure(patient_id, day, start_time, duration, electrodes):
    """Store a seizure and its electrodes using direct database access."""
    conn, cursor = get_db_connection()
    try:
        # Convert time string to time object if needed
        if isinstance(start_time, str):
            try:
                start_time = datetime.strptime(start_time, "%H:%M:%S").time()
            except ValueError:
                start_time = None
        
        # Insert seizure
        cursor.execute(
            """
            INSERT INTO seizures 
            (patient_id, day, start_time, duration, created_at, modified_at) 
            VALUES (%s, %s, %s, %s, NOW(), NOW()) 
            RETURNING id
            """,
            (patient_id, day, start_time, duration)
        )
        seizure_id = cursor.fetchone()[0]
        
        # Process electrodes
        if electrodes:
            for electrode_name in electrodes:
                # Skip empty names
                if not electrode_name or not isinstance(electrode_name, str):
                    continue
                    
                # Find or create electrode
                cursor.execute(
                    "SELECT id FROM electrodes WHERE name = %s", 
                    (electrode_name,)
                )
                electrode_row = cursor.fetchone()
                
                if electrode_row:
                    electrode_id = electrode_row[0]
                else:
                    cursor.execute(
                        """
                        INSERT INTO electrodes 
                        (name, created_at, modified_at) 
                        VALUES (%s, NOW(), NOW()) 
                        RETURNING id
                        """,
                        (electrode_name,)
                    )
                    electrode_id = cursor.fetchone()[0]
                
                # Create association
                cursor.execute(
                    """
                    INSERT INTO seizure_electrode_association 
                    (seizure_id, electrode_id) 
                    VALUES (%s, %s)
                    """,
                    (seizure_id, electrode_id)
                )
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error storing seizure: {str(e)}")
        return False
    finally:
        close_connection(conn, cursor)

def store_drug(patient_id, drug_name, day, dosage):
    """Store a drug administration using direct database access."""
    conn, cursor = get_db_connection()
    try:
        # Ensure drug name is a string
        drug_name = str(drug_name).lower() if drug_name else ""
        if not drug_name:
            return False
            
        # Convert dosage to integer
        try:
            dosage = int(dosage)
        except (ValueError, TypeError):
            dosage = 0
            
        # Find or create drug
        cursor.execute(
            "SELECT id FROM drugs WHERE name = %s", 
            (drug_name,)
        )
        drug_row = cursor.fetchone()
        
        if drug_row:
            drug_id = drug_row[0]
        else:
            cursor.execute(
                """
                INSERT INTO drugs 
                (name, created_at, modified_at) 
                VALUES (%s, NOW(), NOW()) 
                RETURNING id
                """,
                (drug_name,)
            )
            drug_id = cursor.fetchone()[0]
        
        # Create administration record
        cursor.execute(
            """
            INSERT INTO drug_administration 
            (patient_id, drug_id, day, dosage, created_at, modified_at) 
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            """,
            (patient_id, drug_id, day, dosage)
        )
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error storing drug: {str(e)}")
        return False
    finally:
        close_connection(conn, cursor)