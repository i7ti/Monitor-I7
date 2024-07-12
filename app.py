from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Mantenha isso seguro em produção
login_manager = LoginManager()
login_manager.init_app(app)

# Exemplo simples de usuário (substitua por um modelo de usuário real)
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.password = 'senha_encriptada_aqui'

@login_manager.user_loader
def load_user(user_id):
    # Substitua por lógica real para carregar usuário do banco de dados
    return User(user_id)

@app.route('/')
def index():
    return 'Página inicial'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username)

        # Verificação de senha (substitua por lógica real)
        if password == user.password:
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return 'Dashboard protegida'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
