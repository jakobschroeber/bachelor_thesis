import mysql.connector

def get_users_from_db():
    mydb = mysql.connector.connect(
        host="172.20.0.4",
        user="root",
        passwd="m@0dl3ing",
        port=3306,
        database="moodle"
    )

    cur = mydb.cursor()
    userQuery = ("select id, username, email, timecreated, lastlogin FROM moodle.m_user;")
    cur.execute(userQuery)

    output = []
    #user = [str(each)+'<br>' for each in cur.fetchall()]
    user = cur.fetchone()
    for user in cur:
        output.append(user)

    cur.close()
    mydb.close()
    print(output)
    return (output)

#0) fetch current users and their enrollment status to memory (load)
    # all data_source gathering in one module (data_source)
    # data_source gathering calls as abstract as possible (i.e. parametrized input and standardized output)
    # input: query string
        # query name, e.g. 'visQuery2'
        # table (no joins, only single-table queries)
        # aggregate fuctions
        # columns
        # where conditions
        # group by
    # output: list of tuples
        # length of tuples depends on number of columns




#1) load data_source only ad-hoc when assessment are carried out, no update / synchronization with local database
    # no further models (e.g., MoodleUser) needed
    # Reflecting Database Objects with SQLAlchemy Core would suffice for having information about what's in the DB
#2) compare with existing entries and only add new entries (update/sync)
    # Likely to require SQLAlchemy ORM
