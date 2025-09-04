
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # obrigatório para sessões

DB_NAME = 'users.db'

# Context processor para usar {{ brand }} e {{ now().year }}
@app.context_processor
def inject_brand():
    from datetime import datetime
    return {"brand": "AMO Solutions", "now": datetime.now}


### ----------------------------------  GENERAL -------------------------------------------
# Home -------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html', page_title="Home")

@app.route('/enginee')
def enginee():
    return render_template('Source/engineering.html', page_title="Engineering Solutions")

@app.route('/cotations')
def cotations():
    if not session.get('user_id'):
        flash("Faça login para acessar Cotations.")
        return redirect(url_for('login'))
    return render_template('cotations.html', page_title="Cotations")

@app.route('/others')
def others():
    return render_template('Source/others.html', page_title="Others Applications")

@app.route('/project')
def project():
    return render_template('Source/projects.html', page_title="Projects")

@app.route('/about')
def about():
    return render_template('Source/about.html', page_title="About US")


# Página de login ------------------------------------------------------------------------------
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

    return render_template('Source/login.html', page_title="Login")


# Página de cadastro --------------------------------------------------------------------
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

    return render_template('Source/register.html', page_title="Cadastro")


# Logout ---------------------------------------------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Você foi desconectado.")
    return redirect(url_for('index'))

#--
#--
#--
#--
#--
#--
#--
#--
#--
#--
### ---------------------------------- Engineering Solution -------------------------------------------

@app.route('/voltage_drop')
def voltage_drop():
    return render_template('Enginee/voltage.html', page_title="Voltage Drop")


@app.route('/isa')
def isa():
    return render_template('Enginee/isa-51.html', page_title="ISA 5.1")


@app.route('/excel_upload', methods=['GET', 'POST'])
def excel_upload():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash("Nenhum arquivo enviado.")
            return redirect(url_for('excel_upload'))

        df = pd.read_excel(file)  # lê planilha
        data = df.to_dict(orient="records")  # lista de dicionários [{col1: v1, col2: v2, ...}, ...]

        return render_template("Enginee/excel_table.html", data=data, page_title="Tabela Excel")

    # se for GET, mostra a tela de upload
    return render_template("Enginee/read_table_browser.html", page_title="Upload Excel")


@app.route('/eletro_dim')
def eletro_dim():
    return render_template('Enginee/eletro-dimension.html', page_title="Eletro Dimension")


@app.route('/cabletray_dim')
def cabletray_dim():
    return render_template('Enginee/cabletray-dimension.html', page_title="Cable Tray Dimension")






#Inicia Site
#---------------------------------------------------
app.config['TEMPLATES_AUTO_RELOAD'] = True
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)

