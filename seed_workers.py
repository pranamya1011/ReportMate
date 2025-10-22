import MySQLdb

# MySQL connection configuration - update if needed
db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="mySqlroot@1011",
    db="user_auth_db"
)

cursor = db.cursor()

# Updated workers data without skills column
workers = [
    ("John Doe", "Mangalore"),               
    ("Ian Red", "Sullia"),      
    ("Jane Smith", "Mangalore"),                  
    ("George Black", "Bantwal"),
    ("Fiona Green", "Puttur"),                
    ("Hannah Blue", "Moodabidri"),   
    ("Michael Scott", "Mangalore"),
    ("Pam Beesly", "Mangalore"),
    ("Stanley Hudson", "Mangalore"),
    ("Michael Scott", "Puttur")
]

# Insert workers into the workers table without skills column
for name, location in workers:
    cursor.execute(
        "INSERT INTO workers (name, location) VALUES (%s, %s)",
        (name, location)
    )

db.commit()
cursor.close()
db.close()

print("Updated sample workers inserted successfully.")
