import streamlit as st
import os
import requests
import pyrebase
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
import base64

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Função para baixar a chave JSON do Firebase Storage
def get_firebase_credentials():
    url = os.getenv("FIREBASE_CREDENTIALS_URL")
    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            file_path = "firebase_credentials.json"
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        except requests.RequestException as e:
            st.error(f"Erro ao baixar a chave do Firebase: {e}")
            return None
    else:
        st.error("Variável de ambiente 'FIREBASE_CREDENTIALS_URL' não definida.")
        return None

# Função para inicializar o Firebase Admin SDK
def initialize_firebase():
    firebase_credentials_path = get_firebase_credentials()
    if firebase_credentials_path:
        try:
            cred = credentials.Certificate(firebase_credentials_path)
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"Erro ao inicializar Firebase Admin SDK: {e}")

# Inicializar Firebase Admin SDK
initialize_firebase()

# Configurar o Pyrebase usando variáveis de ambiente
firebase_config = {
    "apiKey": os.getenv("API_KEY"),
    "authDomain": os.getenv("AUTH_DOMAIN"),
    "databaseURL": os.getenv("DATABASE_URL"),
    "projectId": os.getenv("PROJECT_ID"),
    "storageBucket": os.getenv("STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("MESSAGING_SENDER_ID"),
    "appId": os.getenv("APP_ID"),
    "measurementId": os.getenv("MEASUREMENT_ID")
}

# Inicializar Pyrebase
try:
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
except Exception as e:
    st.error(f"Erro ao inicializar Pyrebase: {e}")
    st.stop()

# Função de login
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.page = 'dashboard'
    except Exception as e:
        st.error(f"Erro ao realizar login: {e}")

# Inicializar estado da sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Interface de login
if not st.session_state.logged_in:
    st.title("Login no Sistema")
    email = st.text_input("Email", max_chars=50)
    password = st.text_input("Senha", type="password", max_chars=50)
    if st.button("Login"):
        if email and password:
            login(email, password)
        else:
            st.error("Por favor, preencha todos os campos.")
else:
    # Mostrar o logo e permitir que ele redirecione para a dashboard
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
        logo_html = f"""
        <a href="?page=dashboard" style="display:block;text-align:center;">
            <img src="data:image/png;base64,{encoded_image}" width="200">
        </a>
        """
        st.sidebar.markdown(logo_html, unsafe_allow_html=True)
    else:
        st.sidebar.warning(f"O arquivo {logo_path} não foi encontrado.")

    # Mostrar o conteúdo da dashboard se a página for 'dashboard'
    if st.session_state.page == 'dashboard':
        try:
            import dashboard
            dashboard.show_dashboard()
        except ImportError as e:
            st.error(f"Erro ao importar o módulo de dashboard: {e}")
    else:
        st.write("Página não encontrada.")
