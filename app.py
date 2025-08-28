# from flask import Flask, render_template, url_for

# app = Flask(__name__)

# @app.context_processor
# def inject_brand():
#     return {"brand": "AMO Solutions"}

# @app.route("/")
# def index():
#     return render_template("index.html", page_title="Home")

# @app.route("/engineering")
# def engineering():
#     return render_template("engineering.html", page_title="Engineering Solutions!")

# @app.route("/cotations")
# def cotations():
#     return render_template("cotations.html", page_title="Cotations")

# @app.route("/others")
# def others():
#     return render_template("others.html", page_title="Others Applications")

# @app.route("/projects")
# def projects():
#     return render_template("projects.html", page_title="Projects")

# @app.route("/about")
# def about():
#     return render_template("about.html", page_title="About US")

# app.config['TEMPLATES_AUTO_RELOAD'] = True
# if __name__ == "__main__":
#     # Use `flask --app app --debug run` em desenvolvimento (recomendado)
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # obrigatório para sessões

DB_NAME = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Context processor para usar {{ brand }} e {{ now().year }}
@app.context_processor
def inject_brand():
    from datetime import datetime
    return {"brand": "AMO Solutions", "now": datetime.now}

# Home
@app.route('/')
def index():
    return render_template('index.html', page_title="Home")

@app.route('/engineering')
def engineering():
    return render_template('engineering.html', page_title="Engineering Solutions")

@app.route('/cotations')
def cotations():
    if not session.get('user_id'):
        flash("Faça login para acessar Cotations.")
        return redirect(url_for('login'))
    return render_template('cotations.html', page_title="Cotations")

@app.route('/others')
def others():
    return render_template('others.html', page_title="Others Applications")

@app.route('/projects')
def projects():
    return render_template('projects.html', page_title="Projects")

@app.route('/about')
def about():
    return render_template('about.html', page_title="About US")

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # pode ser email ou username
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? OR username=?", (identifier, identifier))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            flash(f"Bem-vindo(a), {user['full_name']}!")
            return redirect(url_for('cotations'))
        else:
            flash("Usuário ou senha incorretos.")
            return redirect(url_for('login'))

    return render_template('login.html', page_title="Login")

# Página de cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (full_name, username, email, password) VALUES (?, ?, ?, ?)",
                (full_name, username, email, password)
            )
            conn.commit()
            conn.close()
            flash("Cadastro realizado com sucesso! Faça login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email ou usuário já cadastrado.")
            return redirect(url_for('register'))

    return render_template('register.html', page_title="Cadastro")

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Você foi desconectado.")
    return redirect(url_for('index'))

app.config['TEMPLATES_AUTO_RELOAD'] = True
if __name__ == "__main__":
    app.run(debug=True)
