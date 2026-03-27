import os
from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Read secret key from file if provided, else from env
secret_key_file = os.getenv('SECRET_KEY_FILE')
if secret_key_file and os.path.exists(secret_key_file):
    with open(secret_key_file, 'r') as f:
        app.secret_key = f.read().strip()
else:
    app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin or user


@app.route('/')
def index():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            return f'Bem-vindo, {session["username"]} (perfil: {user.role})! <a href="/logout">Logout</a>'
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('index'))
        return 'Usuário ou senha inválidos', 401
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# 🍀 Easter Egg: secret leprechaun route
@app.route('/leprechaun')
def leprechaun():
    return "🍀 You found the pot of gold! 🪙 Enjoy a shamrock shake! 🍀"


# 🍀 Easter Egg: custom 404 with leprechaun humour
@app.errorhandler(404)
def not_found(e):
    return "<h1>🍀 Oops! The leprechaun hid this page. Try again! 🍀</h1>", 404


@app.cli.command('init-db')
def init_db():
    """Create tables and populate with test users."""
    db.create_all()
    users = [
        ('admin', generate_password_hash('admin123'), 'admin'),
        ('toni', generate_password_hash('toni123'), 'user'),
        ('zell', generate_password_hash('zell123'), 'user'),
        ('cachorro', generate_password_hash('cachorro123'), 'user')
    ]
    for username, pwd_hash, role in users:
        if not User.query.filter_by(username=username).first():
            user = User(username=username, password=pwd_hash, role=role)
            db.session.add(user)
    db.session.commit()
    print("Banco inicializado com usuários: admin, joao, maria")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)