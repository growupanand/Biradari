from flask import session
import pymongo
from bson import ObjectId
import datetime


#client = pymongo.MongoClient("mongodb://localhost",27017)

client = pymongo.MongoClient("mongodb+srv://test:12345@cluster0.4luf0.mongodb.net/test?retryWrites=true&w=majority")
db = client.test

user_collection = db['users']
request_collection = db['requests']
post_collection = db['posts']


# function to register new user
def register(data):
    username = str.strip(data['username'])
    password = str.strip(data['password'])
    first_name = str.strip(data['first_name'])
    last_name = str.strip(data['last_name'])
    gender = str.strip(data['gender'])
    dob = str.strip(data['dob'])
    location = str.strip(data['location'])

    # check if required filed is not blank
    if '' in (username,password,first_name, last_name,gender,dob,location):
        return False

    # check user is already exist
    query = user_collection.find_one({'username': username})
    if query == None:
        newuser = user_collection.insert_one({'username': username, 'password': password,
                                              'first_name': first_name, 'last_name': last_name,
                                              'gender': gender, 'location': location, 'dob': dob})

        print('new user created with ID:' + str(newuser.inserted_id))
        return True
    else:
        return False


# function to login user
def login(data):

    username = str.strip(data['username'])
    password = str.strip(data['password'])
    if '' in (username, password):
        return False

    query = user_collection.find_one({'username': username, 'password': password})
    if query == None:
        return False
    else:
        query['_id'] = str(query['_id'])
        query['full_name'] = query['first_name'] + ' ' + query['last_name']
        session['login_user'] = query
        session['logged_in'] = True
        return True


# function to logout and clear session
def logout():
    session.clear()
    session['logged_in'] = False
    return True

# refresh user
def refresh_user():
    username = str(session['login_user']['username'])
    password = str(session['login_user']['password'])
    login({'username': username, 'password': password})
    return True

# update profile
def update_profile(data):
    username = str(session['login_user']['username'])
    password = str(session['login_user']['password'])
    first_name = str.strip(data['first_name'])
    last_name = str.strip(data['last_name'])
    gender = str.strip(data['gender'])
    location = str.strip(data['location'])
    dob = str.strip(data['dob'])
    if '' in (first_name, last_name, gender, location, dob):
        return False
    user_collection.update_one({'username': username, 'password': password},
                               {'$set': {'first_name': first_name, 'last_name': last_name, 'gender': gender,
                                         'location': location, 'dob': dob}})
    refresh_user()
    return True


# function to get profile data from username
def get_profile(username):
    query = user_collection.find_one({'username': username}, {'_id': 0})
    if query == None:
        return False
    else:
        query['father'] = None if not 'father' in query else query['father']
        query['mother'] = None if not 'mother' in query else query['mother']
        query['spouse'] = None if not 'spouse' in query else query['spouse']
        query['sibilings'] = [] if not 'sibilings' in query else query['sibilings']
        query['full_name'] = query['first_name'] + ' ' + query['last_name']
        return query


# function to get user list from query
def query_user(query):
    result = user_collection.find({'$or': [{'username': query}, {'first_name': query}, {'last_name': query}]},
                                  {'_id': 0})
    return result


# function to update father
def update_father(username):
    if username == session['login_user']['username']:
        return {'result':False,'msg':'you cannot add yourself as father.'}
    user_collection.update_one({'username': session['login_user']['username']},
                               {'$set': {'father':{'username': username}}})
    refresh_user()
    request_exist = request_collection.find_one({'from_username': session['login_user']['username'],
                                                 'type': 'father'})
    if request_exist == None:
        request_collection.insert_one({'from_username': session['login_user']['username'],
                                       'to_username': username, 'type': 'father'})
    else:
        request_collection.update_one({'from_username': session['login_user']['username'],
                                                 'type': 'father'},
                                      {'$set':{'to_username': username}})

    return {'result':True}

# function to update mother
def update_mother(username):
    if username == session['login_user']['username']:
        return {'result':False,'msg':'you cannot add yourself as mother.'}
    user_collection.update_one({'username': session['login_user']['username']},
                               {'$set': {'mother':{'username': username}}})
    refresh_user()
    request_exist = request_collection.find_one({'from_username': session['login_user']['username'],
                                                 'type': 'mother'})
    if request_exist == None:
        request_collection.insert_one({'from_username': session['login_user']['username'],
                                       'to_username': username, 'type': 'mother'})
    else:
        request_collection.update_one({'from_username': session['login_user']['username'],
                                       'type': 'mother'},
                                      {'$set': {'to_username': username}})
    return {'result':True}

# function to update spouse
def update_spouse(username):
    if username == session['login_user']['username']:
        return {'result':False,'msg':'you cannot add yourself as spouse.'}
    user_collection.update_one({'username': session['login_user']['username']},
                               {'$set': {'spouse':{'username': username}}})
    refresh_user()
    request_exist = request_collection.find_one({'from_username': session['login_user']['username'],
                                                 'type': 'spouse'})
    if request_exist == None:
        request_collection.insert_one({'from_username': session['login_user']['username'],
                                       'to_username': username, 'type': 'spouse'})
    else:
        request_collection.update_one({'from_username': session['login_user']['username'],
                                       'type': 'spouse'},
                                      {'$set': {'to_username': username}})
    return {'result':True}


