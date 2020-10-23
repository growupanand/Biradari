from Biradari import app, controller
from flask import render_template, session
from datetime import datetime



@app.route('/')
def index():
    if session.get('logged_in') == True:
        if not 'father' in session.get('login_user') or not 'mother' in session.get('login_user'):
            return render_template('finish.html', user=session.get('login_user'))
        return render_template('home.html')
    else:
        return render_template('guest.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/add_father')
def view_addfather():
    return render_template('add_father.html')

@app.route('/add_mother')
def view_addmother():
    return render_template('add_mother.html')


@app.route('/profile/<username>')
@app.route('/profile')
def profile(username = None):
    if username == None or username == session['login_user']['username']:
        user = session['login_user']
        page = 'user_profile.html'
    else:
        user = controller.get_profile(username)
        if user == False:
            return 'user not found'
        page = 'view_profile.html'

    user['dob'] = datetime.strptime(user['dob'], '%Y-%m-%d').strftime('%d-%m-%Y')
    return render_template(page, user=user)

@app.route('/edit_profile')
def edit_profile():
    user = session['login_user']
    return render_template('edit_profile.html', user = user)

@app.route('/biradari/<username>')
@app.route('/biradari')
def biradari(username = None):
    if username == None or username == session['login_user']['username']:
        user = controller.get_profile(session['login_user']['username'])
    else:
        user = controller.get_profile(username)

    user['biradari'] =controller.get_biradari(user['username'])
    return render_template('biradari.html', user = user)

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
