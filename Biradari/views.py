from Biradari import app, controller, stringtotimestamp
from flask import render_template, session
from datetime import datetime
from Biradari.user import user


@app.route('/')
def index_page():
    if session.get('logged_in') == True:
        user_data = user(session['user']['username'])
        posts = user_data.get_posts(limit=10, get_wall_posts=True)
        first_timestamp = posts[0]['timestamp'] if len(posts)>0 else None
        last_timestamp = posts[len(posts)-1]['timestamp'] if len(posts)>0 else None
        for i in range(len(posts)):
            timestamp = stringtotimestamp(posts[i]['timestamp'])
            posts[i]['timestamp'] = timestamp.strftime('%d/%B/%Y %H:%M')
        return render_template('home.html', posts=posts, first_timestamp=first_timestamp, last_timestamp=last_timestamp)
    else:
        return render_template('login.html')


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/logout')
def logout_page():
    session.clear()
    return render_template('login.html')


@app.route('/profile/<username>')
@app.route('/profile')
def profile_page(username = None):
    is_biradari = False
    #check if logged in user visited page then show his profile page
    if username == None or username == session['user']['username']:
        user_data = user(session['user']['username'])
        profile_page = 'user_profile.html'
    else:
        #show other user profile page
        user_data = user(username)
        #check if other user is exist
        if user_data == False:
            return 'User not found'
        profile_page = 'view_profile.html'
        #check if other user is in biradari list
        if username in user(session['user']['username']).get_biradari():
            is_biradari = True
    user_profile = user_data.profile()
    user_profile['dob'] = datetime.strptime(user_profile['dob'], '%Y-%m-%d').strftime('%d-%m-%Y')
    biradari_list = []
    for i in user_data.get_biradari():
        biradari_list.append({'username':i,'full_name':user(i).profile()['full_name']})
    return render_template(profile_page, user=user_profile, biradari_list=biradari_list, is_biradari=is_biradari)


@app.route('/edit_profile')
def edit_profile_page():
    user_profile = user(session['user']['username']).profile()
    return render_template('edit_profile.html', user = user_profile)


@app.route('/biradari')
def biradari_page():
    biradari_list = []
    user_data = user(session['user']['username'])
    for username in user_data.get_biradari():
        biradari_list.append({
            'username' : username,
            'full_name' : user(username).profile()['full_name']
        })
    return render_template('biradari.html', user=user_data, biradari_list=biradari_list)


@app.route('/search')
def search_page():
    return render_template('search.html')











@app.route('/edit_biradari')
def edit_biradari():
    user = controller.get_profile(session['login_user']['username'])
    user['family'] = controller.get_family(session['login_user']['username'])
    return render_template('edit_biradari.html', user = user)


@app.route('/requests')
def requests():
    user = controller.get_profile(session['login_user']['username'])
    user['requests'] = controller.get_requests(session['login_user']['username'])
    return render_template('requests.html', user = user)
