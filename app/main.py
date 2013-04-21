# do not change or move the following lines if you still want to use the box.py auto generator
from app import app, db
from models import User, Action, Activity
# you can freely change the lines below
from flask import render_template
from flask import json
from flask import session
from flask import url_for
from flask import redirect
from flask import request
from flask import abort
from flask import Response
import logging
from helpers import generate_key
import hashlib
from datetime import datetime
# define global variables here

def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]  
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

# home root controller
@app.route('/')
def index():
	# define your controller here
	if "user" in session:
		user = User.query.get(session["user"]["id"])
		actions = [item.dto() for item in user.action]
		total_actions = len(actions)
		activities = [item.dto() for item in Activity.query.all()]
		
		
		if not activities:
			activities = None
		if "message" in session:
			message = session["message"]
			session.pop("message",None)
		else:
			message = None
		return render_template('loginhome.html', message=message, activities=activities, user = user.dto(), total_actions = total_actions)
	else:
		ranks = ranks = User.query.order_by("total_score desc").all()
		ranks = ranks[:5]
		return render_template('welcome.html', ranks=ranks)


########### user data model controllers area ###########

@app.route('/user/',methods=['GET','POST'],defaults={'id':None})
@app.route('/user/<id>',methods=['GET','PUT','DELETE'])
def user_controller(id):
	email = request.values.get('email')
	first_name = request.values.get('first_name')
	last_name = request.values.get('last_name')
	password = request.values.get('password')
	country = request.values.get('country')
	city = request.values.get('city')
	join_date = request.values.get('join_date')

	if id:
		if request.method == 'GET':
			user = User.query.get(id)
			if user:
				user = user.dto()
			if request.values.get('json'):
				return json.dumps(dict(user=user))
			else:
				return render_template('user_view.html', user = user)
		elif request.method == 'PUT':
			user_item = User.query.get(id)
			user_item.email = email
			user_item.first_name = first_name
			user_item.last_name = last_name
			user_item.password = password
			user_item.country = country
			user_item.city = city
			user_item.join_date = join_date
			db.session.add(user_item)
			db.session.commit()
			return 'updated'
		elif request.method == 'DELETE':
			user_item = User.query.get(id)
			db.session.delete(user_item)
			db.session.commit()
			return 'deleted'
		else:
			return 'Method Not Allowed'
	else:
		if request.method == 'GET':
			user_list = User.query.all()
			if user_list:
				entries = [user.dto() for user in user_list]
			else:
				entries=None
			if request.values.get('json'):
				return json.dumps(dict(user=entries))
			else:
				return render_template('user.html',user_entries = entries, title = "User List")
		elif request.method == 'POST':
			hasher = hashlib.md5()
			hasher.update(password)
			password = hasher.hexdigest()
			new_user = User(
							email = email,
							first_name = first_name,
							last_name = last_name,
							password = password,
							country = country,
							city = city,
							join_date = datetime.now()
							)

			db.session.add(new_user)
			db.session.commit()
			session["user"] = new_user.dto()
			return redirect(url_for('index'))
		else:
			return 'Method Not Allowed'

@app.route('/user/add/')
def user_add_controller():
	#this is the controller to add new model entries
	return render_template('user_add.html', title = "Add New Entry")

@app.route('/user/edit/<id>')
def user_edit_controller(id):
	#this is the controller to edit model entries
	user_item = User.query.get(id)
	return render_template('user_edit.html', user_item = user_item, title = "Edit Entries")



########### action data model controllers area ###########

@app.route('/action/',methods=['GET','POST'],defaults={'id':None})
@app.route('/action/<id>',methods=['GET','PUT','DELETE'])
def action_controller(id):
	if "user" in session:
		activity_id = request.values.get('activity_id')
		if activity_id:
			activity = Activity.query.get(activity_id)
			if activity:
				score = activity.score
			else:
				score = 0.0
			print score
		if id:
			if request.method == 'GET':
				action = Action.query.get(id)
				if action:
					action = action.dto()
				if request.values.get('json'):
					return json.dumps(dict(action=action))
				else:
					return render_template('action_view.html', action = action)
			elif request.method == 'PUT':
				action_item = Action.query.get(id)
				action_item.activity_id = activity_id
				action_item.score = score
				db.session.add(action_item)
				db.session.commit()
				return 'updated'
			elif request.method == 'DELETE':
				action_item = Action.query.get(id)
				db.session.delete(action_item)
				db.session.commit()
				return 'deleted'
			else:
				return 'Method Not Allowed'
		else:
			if request.method == 'GET':
				action_list = Action.query.filter(Action.user_id == session["user"]["id"])
				if action_list:
					entries = [action.dto() for action in action_list]
				else:
					entries=None
				activities = [item.dto() for item in Activity.query.all()]
				return render_template('action.html', user=session["user"], activities=activities, action_entries = entries, title = "My Actions")
			elif request.method == 'POST':
				user_id = session["user"]["id"]
				
				new_action = Action(
								user_id = user_id,
								activity_id = activity_id,
								score = score,
								time = datetime.now()
								)
				db.session.add(new_action)
				if score < 0.0 or score > 0.0:
					user = User.query.get(session["user"]["id"])
					if not user.total_score:
						user.total_score = score
					else:
						user.total_score += score
					db.session.add(user)
				db.session.commit()
				session["message"] = "Action tracked!!"
				return redirect(url_for('index'))
			else:
				return 'Method Not Allowed'
	else:
		return redirect(url_for('index'))

