from flask import session
from datetime import datetime
from Biradari.db import user_collection, post_collection
from bson import ObjectId

class user:

    def __init__(self, username = None):
        self.username = username


    #login user
    def login(self, password):
        session['user'] = None
        session['logged_in'] = False
        result = {}
        result['result'] = False
        #validate data
        password = None if str.strip(password) == '' else str.strip(password)
        if None in (self.username, password):
            result['msg'] = 'Username or Password cannot be Empty.'
            return result
        q = user_collection.find_one({'username': self.username, 'password': password})
        if q == None:
            result['msg'] = 'Username or Password is wrong.'
            return result
        else:
            session['user'] = self.profile()
            session['logged_in'] = True
            result['result'] = True
            result['msg'] = 'Login Success.'
            return result


    #Register new user
    def register(self, formdata):
        result = {}
        result['result'] = False
        fields = ('username', 'password', 'first_name', 'last_name', 'gender', 'dob', 'location')
        data = {}
        # check if any field is empty
        empty_field = []
        for field in fields:
            if str.strip(formdata[field]) == '':
                empty_field.append(field)
            else:
                data[field] = str.strip(formdata[field])
        if len(empty_field) > 0:
            result['msg'] = 'Field cannot be Empty - ' + ', '.join(empty_field)
            return result
            # check if username already exist
        if not user_collection.find_one({'username': data['username']}) == None:
            result['msg'] = 'Username already exist.'
        else:
            data['type'] = 'real'
            q = user_collection.insert_one(data)
            if q:
                result['result'] = True
                result['msg'] = 'User created.'
                result['id'] = str(q.inserted_id)
                print('user created: ' + str(data['username']) + ' : ' + result['id'])
            else:
                result['msg'] = 'Something went wrong.'
        return result


    #logout user and clear session
    def logout(self):
        session.clear()
        return {'result':True}


    #get user profile data
    def profile(self, username=None):
        if username == None:
            username = self.username
        q = user_collection.find_one({'username':username})
        if not q == None:
            q['_id'] = str(q['_id'])
            q['full_name'] = q['first_name']+' '+q['last_name']
            return q
        else:
            return False

    #get user posts
    def get_posts(self, limit=0, after=None, before=None, get_wall_posts=False):
        limit = int(limit)
        username_list = []
        full_name_list = {}
        query = {}
        query_sort = -1
        username_list.append(self.username)
        full_name_list[self.username] = self.profile()['full_name']
        if not before == None:
            query['timestamp'] = {'$lt':before}
            query_sort = -1
        if not after == None:
            query['timestamp'] = {'$gt':after}
            query_sort = 1
        if get_wall_posts:
            for i in self.get_biradari():
                username_list.append(i)
        query['username'] = {'$in':username_list}
        q = post_collection.find(query).sort('timestamp', query_sort).limit(limit)
        result = []
        for post in q:
            post['_id'] = str(post['_id'])
            post['timestamp'] = str(post['timestamp'])
            post['full_name'] = user(post['username']).profile()['full_name']
            result.append(post)
        return result


    #post content
    def post(self, content):
        result = {}
        result['result'] = False
        if str.strip(content) == '' or content == None:
            result['msg'] = 'Content cannot be empty.'
            return result
        q = post_collection.insert_one({'username':self.username,
                                'content':content,
                                'timestamp':datetime.utcnow()})
        if q.acknowledged:
            result['id'] = str(q.inserted_id)
            result['result'] = True
            result['msg'] = 'Posted successfully.'
        else:
            result['msg'] = 'Something went wrong.'
        return result

    #get biradari list
    def get_biradari(self):
        result = []
        q = user_collection.find_one({'username':self.username},{'_id':0, 'biradari':1})
        if 'biradari' in q:
            for username in q['biradari']:
                result.append(username)
        return result


    #update user profile
    def update_profile(self, updated_data):
        result = {}
        result['result'] = False
        q = user_collection.update_one({'username': self.username},
                                   {'$set': updated_data})
        if q.acknowledged:
            result['result'] = True
            session['user'] = self.profile()
            result['msg'] = 'Profile Updated successfully.'
        else:
            result['msg'] = 'Something went wrong'
        return result


    #delete user post
    def delete_post(self, id):
        result = {}
        result['result'] = False
        q = post_collection.delete_one({'username':self.username, '_id':ObjectId(id)})
        if q.deleted_count>0:
            result['result'] = True
        else:
            result['msg'] = 'Something went wrong'
        return result


    # add user in biradari
    def add_biradari(self, username):
        result = {}
        result['result'] = False
        #check if user already exist in biradari
        if username in self.get_biradari():
            result['msg'] = 'User already exist in Biradari.'
        else:
            q = user_collection.update_one({'username':self.username},
                                           {'$push':{'biradari':username}})
            if q.matched_count>0:
                result['result'] = True
                result['msg'] = 'user added in biradari.'
        return result

    # remove user in biradari
    def remove_biradari(self, username):
        result = {}
        result['result'] = False
        # check if user already exist in biradari
        if username in self.get_biradari():
            q = user_collection.update_one({'username': self.username},
                                           {'$pull': {'biradari': username}})
            if q.matched_count > 0:
                result['result'] = True
                result['msg'] = 'user removed from biradari.'
        else:
            result['msg'] = 'User not found in Biradari.'
        return result


    #find person
    def find_person(self, query):
        q = user_collection.find({'$or': [
            {'username': query},
            {'first_name': query},
            {'last_name': query}
        ]})
        result = []
        for i in q:
            result.append({
                'username': i['username'],
                'full_name': i['first_name'] + ' ' + i['last_name']
            })
        return result
