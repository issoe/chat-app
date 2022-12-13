from mysql import connector as mysql_connector

def connect_db():
    return mysql_connector.connect(
        user = 'root',
        password = '71102Tony#',
        host = '127.0.0.1',
        database = 'chatapp_new'
    )
    
def get_user(uid):
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('CALL get_user(%s)',(uid,))
        user = cursor.fetchone()
    except:
        connection.close()
        raise mysql_connector.Error('User not found')

    connection.close()
    return user
   
def get_user_friends(uid):
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('CALL get_friend_list(%s)', (uid,))
        friends = cursor.fetchall()
    except:
        connection.close()
        raise mysql_connector.Error('User id not found')
    
    connection.close()
    return friends

def get_user_from_credential(username, password):
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('CALL login(%s, %s)',(username, password))
        user = cursor.fetchone()
    except:
        connection.close()
        raise mysql_connector.Error('User not found')

    connection.close()
    return user

def get_user_by_username(username):
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('CALL get_user_by_username(%s)',(username,))
        user = cursor.fetchone()
    except:
        connection.close()
        raise mysql_connector.Error('User not found')

    connection.close()
    return user

def add_friend(sender_id, receiver_id):
    try:
        fid = None
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('add_friend', (fid, sender_id, receiver_id))
        connection.commit()
    except mysql_connector.Error as e:
        print(e)
        connection.close()
        raise e
    return fid

def accept_friend(sender_id, receiver_id):
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.callproc('accept_friend', (sender_id, receiver_id))
        connection.commit()
        connection.close()
    except mysql_connector.Error as e:
        print(e)
        connection.close()
        raise mysql_connector.Error('Friend request not found')
    connection.close()

def check_friend(uid, fid):
    """return accepted friend request else return None"""
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('CALL get_friend(%s, %s)', (uid, fid))
        frequest = cursor.fetchone()
    except mysql_connector.Error as e:
        connection.close()
        raise e
    connection.close()
    return bool(frequest) 

def get_friend_requests(uid):
    """return incomming friend requests"""
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True) 
        cursor.execute('CALL get_friend_requests(%s)', (uid,))
        requests = cursor.fetchall()
    except mysql_connector.Error as e:
        connection.close()
        raise e
    connection.close()
    return requests