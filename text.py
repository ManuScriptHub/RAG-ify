# import psycopg2

# def check_db_connection():
#     """
#     Tries to connect to the DB and returns the connection object if successful.
#     Does NOT close the connection here, so we can use it in 'data()'.
#     """
#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             database="RAG-ify",
#             user="postgres",
#             password="radhe",
#             port=5432,
#         )
#         print("Success! Connected to the database.")
#         return conn
#     except Exception as e:
#         print("Failed to connect:", e)
#         return None

# def data():
#     """
#     Calls 'check_db_connection()', uses the returned connection to query "Users",
#     prints out the rows, and then closes the connection.
#     """
#     conn = check_db_connection()
#     if not conn:
#         return  # If connection is None, we can't do anything else

#     try:
#         cur = conn.cursor()
        
#         # If your table name is literally CREATE TABLE "Users" (...), 
#         # then you need double quotes around Users here.
#         # If your table is just users (no quotes in CREATE TABLE), then use: SELECT * FROM users;
#         cur.execute('SELECT * FROM "Users";')
        
#         rows = cur.fetchall()  # fetch all results
#         print("Rows from Users table:", rows)

#     except Exception as e:
#         print("Query error:", e)
#     finally:
#         # Close the DB connection after we're done
#         if conn:
#             conn.close()
#             print("Connection closed.")

# if __name__ == "__main__":
#     data()


tup = ("ff", "fff")
print(dict(tup))



[('660dd35c004a4843bfca4d0ba3600da0', 'manu', 'm@outlook.com', 'read', datetime.datetime(2025, 4, 4, 18, 52, 39, 136514, tzinfo=datetime.timezone(datetime.timedelta(seconds=19800))), datetime.datetime(2025, 4, 4, 18, 52, 39, 136514, tzinfo=datetime.timezone(datetime.timedelta(seconds=19800))))]