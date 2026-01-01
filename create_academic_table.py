"""
Script to create the academic_performance table.
Run this script to create the table if it doesn't exist.
"""

import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_academic_table():
    """Create academic_performance table."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DB', 'learnsmart_ai'),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        cursor = conn.cursor()
        
        print("Creating academic_performance table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_performance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                class_semester VARCHAR(100) NOT NULL,
                exam_name VARCHAR(100) NOT NULL,
                subject_name VARCHAR(100) NOT NULL,
                marks_scored DECIMAL(6,2) NOT NULL,
                total_marks DECIMAL(6,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_class_semester (user_id, class_semester)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ academic_performance table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {str(e)}")
        print("\nPossible issues:")
        print("1. MySQL server is not running")
        print("2. Database 'learnsmart_ai' does not exist")
        print("3. Users table doesn't exist (must create users table first)")
        print("4. Wrong MySQL credentials in .env file")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Academic Performance Table Initialization")
    print("=" * 50)
    print()
    
    success = create_academic_table()
    
    if success:
        print("\n✅ You can now use the Academic Performance Tracker feature!")
    else:
        print("\n❌ Please check the error message above and try again.")

