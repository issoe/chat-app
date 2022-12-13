import mysql.connector as mysql_connector
from utils import db
from utils.tokens import (
    create_access_token,
    auth_required
)
from flask import Flask
from flask import request
from utils.user_manager import (
    UserManager,
    create_response,
)
from utils.events import Event as FEvent
app = Flask(__name__)
user_manager = None

@app.route('/login', methods=['POST'])
def login():
    try:
        if request.is_json:
            username = request.json['username']
            password = request.json['password']
        else:
            username = request.form['username']
            password = request.form['password']
        user = db.get_user_from_credential(username, password)
        token = create_access_token(uid=user['id'])

        return {'user': user, 'access': token}

    except KeyError:
        return {'status': 'error', 'detail': 'Missing credentials'}, 400
    except mysql_connector.Error as e:
        return {'status': 'error', 'detail': str(e)}, 405

@app.route('/add_friend', methods=['POST'])
@auth_required
def add_friend(user):
    print(user_manager._users.keys())
    try:
        if request.is_json:
            fusername = request.json['fusername']
        else:
            fusername = request.form['fusername']
        uid = user['id']
        friend = db.get_user_by_username(fusername.strip())
        print(friend)
        db.add_friend(user['id'], friend['id'])
        fid = friend['id']
    except KeyError as e:
        print(e)
        return {'status': 'error', 'detail': 'your friend is incorrect'}, 400

    except mysql_connector.Error as e:
        print(e)
        return {'status': 'error', 'detail': str(e)}, 405

    noti = create_response(
        event=FEvent.friend_request,
        body={
            'friend_id': uid,
            'username': user['username']
        }
    )

    user_manager.send(fid, noti)
    return {'status': 'ok'}

@app.route('/accept_friend', methods=['PUT'])
@auth_required
def accept_friend(user):
    print(user_manager._users.keys())
    try:
        if request.is_json:
            fid = request.json['friend_id']
        else:
            fid = request.form['friend_id']
        fid=fid.strip()
        uid = user['id']
        db.accept_friend(fid, uid)
        is_online = int(fid) in user_manager.get_online_user()
        
    except KeyError:
        return {'status': 'error', 'detail': 'sender_id is required'}, 400
    except mysql_connector.Error as e:
        print(e)
        return {'status': 'error', 'detail': str(e)}, 405
    
    noti = create_response(
        event=FEvent.friend_accept,
        body={
            'friend_id': uid,
            'username': user['username']
        }
    )
    user_manager.send(fid, noti)
    return {'status': 'ok', 'is_online': is_online}
    
@app.route('/friend_list', methods=['GET'])
@auth_required
def friend_list(user):
    uid = user['id']
    try:
        friends = db.get_user_friends(uid)
        online_users = user_manager.get_online_user()

        for f in friends:
            if f['id'] in online_users:
                f['is_online'] = True
            else: 
                f['is_online'] = False

    except mysql_connector.Error as e:
        return {'status': 'error', 'detail': str(e)}, 405
    return {'status': 'ok', 'friends': friends}

@app.route('/get_address', methods=['GET'])
@auth_required
def get_address(user):
    uid = user['id']
    try:
        fid = request.args.get('friend_id')
        ok = db.check_friend(uid, fid)
        if not ok:
            return {'status': 'error', 'detail': 'Cannot get address of stranger'}, 400
    except KeyError as e:
        return {'status': 'error', 'detail': 'friend_id is required'}, 400
    except mysql_connector.Error as e:
        return {'status': 'error', 'detail': 'Server fail'}, 400

    address = user_manager.address_of(fid)
    if not address:
        return {'status': 'error', 'detail': 'User not online'}, 400
    return {'status': 'ok', 'address': address}


@app.route('/friend_requests', methods=['GET'])
@auth_required
def friend_requests(user):
    uid = user['id']
    try:
        requests = db.get_friend_requests(uid)
    except mysql_connector.Error as e:
        return {'status': 'error', 'detail': 'Get friend requests fail'}, 405
    return {'status': 'ok', 'requests': requests}

user_manager = UserManager()

if __name__ == '__main__':
    user_manager.start()
    app.run()