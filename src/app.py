from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from dotenv import load_dotenv
from os import getenv
from flask_mysqldb import MySQL
import smtplib, ssl
import getpass
import random
from jwt import encode, decode
from jwt import exceptions
from datetime import datetime, timezone, timedelta

load_dotenv()

app = Flask(__name__)

app.config['MYSQL_HOST'] = getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = getenv('MYSQL_DB')
app.secret_key = getenv('SECRET_KEY')

mysql = MySQL(app)

@app.route('/')
def index():

    return render_template('bienvenida.html')

@app.route('/login')
def login():
    return render_template('log_in.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/verificateemail')
def verificate():
    return render_template('emailForResetPass.html')

@app.route('/verificatecode')
def verificatecode():
    return redirect(url_for('login'))

@app.route('/validar-token/<token>', methods=['GET'])
def validate_token(token):
    try:
        if output:
             return decode(
                token, 
                key=getenv('SECRET'), 
                algorithms=['HS256']
                )

        decode(token, key=getenv('SECRET'), algorithms=['HS256'])

        return render_template('reset_password.html')

    except exceptions.DecodeError as e:
        
        response = jsonify({'message': 'Invalid token'})
        response.status_code = 401

        return response 

    except exceptions.ExpiredSignatureError as e:

        response = jsonify({'message': 'Token Expired'})
        response.status_code = 401

        return response 

@app.route('/newpassword/<token>', methods=['POST'])
def newpassword(token):
    return 'hola'


@app.route('/forgotpassword', methods=['POST'])
def reset():
    email = request.form.get('email')
    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM registrados WHERE email = %s', (email,))

    data = cur.fetchone()

    if not data:  
        return 'Este correo electronico no existe en la base de datos'

    print(email)
    print(data)
    
    token = encode(
        payload={
            'email': email, 
            'exp': datetime.now(tz=timezone.utc) + timedelta(hours=1)
            },
        key=getenv('SECRET'),
        algorithm='HS256')

    print(token)

    reset_link = f"http://127.0.0.1:5000/validar-token/{token}"

    mysql.connection.commit()

    port = 465
    password = 'lfok kejs iytx zfiz'

    sender_mail = "barellanutellacucurella426@gmail.com"
    receiver_mail = email
    server_domain = "smtp.gmail.com"

    msg = f'''Subject: Código de verificacion
    To:{email}@gmail.com    
    
    {reset_link}

    '''

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(server_domain,
                        port,
                        context=context) as s:

        s.login(sender_mail, password)
        s.sendmail(sender_mail, receiver_mail, msg.encode('UTF-8'))

    print("Email enviado de forma correcta!!!")

    return jsonify({'message': 'Correo enviado de forma correcta'}), 200

@app.route('/add_user', methods=['POST'])
def add_user():
    print(request.form)
    fullname = request.form.get('fullname')
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    print(fullname, username, password, email)

    cur = mysql.connection.cursor()

    cur.execute('INSERT INTO registrados (fullname, username, contra, email) VALUES (%s,%s,%s,%s)', (fullname, username, password, email))

    mysql.connection.commit()

    return redirect(url_for('login'))

@app.route('/verificate_user', methods=['POST'])
def log_user():
    username = request.form.get('username')
    password = request.form.get('password')

    print(username, password)

    cur = mysql.connection.cursor()

    cur.execute('SELECT * FROM registrados WHERE username = %s && contra = %s', (username,password))

    data = cur.fetchone()

    if not data:  
        return 'este usuario no existe en la base de datos, intentelo de nuevo'
    print(data)
    
    mysql.connection.commit()

    return render_template('inicio.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')