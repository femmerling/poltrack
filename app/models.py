from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(50))
	first_name = db.Column(db.String(50))
	last_name = db.Column(db.String(50))
	password = db.Column(db.String(50))
	total_score = db.Column(db.Float,default=0.0)
	country = db.Column(db.String(50))
	city = db.Column(db.String(50))
	join_date = db.Column(db.DateTime)
	action = db.relationship('Action', backref='user', lazy='dynamic')


	# data transfer object to form JSON
	def dto(self):
		return dict(
				id = self.id,
				email = self.email,
				first_name = self.first_name,
				last_name = self.last_name,
				total_score = self.total_score,
				password = self.password,
				country = self.country,
				city = self.city,
				join_date = self.join_date)

class Action(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	score = db.Column(db.Float)
	time = db.Column(db.DateTime)
	
	# data transfer object to form JSON
	def dto(self):
		activity = self.activity.name
		return dict(
				id = self.id,
				activity_id = self.activity_id,
				score = self.score,
				time = self.time.isoformat(),
				activity = activity)
	
	def total_comment(self):
		comments = [item.dto() for item in self.comment]
		return len(comments)

class Activity(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	score = db.Column(db.Float)
	action = db.relationship('Action',backref='activity',lazy='dynamic')
	# data transfer object to form JSON
	def dto(self):
		return dict(
				id = self.id,
				name = self.name,
				score = self.score)
