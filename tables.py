import mysql.connector
from mysql.connector import errorcode
def connect_to_database():
    try:
        cnx = mysql.connector.connect(
            user='root',
            password='12345',
            host='localhost',
            port=3306,
            database='election2024'
        )
        print("Connected to the database.")
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        elif err.errno == errorcode.CR_CONNECTION_ERROR:
            print("Cannot connect to the database server. Ensure it is running and accessible.")
        else:
            print(err)
        return None
def get_candidate_votes(cursor, candidate_id):
    cursor.execute("SELECT COUNT(*) FROM votes WHERE candidate_id = %s", (candidate_id,))
    result = cursor.fetchone()
    return result[0] if result else 0
def show_data(cursor):
    print("\nCandidates Table:")
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    print("ID\tName\t\t\tParty\t\tVotes")
    print("-" * 50)
    total_votes = 0
    for candidate in candidates:
        votes = get_candidate_votes(cursor, candidate[0])
        total_votes += votes
        print(f"{candidate[0]}\t{candidate[1].ljust(20)}{candidate[2].ljust(20)}{votes}")
    print("\nTotal Votes Cast:", total_votes)
    print("\nVoters Table:")
    cursor.execute("SELECT * FROM voters")
    voters = cursor.fetchall()
    print("ID\tUsername\tVote ID\t\tAddress\t\tAge\tCandidate ID")
    print("-" * 60)
    for voter in voters:
        print(f"{voter[0]}\t{voter[1].ljust(10)}\t{voter[2]}\t{voter[3].ljust(15)}\t{voter[4]}\t{voter[5]}")
    print("\nVotes Table:")
    cursor.execute("SELECT * FROM votes")
    votes = cursor.fetchall()
    print("ID\tCandidate ID\tVoter Name\tEmail\t\t\t\tVote Date")
    print("-" * 80)
    for vote in votes:
        print(f"{vote[0]}\t{vote[1]}\t\t{vote[2].ljust(10)}\t{vote[3].ljust(25)}\t{vote[4]}")
def main():
    cnx = connect_to_database()
    if cnx:
        cursor = cnx.cursor()
        try:
            show_data(cursor)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cursor.close()
            cnx.close()
if __name__ == "__main__":
    main()
