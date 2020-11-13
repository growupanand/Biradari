from Biradari import app, controller, datetime, stringtotimestamp
from flask import request, session
import json
from bson.json_util import dumps
from Biradari.user import user


@app.route('/api/login', methods=["POST"])
def login_api():
    username = request.form['username']
    password = request.form['password']
    result = user(username).login(password)
    return json.dumps(result)


@app.route('/api/register', methods=['POST'])
def register_api():
    return json.dumps(user().register(request.form))


@app.route('/api/logout')
def logout_api():
    return json.dumps(user().logout())


@app.route('/api/get_posts/<username>', methods=['GET', 'POST'])
@app.route('/api/get_posts', methods=['GET', 'POST'])
def get_posts_api(username = None):
    if username == None or username == session['user']['username']:
        user_data = user(session['user']['username'])
    else:
        user_data = user(username)
    limit = request.form.get('limit', 0)
    before = None
    last_timestamp = request.form.get('last_timestamp', None)
    if not last_timestamp in (None, 'None'):
        before = stringtotimestamp(last_timestamp)
    after = None
    first_timestamp = request.form.get('first_timestamp', None)
    if not first_timestamp in (None, 'None'):
        after = stringtotimestamp(first_timestamp)
    get_wall_posts = request.form.get('get_wall_posts', False)
    posts = user_data.get_posts(limit=limit, before=before, after = after, get_wall_posts=get_wall_posts)
    return json.dumps(posts)


@app.route('/api/post', methods=['POST'])
def post_api():
    content = request.form['content']
    result = user(session['user']['username']).post(content)
    return json.dumps(result)


@app.route('/api/update_profile', methods=['POST'])
def update_profile_api():
    result = {}
    result['result'] = False
    updated_data = {}
    empty_field = []
    for field in ('first_name', 'last_name', 'gender', 'location', 'dob'):
        data = request.form.get(field, None)
        if data == None or str.strip(data) == '':
            empty_field.append(field)
        else:
            updated_data[field] = str.strip(data)
    if len(empty_field)>0:
        result['msg'] = 'Field cannot be Empty - ' + ', '.join(empty_field)
    else:
        result = user(session['user']['username']).update_profile(updated_data)
    return json.dumps(result)


@app.route('/api/delete_post', methods=['POST'])
def delete_post_api():
    result = {}
    result['result'] = False
    id = request.form.get('id', None)
    if id == None or str.strip(id) == '':
        result['msg'] = 'ID not set'
    else:
        result = user(session['user']['username']).delete_post(id)
    return result


@app.route('/api/add_biradari', methods=['POST'])
def add_biradari_api():
    result = {}
    result['result'] = False
    username = request.form.get('username', None)
    if username == None or str.strip(username) == '':
        result['msg'] = 'Provide username.'
    else:
        result = user(session['user']['username']).add_biradari(username)
    return result


@app.route('/api/remove_biradari', methods=['POST'])
def remove_biradari_api():
    result = {}
    result['result'] = False
    username = request.form.get('username', None)
    if username == None or str.strip(username) == '':
        result['msg'] = 'Provide username.'
    else:
        result = user(session['user']['username']).remove_biradari(username)
    return result


@app.route('/api/search_person', methods=['POST'])
def search_person_api():
    result = {}
    result['result'] = False
    query = request.form.get('query', None)
    if query == None or str.strip(query) == '':
        result['msg'] = 'Type something for search.'
    else:
        result['result'] = True
        result['data'] = []
        for i in user(session['user']['username']).find_person(query):
            result['data'].append(i)
    return result




@app.route('/api/<task>', methods=["POST"])
def task(task):
    post_data = request.form


    if task == 'create_father':
        data = {}
        data['first_name'] = post_data['first_name']
        data['last_name'] = post_data['last_name']
        data['gender'] = 'male'
        data['owner'] = session.get('login_user')['username']
        data['username'] = str(data['owner'])+'.'+str(data['first_name'])+str(data['last_name'])
        data['type'] = 'virtual'
        result = controller.create_virtual_user(data)
        if result['result'] == True:
            controller.update_father(data['username'])
        return json.dumps(result)

    if task == 'create_mother':
        data = {}
        data['first_name'] = post_data['first_name']
        data['last_name'] = post_data['last_name']
        data['gender'] = 'female'
        data['owner'] = session.get('login_user')['username']
        data['username'] = str(data['owner'])+'.'+str(data['first_name'])+str(data['last_name'])
        data['type'] = 'virtual'
        result = controller.create_virtual_user(data)
        if result['result'] == True:
            controller.update_mother(data['username'])
        return json.dumps(result)


    if task == 'query_user':
        result = controller.query_user(post_data['query'])
        return dumps(result)


    if task == 'update_father':
        result = controller.update_father(post_data['username'])
        return dumps(result)


    if task == 'update_mother':
        result = controller.update_mother(post_data['username'])
        return dumps(result)


    if task == 'update_spouse':
        result = controller.update_spouse(post_data['username'])
        return dumps(result)


    if task == 'add_sibiling':
        result = controller.add_sibiling(post_data['username'])
        return dumps(result)


    if task == 'delete_sibiling':
        controller.delete_sibiling(post_data['username'])
        return dumps({'result': 'ok'})


    if task == 'confirm_request':
        controller.confirm_request(post_data['id'])
        return dumps({'result': True})


    return 'API function not found'


