import sqlite3

DB_NAME = "questions.db"
#get an api key

#def denotes new function in python, indentation is like your curly braces
def createdb():
    #when creating database in sqlite you need to "open a connection"
    #this line will basically open up a file for the database if it doesnt alrdy exist
    conn = sqlite3.connect(DB_NAME)
    #a cursor is practically a pointer that lets us execute commands after opening the db
    c = conn.cursor()
    #.execute is how you tell the db to do something
    #triple quotes for denoting multi string code in python, makes it neater
    #commanding db to create a db table if it doesnt alrdy exist and call it questions
    #give each item in this db unique property, name of property then its type
    #thisll keep track of the questions and its data
    c.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        question TEXT,
        correctAns TEXT,
        wrongAns TEXT
    )
    """ 
    )

    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO categories (name) VALUES (?)",
                    [("Math",), ("Computer Science",)])


    #if i wanna keep track of the progress of the user ill also need info on questions they got wrong
    c.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        question TEXT,
        result INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    )
    #select count from questions counts the number of rows in the questions table
    #we trynna see if the db is empty so we can add questns jst in case
    #fetch one will check the first row of the db, if there is nothing there it inputs the questns
    c.execute("SELECT COUNT(*) FROM questions")
    if c.fetchone()[0] == 0:
        sampleData = [
            ("Math", "What is 5*5?", "25", "20,30,15"),
            ("Math", "What is 7*7?", "49", "41,42,56"),
            ("Computer Science", "What does CPU stand for?", "Central Processing Unit", "Computer Power Unit,Core Process Utility"),
        ]
        #inserting questions multiple times so we use execute many
        #???? is a palceholder so no one inserts malicious links to our db 
        c.executemany("INSERT INTO questions (subject, question, correctAns, wrongAns) VALUES (?,?,?,?)", sampleData)
        #commits changes to db
        conn.commit()
    #close the connection to db
    conn.close()
