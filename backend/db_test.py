import psycopg2
import sys

def test_connection():
    try:
        # Test connection
        conn = psycopg2.connect(
            host="localhost",
            database="posturetrackdatabase",
            user="posturetrackdatabase_user", 
            password="posturetrack123",
            port="5432"
        )
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT 'Database connection successful!' as message;")
        result = cur.fetchone()
        print(f"✅ {result[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("🎉 Database is ready for the application!")
    else:
        print("🚨 Fix database connection before proceeding")
        sys.exit(1)