@app.route('/action/add/')
def action_add_controller():
	#this is the controller to add new model entries
	return render_template('action_add.html', title = "Add New Entry")

@app.route('/action/edit/<id>')
def action_edit_controller(id):
	#this is the controller to edit model entries
	action_item = Action.query.get(id)
	return render_template('action_edit.html', action_item = action_item, title = "Edit Entries")



########### activity data model controllers area ###########

@app.route('/activity/',methods=['GET','POST'],defaults={'id':None})
@app.route('/activity/<id>',methods=['GET','PUT','DELETE'])
def activity_controller(id):
	name = request.values.get('name')
	score = request.values.get('score')

	if id:
		if request.method == 'GET':
			activity = Activity.query.get(id)
			if activity:
				activity = activity.dto()
			if request.values.get('json'):
				return json.dumps(dict(activity=activity))
			else:
				return render_template('activity_view.html', activity = activity)
		elif request.method == 'PUT':
			activity_item = Activity.query.get(id)
			activity_item.name = name
			activity_item.score = score
			db.session.add(activity_item)
			db.session.commit()
			return 'updated'
		elif request.method == 'DELETE':
			activity_item = Activity.query.get(id)
			db.session.delete(activity_item)
			db.session.commit()
			return 'deleted'
		else:
			return 'Method Not Allowed'
	else:
		if request.method == 'GET':
			activity_list = Activity.query.all()
			if activity_list:
				entries = [activity.dto() for activity in activity_list]
			else:
				entries=None
			if request.values.get('json'):
				return json.dumps(dict(activity=entries))
			else:
				return render_template('activity.html',activity_entries = entries, title = "Activity List")
		elif request.method == 'POST':
			new_activity = Activity(
							name = name,
							score = score
							)

			db.session.add(new_activity)
			db.session.commit()
			if request.values.get('json'):
				url = '/activity/json=true'
			else:
				url = '/activity/'
			return redirect(url)
		else:
			return 'Method Not Allowed'

@app.route('/activity/add/')
def activity_add_controller():
	#this is the controller to add new model entries
	return render_template('activity_add.html', title = "Add New Entry")

@app.route('/activity/edit/<id>')
def activity_edit_controller(id):
	#this is the controller to edit model entries
	activity_item = Activity.query.get(id)
	return render_template('activity_edit.html', activity_item = activity_item, title = "Edit Entries")

@app.route('/login',methods=["POST","GET"])
def login():
	email = request.values.get('email')
	password = request.values.get('password')
	hasher = hashlib.md5()
	hasher.update(password)
	password = hasher.hexdigest()
	check_user = User.query.filter(User.email == email, User.password == password).first()
	if check_user:
		session["user"] = check_user.dto()
	return redirect(url_for('index'))

@app.route('/logout')
def logout():
	session.pop("user",None)
	return redirect(url_for('index'))

@app.route('/profile')
def profile_control():
	if "user" in session:
		user = User.query.get(session["user"]["id"])
		acts = [item.dto() for item in user.action]
		acts = multikeysort(acts, ['-id'])
		return render_template('user_view.html', user=user.dto(), acts=acts[:20])

@app.route('/ranks/city')
def city_rank():
	if "user" in session:
		user = User.query.get(session["user"]["id"])
		ranks = User.query.filter(User.city == session["user"]["city"]).order_by("total_score desc").all()
		ranks = [item.dto() for item in ranks]
		return render_template("ranks.html", ranks=ranks, user=user.dto(),area="City")
	else:
		return redirect(url_for('global_rank'))

@app.route('/ranks')
@app.route('/ranks/')
def global_rank():
	if "user" in session:
		user = User.query.get(session["user"]["id"])
		ranks = User.query.order_by("total_score desc").all()
		ranks = [item.dto() for item in ranks]
		return render_template("ranks.html", ranks=ranks, user = user.dto(),area="Global")	
	else:
		ranks = User.query.order_by("total_score desc").all()
		ranks = [item.dto() for item in ranks]
		return render_template("ranks.html", ranks=ranks, area="Global")