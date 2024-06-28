import mysql.connector
from mysql.connector import errorcode
from email.mime.text import MIMEText
import smtplib
import datetime
cnx = None
def connect_to_database():
    global cnx
    try:
        cnx = mysql.connector.connect(
            user='root',
            password='12345',
            host='localhost',
            port=3306,
            database='election2024'
        )
        print("Connected to the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
def create_tables(cursor):
    cursor.execute("DROP TABLE IF EXISTS votes")
    cursor.execute("DROP TABLE IF EXISTS voters")
    cursor.execute("DROP TABLE IF EXISTS candidates")
    queries = [
        """CREATE TABLE candidates (
               id INT AUTO_INCREMENT PRIMARY KEY,
               name VARCHAR(255) NOT NULL,
               party VARCHAR(255) NOT NULL
           )""",
        """CREATE TABLE voters (
               id INT AUTO_INCREMENT PRIMARY KEY,
               username VARCHAR(255) NOT NULL,
               vote_id VARCHAR(255) NOT NULL,
               address VARCHAR(255) NOT NULL,
               age INT NOT NULL,
               candidate_id INT,
               FOREIGN KEY (candidate_id) REFERENCES candidates(id)
           )""",
        """CREATE TABLE votes (
               id INT AUTO_INCREMENT PRIMARY KEY,
               candidate_id INT,
               voter_name VARCHAR(255) NOT NULL,
               email VARCHAR(255) NOT NULL,
               vote_date DATETIME NOT NULL,
               FOREIGN KEY (candidate_id) REFERENCES candidates(id)
           )"""
    ]
    for query in queries:
        cursor.execute(query)
def insert_candidates(cursor):
    candidates = [
        ("Murasoli.S", "DMK"),
        ("Saravanan .M", "ADMK"),
        ("Muruganantham .M", "BJP"),
        ("Humayun Kabir", "Naam Tamilar Katchi")
    ]
    for candidate in candidates:
        cursor.execute("INSERT INTO candidates (name, party) VALUES (%s, %s)", candidate)
def send_email(subject, message, receiver_email):
    sender_email = 'your_email@example.com'
    password = 'your_email_password'
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
def insert_voter(cursor, username, vote_id, address, age, candidate_id):
    add_voter = ("INSERT INTO voters (username, vote_id, address, age, candidate_id) VALUES (%s, %s, %s, %s, %s)")
    voter_data = (username, vote_id, address, age, candidate_id)
    cursor.execute(add_voter, voter_data)
    print("Voter added successfully.")
def cast_vote(cursor, candidate_id, voter_name, email):
    try:
        vote_date = datetime.datetime.now()
        cursor.execute("INSERT INTO votes (candidate_id, voter_name, email, vote_date) VALUES (%s, %s, %s, %s)",
                       (candidate_id, voter_name, email, vote_date))
        print("Vote cast successfully!")
        send_email("Vote Confirmation", "Thank you for voting! Your vote has been successfully registered.", email)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        cnx.rollback()
def get_candidate_votes(cursor, candidate_id):
    try:
        cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate_id = %s", (candidate_id,))
        return cursor.fetchone()[0]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
def validate_age(age):
    try:
        age = int(age)
        if age < 18:
            raise ValueError("Age must be 18 or above.")
        return age
    except ValueError:
        raise ValueError("Invalid age. Please enter a valid integer.")
def main():
    print("Welcome to the Thanjavur Election 2024!\n")
    connect_to_database()
    if cnx:
        cursor = cnx.cursor()
        create_tables(cursor)
        insert_candidates(cursor)
        cnx.commit()
        cursor.execute("SELECT id, name, party FROM candidates")
        candidates = cursor.fetchall()
        print("Candidate ID\tCandidate Names\t\tParty")
        print("-" * 40)
        for candidate in candidates:
            print(f"{candidate[0]}\t\t{candidate[1].ljust(20)}{candidate[2]}")
        try:
            while True:
                choice = input("To add more votes, enter 1. To exit, enter 0: ")
                if choice == '0':
                    break
                elif choice == '1':
                    username = input("Enter username: ")
                    vote_id = input("Enter vote ID: ")
                    address = input("Enter address: ")
                    age = input("Enter age: ")
                    age = validate_age(age)
                    candidate_id = int(input("Enter the candidate ID you want to vote for: "))
                    insert_voter(cursor, username, vote_id, address, age, candidate_id)
                    receiver_email = input("Enter your email address for confirmation: ")
                    cast_vote(cursor, candidate_id, username, receiver_email)
                    cnx.commit() 
                    current_datetime = datetime.datetime.now()
                    file_text = (f"Election Program Details\nDate and Time: {current_datetime}\n"
                                 f"User Details:\nUsername: {username}\nVote ID: {vote_id}\n"
                                 f"Address: {address}\nAge: {age}\n")
                    with open(f"election_details_{current_datetime.strftime('%Y-%m-%d_%H-%M-%S')}.txt", 'w') as file:
                        file.write(file_text)
                else:
                    print("Invalid choice. Please enter 0 or 1.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cursor.close()  
            cnx.close()  
if __name__ == "__main__":
    main()
