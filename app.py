from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Mantenha isso seguro em produção

# Exemplo simples de usuário (substitua por um modelo de usuário real)
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# Simulação de um banco de dados de usuários
users_db = [
    User('usuario1', 'senha1'),
    User('usuario2', 'senha2')
]

# Função para verificar autenticação do usuário
def user_is_authenticated(username, password):
    for user in users_db:
        if user.username == username and user.password == password:
            return True
    return False

@app.route('/')
def index():
    return 'Página inicial'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificação de senha (substitua por lógica real)
        if user_is_authenticated(username, password):
            return redirect(url_for('dashboard'))
        else:
            return 'Credenciais inválidas. Tente novamente.'

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return 'Dashboard protegida'

@app.route('/authenticated', methods=['POST'])
def authenticated():
    if user_is_authenticated(request.form['username'], request.form['password']):
        return jsonify({'message': 'Authenticated'}), 200
    else:
        return jsonify({'message': 'Not Authenticated'}), 401

if __name__ == '__main__':
    app.run(debug=True)
