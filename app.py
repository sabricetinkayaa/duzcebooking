from flask import Flask,render_template,flash,redirect,url_for,request
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import InputRequired,Email,Length,EqualTo
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from datetime import datetime
from sqlalchemy import Date, cast,and_

app = Flask(__name__)

#Config
app.config['SECRET_KEY']='a random string'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy(app)
'''
USER_APP_NAME = "Flask-User Basic App"      # Shown in and email templates and page footers
USER_ENABLE_EMAIL = True        # Enable email authentication
USER_ENABLE_USERNAME = False    # Disable username authentication
USER_EMAIL_SENDER_NAME = USER_APP_NAME
USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
'''
#login initialize
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Tables
class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(),unique=True)
    email = db.Column(db.String())
    password = db.Column(db.String())
    reservations= db.relationship('Reservation',backref='user')
    bonus = db.Column(db.Integer)
    #roles = db.relationship('Role', secondary='user_roles')
    '''
class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50))
class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
'''
class Room(db.Model):
    roomno = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    floorno = db.Column(db.Integer)
    childbed = db.Column(db.Integer)
    adultbed = db.Column(db.Integer)
    roomtype = db.Column(db.String(255))
    inDate = db.Column(db.Date)
    outDate=db.Column(db.Date)
    isreserve = db.Column('is_reserve',db.Boolean)
    reservations = db.relationship('Reservation',backref='room')
class Reservation(db.Model):
    invoiceno=db.Column(db.Integer,primary_key=True)
    time=db.Column(db.DateTime,index=True,default=datetime.now())
    totalamount=db.Column(db.Float)
    userid=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'))
    roomno=db.Column(db.Integer,db.ForeignKey('room.roomno',ondelete='CASCADE'))  
class Baskets(db.Model):
    basketno=db.Column(db.Integer,primary_key=True)
    roomno=db.Column(db.Integer,db.ForeignKey('room.roomno',ondelete='CASCADE'))
    userid=db.Column(db.Integer,db.ForeignKey('user.id',ondelete='CASCADE'))
    price = db.Column(db.Integer)
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
'''
user_manager = UserManager(app,db,User)

    # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
if not User.query.filter(User.email == 'admin@example.com').first():
    user = User(username='Admin',email='admin@example.com',password=user_manager.hash_password('Password1'))
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()


user = User(username='Admin',email='admin@example.com',password=generate_password_hash('123','sha256'))
user.roles.append(Role(name='Admin'))
#user.roles.append(Role(name='Agent'))
db.session.add(user)
db.session.commit()
'''

db.create_all()


#Formlar
class LoginForm(FlaskForm):
    username = StringField('username',validators=[InputRequired()])
    password = PasswordField('password',validators=[InputRequired()])
    submit = SubmitField('Login')
