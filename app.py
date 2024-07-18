import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import requests
import os

# Configuração da página do Streamlit
st.set_page_config(page_title="Login App", layout="centered")

# Função para inicializar o Firebase Admin SDK
@st.cache(allow_output_mutation=True)
def initialize_firebase():
    # URL do arquivo JSON no Firebase Storage
    url = "https://firebasestorage.googleapis.com/v0/b/status-printer.appspot.com/o/serviceAccountKey.json?alt=media&token=f4767579-f2a7-469b-b773-750af9a04e3f"
    file_path = "serviceAccountKey.json"

    # Baixar o arquivo JSON se não existir
    if not os.path.exists(file_path):
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(file_path, 'wb') as f:
                f.write(response.content)
            st.success("Arquivo de credenciais baixado com sucesso.")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao baixar o arquivo de credenciais: {e}")
            return None

    # Inicializar Firebase Admin SDK com credenciais do arquivo JSON baixado
    try:
        cred = credentials.Certificate(file_path)
        firebase_admin.initialize_app(cred)
        st.success("Firebase inicializado com sucesso.")
        return auth
    except Exception as e:
        st.error(f"Erro ao inicializar Firebase: {e}")
        return None

# Inicialização do Firebase
auth = initialize_firebase()

if auth is not None:
    # Título e descrição do login
    st.title("Login no Sistema")
    st.write("Por favor, faça login para acessar o sistema.")

    # Formulário de login
    with st.form(key='login_form'):
        email = st.text_input("Email")
        password = st.text_input("Senha", type='password')
        submit_button = st.form_submit_button('Login')

        if submit_button:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.success(f'Login realizado com sucesso! Bem-vindo, {user["email"]}.')
                # Redirecionar para a página principal ou dashboard
                # st.experimental_set_query_params(user=user['email'])  # Exemplo de parâmetro de query para usuário
                # st.experimental_rerun()
            except Exception as e:
                st.error(f'Erro ao realizar login: {e}')

else:
    st.error("Erro ao inicializar o Firebase Admin SDK. Verifique as credenciais e tente novamente.")
