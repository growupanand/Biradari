from Biradari import app
from flask import request, session
from Biradari import controller
import json
from bson.json_util import dumps

@app.route('/api/<task>', methods=["POST", "GET"])
def task(task):
    post_data = request.form

    if task == 'register':
        result = controller.register(post_data)
        return json.dumps({'usercreated':result})


    if task == 'login':
        result = controller.login(post_data)
        return json.dumps({'loggedin':result})


    if task == 'logout':
        controller.logout()
        return json.dumps({'result':True})


    if task == 'update_profile':
        controller.update_profile(post_data)
        return json.dumps({'result':True})


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

    if task == 'post':
        result = controller.post(post_data['content'])
        return dumps(result)

    if task == 'get_new_posts':
        newest_post_timestamp = post_data['newest_post_timestamp']
        posts = controller.get_new_wall_posts(newest_post_timestamp)
        return dumps(posts)

    if task == 'get_old_posts':
        oldest_post_timestamp = post_data['oldest_post_timestamp']
        posts = controller.get_old_wall_posts(oldest_post_timestamp)
        return dumps(posts)

    return 'API function not found'


@app.route('/api/get_posts', methods=["GET","POST"])
def get_posts():
    newest_post_timestamp = None if request.form.get('newest_post_timestamp') == '' else request.form.get('newest_post_timestamp')
    oldest_post_timestamp = None if request.form.get('oldest_post_timestamp') == '' else request.form.get('oldest_post_timestamp')
    username = request.form.get('username')
    posts = controller.get_wall_posts(username=username,newest_post_timestamp=newest_post_timestamp,oldest_post_timestamp=oldest_post_timestamp )
    return dumps(posts)