# function to add sibiling
def add_sibiling(username):
    if username == session['login_user']['username']:
        return {'result':False,'msg':'you cannot add yourself as sibiling.'}
    sibilings = get_profile(session['login_user']['username'])['sibilings']
    for i in sibilings:
        if i['username'] == username:
            return {'result': False, 'msg': 'Already added as sibiling!'}
    else:
        user_collection.update_one({'username': session['login_user']['username']},
                                   {'$push': {'sibilings': {'username': username}}}, upsert=True)
    refresh_user()
    request_exist = request_collection.find_one({'from_username': session['login_user']['username'],
                                       'to_username': username, 'type': 'sibiling'})
    if request_exist == None:
        request_collection.insert_one({'from_username': session['login_user']['username'],
                                       'to_username': username, 'type': 'sibiling'})
    return {'result':True}


# function to delete sibiling
def delete_sibiling(username):
    user_collection.update_one({'username': session['login_user']['username']},
                               {'$pull': {'sibilings': {'username':username}}})
    request_exist = request_collection.find_one({'from_username': session['login_user']['username'],
                                                 'to_username': username, 'type': 'sibiling'})
    if not request_exist == None:
        request_collection.delete_one({'from_username': session['login_user']['username'],
                                       'to_username': username, 'type': 'sibiling'})
    refresh_user()
    return True


# function to get family
def get_family(username):
    user = get_profile(username)
    result = {}
    for relation in ('father','mother','spouse'):
        if user[relation] == None:
            result[relation] = None
        else:
            result[relation] = user[relation]
            q = get_profile(user[relation]['username'])
            result[relation]['name'] = q['full_name']

    if user['sibilings'] == None:
        result['sibilings'] = None
    else:
        result['sibilings'] = user['sibilings']
        i = 0
        for sibiling in user['sibilings']:
            q = get_profile(sibiling['username'])
            result['sibilings'][i]['name'] = q['full_name']
            i += 1
    return result


# function to get requests list
def get_requests(username):
    q = request_collection.find({'to_username':username})
    result = []
    for x in q:
        x['_id'] = str(x['_id'])
        name = get_profile(x['from_username'])['full_name']
        x['name'] = name
        result.append(x)
    return result


# function to confirm request
def confirm_request(id):
    _id = ObjectId(id)
    request = request_collection.find_one({'_id':_id})
    if request['type'] in ('father','mother','spouse'):
        user_collection.update_one({'username': request['from_username']}, {'$set': {request['type']+'.confirmed': True}})
    elif request['type'] == 'sibiling':
        user_collection.update_one({'username': request['from_username'], 'sibilings.username':request['to_username']}, {'$set': {'sibilings.$.confirmed': True}})
    request_collection.delete_one({'_id': _id})
    return True


# function to post on wall
def post(content):
    if str.strip(content) == '':
        return {'result':False,'msg':'Field cannot be black'}
    q = post_collection.insert_one({'username':session['login_user']['username'],
                                'content':content,
                                'timestamp':datetime.datetime.utcnow()})
    return {'result':True,'id':str(q.inserted_id)}


# function to get post list
def get_user_posts(username):
    q = post_collection.find({'username':username}).sort('timestamp',-1)
    result = []
    for post in q:
        post['_id'] = str(post['_id'])
        post['full_name'] = get_profile(post['username'])['full_name']
        timestamp = post['timestamp']
        post['timestamp'] = timestamp.strftime('%d/%m/%Y')
        result.append(post)
    return result

# function to get wall post list
def get_wall_posts(username=None,newest_post_timestamp=None,oldest_post_timestamp=None):
    login_user = get_profile(session['login_user']['username'])
    if username == None:
        username_list = [login_user['username']]
        #add more username to query posts
        for relation in ('father','mother','spouse'):
            if not login_user[relation] == None:
                if not login_user[relation]['username'] in username_list:
                    username_list.append(login_user[relation]['username'])
        for sibiling in login_user['sibilings']:
            if not sibiling['username'] in username_list:
                username_list.append(sibiling['username'])
    else:
        username_list = [username]

    if not newest_post_timestamp == None:
        timestamp_query = datetime.datetime.strptime(newest_post_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        q = post_collection.find({'username': {'$in': username_list}, 'timestamp': {'$gt': timestamp_query}}).sort(
            'timestamp', -1)
    elif not oldest_post_timestamp == None:
        timestamp_query = datetime.datetime.strptime(oldest_post_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        q = post_collection.find({'username': {'$in': username_list}, 'timestamp': {'$lt': timestamp_query}}).sort(
            'timestamp', -1).limit(10)
    else:
        q = post_collection.find({'username':{'$in':username_list}}).sort('timestamp',-1).limit(10)


    result = []
    for post in q:
        post['_id'] = str(post['_id'])
        post['user_full_name'] = get_profile(post['username'])['full_name']
        timestamp = post['timestamp']
        post['raw_timestamp'] = str(timestamp)
        post['timestamp'] = timestamp.strftime('%d/%m/%Y')
        result.append(post)
    return result

