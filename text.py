import os
from dotenv import load_dotenv
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


# import pymupdf4llm
# print(dir(pymupdf4llm))

from euriai import EuriaiClient
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Get the API key from environment variable
api_key = os.getenv("EURIAI_API_KEY")

if not api_key:
    raise ValueError("EURIAI_API_KEY not found in environment")

client = EuriaiClient(
    api_key=api_key,  # Replace with your actual API key
    model="gpt-4.1-nano"  # You can also try: "gemini-2.0-flash-001", "llama-4-maverick", etc.
)

response = client.generate_completion(
    prompt="List the popluar sports team no matter the sport.",
    temperature=0.7,
    max_tokens=300
)

print(response['choices'][0]['message']['content'])

# from llama_cloud_services import LlamaParse

load_dotenv()
api_key = os.getenv("LLAMA_API_KEY")

if not api_key:
    raise ValueError("LLAMA_API_KEY not found in environment")

# parser = LlamaParse(
#     api_key="api_key",  # can also be set in your env as LLAMA_CLOUD_API_KEY
#     num_workers=4,       # if multiple files passed, split in `num_workers` API calls
#     verbose=True,
#     language="en",       # optionally define a language, default=en
# )

# # sync
# result = parser.parse(r"C:\Users\Admin\Downloads\irc.gov.in.018.2000.pdf")
# markdown_documents = result.get_markdown_documents(split_by_page=True)
# with open("output.md", "w", encoding="utf-8") as f:
#     for doc in markdown_documents:
#         f.write(str(doc) + "\n\n")


# print(result)  # Corrected the syntax by removing the extra (result) at the end
