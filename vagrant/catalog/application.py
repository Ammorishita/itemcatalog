from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, FoodGroup, FoodItem, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import urllib2
import requests

app = Flask(__name__)
usdakey = 'XfPYRapBT32bi6UZVPcKXJX1jFvG9LSoyR1Hldnd'
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Food Groups"

# Connect to Database and create database session
engine = create_engine('sqlite:///nutritioncatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all foodgroups
@app.route('/')
@app.route('/foodgroup/')
def showFoodGroups():
	foodgroup = session.query(FoodGroup).order_by(asc(FoodGroup.name))
	if 'username' not in login_session:
		return render_template('publicFoodTable.html', foodgroup=foodgroup)
	else:
		return render_template('FoodTable.html', foodgroup = foodgroup)

# Add a food group

@app.route('/foodgroup/new/', methods=['GET', 'POST'])
def newFoodGroup():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newFoodGroup = FoodGroup(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newFoodGroup)
        flash('New FoodGroup %s Successfully Created' % newFoodGroup.name)
        session.commit()
        return redirect(url_for('showFoodGroups'))
    else:
        return render_template('newFoodGroup.html')


# Edit a food group

@app.route('/foodgroup/<int:foodgroup_id>/edit', methods=['GET','POST'])
def editFoodGroup(foodgroup_id):
    if 'username' not in login_session:
        return redirect('/login')
    foodgroup = session.query(FoodGroup).filter_by(id=foodgroup_id).one()
    login = login_session['user_id']
    itemid = foodgroup.user_id
    if login_session['user_id'] != foodgroup.user_id:
        return render_template('accessdenied.html', login = login, itemid = itemid)
    if request.method == 'POST':
        if request.form['name']:
	        foodgroup.name = request.form['name']
	        session.add(foodgroup)
	        session.commit()
	        flash('Food Group Successfully Edited')
	        return redirect(url_for('showFoodGroups', foodgroup_id=foodgroup_id))
    else:
        return render_template('editFoodGroup.html', foodgroup_id=foodgroup_id, item=foodgroup)

# Delete a food group

@app.route('/foodgroup/<int:foodgroup_id>/delete', methods=['GET','POST'])
def deleteFoodGroup(foodgroup_id):
    if 'username' not in login_session:
        return redirect('/login')
    foodgroup = session.query(FoodGroup).filter_by(id=foodgroup_id).one()
    login = login_session['user_id']
    itemid = foodgroup.user_id
    if login_session['user_id'] != foodgroup.user_id:
	    return render_template('accessdenied.html', login=login, itemid=itemid)
    if request.method == 'POST':
        session.delete(foodgroup)
        session.commit()
        flash('Food Item Successfully Deleted')
        return redirect(url_for('showFoodGroups', foodgroup_id=foodgroup_id))
    else:
        return render_template('deleteFoodGroup.html', item=foodgroup, login=login, itemid=itemid)

# Show an individual food group

@app.route('/foodgroup/<int:foodgroup_id>/')
@app.route('/foodgroup/<int:foodgroup_id>/items/')
def showFoodItem(foodgroup_id):
	foodgroup = session.query(FoodGroup).filter_by(id=foodgroup_id).one()
	fooditems = session.query(FoodItem).filter_by(foodgroup_id=foodgroup_id).all()
	creator = getUserInfo(foodgroup.user_id)
	if 'username' not in login_session or creator.id != login_session['user_id']:
		return render_template('publicfoodItem.html', fooditems=fooditems, foodgroup=foodgroup, creator=creator)
	else:
		return render_template('foodItem.html', fooditems=fooditems, foodgroup=foodgroup, creator=creator)

# Search for a food item in usda database

@app.route('/foodgroup/<int:foodgroup_id>/items/search/', methods=['GET', 'POST'])
def searchFoodItem(foodgroup_id):
    if request.method == 'POST':
        item = request.form['foodName']
        url = 'https://api.nal.usda.gov/ndb/search/?format=json&q=' + item + '&max=1&offset=0&api_key=' + usdakey
        response = urllib2.urlopen(url)
        data = json.load(response)
        ndbno = data['list']['item'][0]['ndbno']
        newurl = 'https://api.nal.usda.gov/ndb/reports/?ndbno=' + ndbno + '&type=b&format=json&api_key=' + usdakey
        newResponse = urllib2.urlopen(newurl)
        newData = json.load(newResponse)
        return render_template('response.html', response=newData, foodgroup_id = foodgroup_id)
    else:
        return 'get request'

# Add searched food item
@app.route('/foodgroup/<int:foodgroup_id>/items/response/', methods=['GET', 'POST'])
def addSearchedItem(foodgroup_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    foodgroup = session.query(FoodGroup).filter_by(id=foodgroup_id).one()
    # if login_session['user_id'] != foodgroup.user_id:
    #     return "<script>function myFunction() {alert('You are not authorized to add menu items to this foodgroup. Please create your own foodgroup in order to add items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        newItem = FoodItem(name=request.form['name'], foodgroup_id=foodgroup_id)
        if request.form['name']:
            newItem.name = request.form['name']
        if request.form['calories']:
            newItem.calories = request.form['calories']
        if request.form['carbs']:
            newItem.carbs = request.form['carbs']
        if request.form['sugars']:
            newItem.sugars = request.form['sugars']
        if request.form['fats']:
            newItem.fats = request.form['fats']
        session.add(newItem)
        session.commit()
        flash('New Food %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showFoodItem', foodgroup_id=foodgroup_id))
    else:
        return render_template('newFoodItem.html', foodgroup_id=foodgroup_id)

# Create a new food item
@app.route('/foodgroup/<int:foodgroup_id>/items/new/', methods=['GET', 'POST'])
def newFoodItem(foodgroup_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    foodgroup = session.query(FoodGroup).filter_by(id=foodgroup_id).one()
    # if login_session['user_id'] != foodgroup.user_id:
    #     return "<script>function myFunction() {alert('You are not authorized to add menu items to this foodgroup. Please create your own foodgroup in order to add items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        newItem = FoodItem(name=request.form['name'], foodgroup_id=foodgroup_id)
        if request.form['name']:
            newItem.name = request.form['name']
        if request.form['calories']:
            newItem.calories = request.form['calories']
        if request.form['carbs']:
            newItem.carbs = request.form['carbs']
        if request.form['sugars']:
            newItem.sugars = request.form['sugars']
        if request.form['fats']:
            newItem.fats = request.form['fats']
        session.add(newItem)
        session.commit()
        flash('New Food %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showFoodItem', foodgroup_id=foodgroup_id))
    else:
        return render_template('newFoodItem.html', foodgroup_id=foodgroup_id)


# Edit a food item
@app.route('/foodgroup/<int:foodgroup_id>/items/<int:fooditem_id>/edit', methods=['GET', 'POST'])
def editFoodItem(foodgroup_id, fooditem_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(FoodItem).filter_by(id=fooditem_id).one()
    foodgroup = session.query(FoodGroup).filter_by(id=foodgroup_id).one()
    if login_session['user_id'] != foodgroup.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this foodgroup. Please create your own foodgroup in order to edit items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['calories']:
            editedItem.calories = request.form['calories']
        if request.form['carbs']:
            editedItem.carbs = request.form['carbs']
        if request.form['sugars']:
            editedItem.sugars = request.form['sugars']
        if request.form['fats']:
        	editedItem.fats = request.form['fats']
        session.add(editedItem)
        session.commit()
        flash('Food Item Successfully Edited')
        return redirect(url_for('showFoodItem', foodgroup_id=foodgroup_id))
    else:
        return render_template('editFoodItem.html', foodgroup_id=foodgroup_id, fooditem_id=fooditem_id, item=editedItem)

# Delete a food item
@app.route('/foodgroup/<int:foodgroup_id>/item/<int:fooditem_id>/delete', methods=['GET', 'POST'])
def deleteFoodItem(foodgroup_id, fooditem_id):
    if 'username' not in login_session:
        return redirect('/login')
    foodgroup = session.query(FoodGroup).filter_by(id=foodgroup_id).one()
    itemToDelete = session.query(FoodItem).filter_by(id=fooditem_id).one()
    if login_session['user_id'] != foodgroup.user_id:
	    return "<script>function myFunction() {alert('You are not authorized to delete menu items to this foodgroup. Please create your own foodgroup in order to delete items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Food Item Successfully Deleted')
        return redirect(url_for('showFoodItem', foodgroup_id=foodgroup_id))
    else:
        return render_template('deleteFoodItem.html', item=itemToDelete)

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token


    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output



# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
        
# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showFoodGroups'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showFoodGroups'))


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# JSON APIs to view food group information
@app.route('/foodgroup/<int:foodgroup_id>/item/JSON')
def foodGroupJSON(foodgroup_id):
    foodgroup = session.query(FoodGroup).filter_by(id=foodgroup_id).one()
    items = session.query(FoodItem).filter_by(
        foodgroup_id=foodgroup_id).all()
    return jsonify(FoodItems=[i.serialize for i in items])


@app.route('/foodgroup/<int:foodgroup_id>/item/<int:fooditem_id>/JSON')
def foodItemJSON(foodgroup_id, fooditem_id):
    fooditem = session.query(FoodItem).filter_by(id=fooditem_id).one()
    return jsonify(fooditem=fooditem.serialize)


@app.route('/foodgroup/JSON')
def foodGroupsJSON():
    foodGroups = session.query(FoodGroup).all()
    return jsonify(foodGroups=[r.serialize for r in foodGroups])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)