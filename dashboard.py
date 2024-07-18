import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import requests
import json
import os

# Configurar a página do Streamlit como a primeira instrução
st.set_page_config(layout="wide")

# Configurações do Pyrebase
firebase_config = {
    "apiKey": "AIzaSyDtuEAx1X9f7kB3zl83btfA23k16qQjDsY",
    "authDomain": "status-printer.firebaseapp.com",
    "databaseURL": "https://status-printer.firebaseio.com",
    "projectId": "status-printer",
    "storageBucket": "status-printer.appspot.com",
    "messagingSenderId": "559633962179",
    "appId": "1:559633962179:web:abc123def456",
    "measurementId": "G-measurementid"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

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

# Verificar se o Firebase já está inicializado
if not firebase_admin._apps:
    # Inicializar Firebase Admin SDK com credenciais do arquivo JSON baixado
    try:
        cred = credentials.Certificate(file_path)
        firebase_admin.initialize_app(cred)
        st.success("Firebase inicializado com sucesso.")
    except Exception as e:
        st.error(f"Erro ao inicializar Firebase: {e}")

# Função para realizar login via Pyrebase
def login_via_pyrebase(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        return None

# Função para realizar o login
def login(email, password):
    user = login_via_pyrebase(email, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        st.success(f"Bem-vindo, {email}!")
        st.experimental_rerun()
    else:
        st.error("Erro ao realizar login. Verifique suas credenciais.")

# Tela de login
def login_screen():
    st.title("Login no Sistema")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")
    if st.button("Login"):
        login(email, password)

# Verificar se o usuário está logado
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_screen()
else:
    # Inicializar Firestore apenas se o Firebase Admin SDK estiver inicializado
    if firebase_admin._apps:
        db = firestore.client()

        # Sidebar do Streamlit
        st.sidebar.title('Monitor I7 T.I.')
        st.sidebar.markdown('### Menu')
        menu = ['Dashboard', 'Locais', 'Relatórios', 'Helpdesk', 'Contas', 'Notificações', 'Suprimentos', 'Downloads', 'Ajuda']
        choice = st.sidebar.selectbox('Selecione uma opção', menu)

        # Função para obter dados do Firestore
        @st.cache_data
        def get_data():
            printers_ref = db.collection('impressoras')
            docs = printers_ref.stream()
            data = []
            for doc in docs:
                data.append(doc.to_dict())
            return data

        # Função para criar um novo usuário
        def create_user(email, password, display_name):
            user = auth.create_user(
                email=email,
                email_verified=False,
                password=password,
                display_name=display_name,
                disabled=False
            )
            return user

        # Função para exibir detalhes do local
        def exibir_detalhes_local(local_name):
            locais = get_data()
            local_details = next((item for item in locais if item['Local'] == local_name), None)
            if local_details:
                st.header(f"Detalhes de {local_name}")
                st.write("Impressoras:")
                for printer in local_details.get('Impressoras', []):
                    st.write(printer)
                st.write("Total PB:", local_details.get('Total PB', 'N/A'))
                st.write("Total Color:", local_details.get('Total Color', 'N/A'))
            else:
                st.write("Não há detalhes disponíveis para este local.")

        # Página de Locais
        if choice == 'Locais':
            st.title('Locais')
            locais = get_data()

            colunas = ['Local', 'Status', 'Impressoras', 'Total PB', 'Total Color']
            tabela = []
            for local in locais:
                status = "Online" if local.get('Status') == "Online" else "Offline"
                status_text = f"<span style='color: green;'>{status}</span>" if status == "Online" else f"<span style='color: red;'>{status}</span>"
                tabela.append([local['Local'], status_text, local['Impressoras'], local['Total PB'], local['Total Color']])

            # Exibir tabela usando st.dataframe para uma melhor interação
            df = pd.DataFrame(tabela, columns=colunas)
            st.dataframe(df)

            # Verificar se há um local selecionado
            params = st.query_params
            selected_local = params.get("local", [None])[0]

            if selected_local:
                exibir_detalhes_local(selected_local)

        # Página de Contas
        elif choice == 'Contas':
            st.title('Contas')
            
            # Formulário para adicionar novo usuário
            with st.form(key='user_form'):
                email = st.text_input('Email')
                password = st.text_input('Senha', type='password')
                display_name = st.text_input('Nome de Exibição')
                submit_button = st.form_submit_button(label='Adicionar Usuário')

            if submit_button:
                try:
                    user = create_user(email, password, display_name)
                    st.success(f'Usuário {user.display_name} criado com sucesso!')
                except Exception as e:
                    st.error(f'Erro ao criar usuário: {e}')

            # Exibir lista de usuários
            users = auth.list_users().users
            for user in users:
                st.write(f'Nome: {user.display_name}, Email: {user.email}')

        # Página de Dashboard
        elif choice == 'Dashboard':
            st.title('Dashboard')
            st.header('Tickets')
            st.markdown('Nenhum ticket em aberto.')

            st.header('Locais')
            locais = get_data()
            for local in locais:
                st.write(local['Local'], '-', local['Status'], '-', local['Impressoras'], '-', local['Total PB'], '-', local['Total Color'])

            st.header('Equipamentos')
            for local in locais:
                if 'detalhes_impressora' in local:
                    st.write(local['detalhes_impressora']['Modelo'], '-', local['detalhes_impressora']['ID'])

            st.header('Logs')
            for local in locais:
                st.write(local['timestamp'], '-', local['Local'])

        # Página de Relatórios
        elif choice == 'Relatórios':
            st.title('Relatórios')
            st.write('Página de Relatórios em construção...')

        # Página de Helpdesk
        elif choice == 'Helpdesk':
            st.title('Helpdesk')
            st.write('Página de Helpdesk em construção...')

        # Página de Notificações
        elif choice == 'Notificações':
            st.title('Notificações')
            st.write('Página de Notificações em construção...')

        # Página de Suprimentos
        elif choice == 'Suprimentos':
            st.title('Suprimentos')
            st.write('Página de Suprimentos em construção...')

        # Página de Downloads
        elif choice == 'Downloads':
            st.title('Downloads')
            st.write('Página de Downloads em construção...')

        # Página de Ajuda
        elif choice == 'Ajuda':
            st.title('Ajuda')
            st.write('Página de Ajuda em construção...')
    else:
        st.error("Erro ao inicializar o Firebase Admin SDK. Verifique as credenciais e tente novamente.")