class RegisterFrom(FlaskForm):
    username = StringField('username',validators=[InputRequired()])
    email = StringField('email',validators=[InputRequired(),Email()])
    password = PasswordField('password',validators=[InputRequired()])
    confirm_password = PasswordField('confirm_password',validators=[InputRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

#Routes
@app.route('/')
def index():
    '''
    room1 = Room(price=1500,capacity=3,floorno=2,childbed=1,adultbed=2,roomtype='Suite',isreserve = 0)
    db.session.add(room1)
    db.session.commit()
    room2 = Room(price=1000,capacity=2,floorno=1,childbed=0,adultbed=2,roomtype='Family',isreserve = 1)
    db.session.add(room2)
    db.session.commit()

    reservation = Reservation(totalamount=1000,userid=1,roomno=2,inDate=datetime.strptime('17/12/19', '%d/%m/%y'),outDate=datetime.strptime('27/12/19', '%d/%m/%y'))
    db.session.add(reservation)
    db.session.commit()
    '''
    return render_template('index.html')
@app.route('/rooms',methods=['GET','POST'])
def rooms():
    if request.method == 'POST':
        
        indateold = str(request.form.get('indate'))
        indatesplited = indateold.split('/')
        month = indatesplited[0]
        day = indatesplited[1]
        year = indatesplited[2]
        indate = str(year+'-'+month+'-'+day)
        outdateold = str(request.form.get('outdate'))
        outdatesplited = outdateold.split('/')
        outdate= str(outdatesplited[2]+'-'+outdatesplited[0]+'-'+outdatesplited[1])
        roomtype = str(request.form.get('roomtype'))
        adultbed = int(request.form.get('customer'))
        print(roomtype)
        
        #search = indate+" "+ outdate + " "+ roomtype + " " + customer
        #result = db.session.query(Room).filter(Room.inDate>=indate,Room.outDate<=outdate,Room.roomtype=='Suit',Room.isreserve==0)
        #result = db.session.query(Room).filter_by(roomno=2).all()
        #result = db.session.query(Room).filter_by(and_(roomtype=='Suit',isreserve==0)   ).all() Yanlış
        result = Room.query.filter(Room.roomtype==roomtype).filter(Room.isreserve==0).filter(Room.inDate<=indate).filter(Room.outDate>=outdate).all() #Çalışıyor!
        #result = Room.query.filter(Room.inDate>=datetime.strptime('2019-12-19','%Y-%m-%d'),Room.outDate>=datetime.strptime('2019-12-25','%Y-%m-%d'),Room.roomtype=='Suit',Room.isreserve==0).all()
        #print(result)
        return render_template('rooms.html',result=result)
    if request.method == 'GET':
        return render_template('rooms.html')
    return render_template('rooms.html')
@app.route('/roomdetail')
def roomdetail():
    return render_template('roomdetail.html')
@app.route('/about')
@login_required
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                login_user(user)
                flash(f'You logged {form.username.data}','success')
        else:
            flash('Invald passwrod or username','error')
        
    return render_template('login.html',form=form)
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterFrom()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data,method='sha256')
        new_user = User(username=form.username.data,email=form.email.data,password =hashed_password,bonus=0)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account created for {form.username.data}','success')
    return render_template('register.html',form=form)

@app.route('/logout')
@login_required
def logout():
    Baskets.query.filter_by(userid=current_user.id).delete()
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        price = int(request.form.get('price'))
        capacity = int(request.form.get('capacity'))
        floorno = int(request.form.get('floorno'))
        childbed = int(request.form.get('childbed'))
        adultbed= int(request.form.get('adultbed'))
        roomtype = request.form.get('roomtype')
        inDate = datetime.strptime(request.form.get('inDate'),'%Y-%m-%d')
        outDate = datetime.strptime(request.form.get('outDate'),'%Y-%m-%d')
        isreserve = str(request.form.get('isreserve'))
        if isreserve == 'on':
            isreserve ='1'
        elif isreserve == 'None':
            isreserve = '0'
        room = Room(price=price,capacity=capacity,floorno=floorno,childbed=childbed,adultbed=adultbed,roomtype=roomtype,inDate=inDate,outDate=outDate,isreserve=int(isreserve))
        db.session.add(room)
        db.session.commit()
    '''elif request.method == 'GET':
        if current_user:
            return render_template('login.html')
        elif current_user.username == 'Admin':
            return render_template('admin.html')
        '''
        
        
    return render_template('admin.html')
@login_required
@app.route('/book/<roomno>/<price>',methods=['GET','POST'])
def book(roomno,price):
    bas=Baskets(userid=current_user.id,roomno=roomno,price=price)
    db.session.add(bas)
    db.session.commit()
    return render_template('index.html')
@login_required
@app.route('/listbasket')
def listbasket():
    list=db.session.query(Baskets).filter_by(userid=current_user.id)
    return render_template('basket.html',list=list)

@login_required
@app.route('/reservations')
def reservations():
    result=db.session.query(Reservation).filter(Reservation.userid==current_user.id).all()
    return render_template('info.html',result=result)

@login_required
@app.route('/insres/<roomno>/<basketno>')#sepetten rezervasyon ekleme
def insres(roomno,basketno):
    room=Room.query.get(roomno)
    bas=Baskets.query.get(basketno)
    res=Reservation(userid=current_user.id,roomno=room.roomno,totalamount=bas.price)
    db.session.commit()
    db.session.add(res)
    addbonus=current_user.bonus
    addbonus+=room.price*0.03
    current_user.bonus=addbonus
    room=Room.query.get(roomno)
    room.isreserve=True
    Baskets.query.filter_by(basketno=basketno).delete()
    db.session.commit()
    return render_template('info.html')

@login_required
@app.route('/insresdirect/<roomno>')
def insresdirect(roomno):
    room=Room.query.get(roomno)
    res=Reservation(userid=current_user.id,roomno=room.roomno,totalamount=room.price)
    db.session.add(res)
    addbonus=current_user.bonus
    addbonus+=room.price*0.03
    current_user.bonus=addbonus
    room=Room.query.get(roomno)
    room.isreserve=True
    db.session.commit()
    return render_template('info.html')
    


@login_required
@app.route('/delres/<invoiceno>/<roomno>')
def delres(invoiceno,roomno):
    Reservation.query.filter_by(invoiceno=invoiceno).delete()
    room=Room.query.get(roomno)
    room.isreserve=False
    db.session.commit()
    return redirect(url_for('reservations'))

@login_required
@app.route('/delbasket/<basketno>')
def delbasket(basketno):
    Baskets.query.filter_by(basketno=basketno).delete()
    db.session.commit()
    return redirect(url_for('listbasket'))

@login_required
@app.route('/usebonus/<basketno>/<price>')
def usebonus(basketno,price):
    bas=Baskets.query.get(basketno)
    bas.price=bas.price-current_user.bonus
    current_user.bonus=0
    db.session.commit()
    return redirect(url_for('listbasket'))

@login_required
@app.route('/countroom')
def countroom():
    odalar=Room.query.get('is_reserve')
    query = odalar.count()
    print(odalar)

app.run(debug=True)