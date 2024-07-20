import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

def show_dashboard():
    st.title("Dashboard")

    # Configurações do Pyrebase usando variáveis de ambiente
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

    # Função para obter dados do Firestore
    @st.cache_data
    def get_data():
        db = firestore.client()
        printers_ref = db.collection('impressoras')
        docs = printers_ref.stream()
        data = []
        for doc in docs:
            data.append(doc.to_dict())
        return data

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

    # Página de Dashboard
    st.sidebar.title('Monitor I7 T.I.')
    st.sidebar.markdown('### Menu')
    menu = ['Dashboard', 'Locais', 'Relatórios', 'Helpdesk', 'Contas', 'Notificações', 'Suprimentos', 'Downloads', 'Ajuda']
    choice = st.sidebar.selectbox('Selecione uma opção', menu)

    if choice == 'Dashboard':
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

    # Página de Locais
    elif choice == 'Locais':
        st.title('Locais')
        locais = get_data()

        # Definir as colunas da tabela
        colunas = ['Local', 'Status', 'Impressoras', 'Total PB', 'Total Color']
        tabela = []

        # Construir a tabela com os dados dos locais
        for local in locais:
            # Obter o status do local e formatar como texto HTML
            status = local.get('Status', 'Offline')  # Default para 'Offline' caso não exista status
            status_text = f"<span style='color: green;'>Online</span>" if status == "Online" else f"<span style='color: red;'>Offline</span>"
            tabela.append([local.get('Local', 'N/A'), status_text, local.get('Impressoras', 'N/A'), local.get('Total PB', 'N/A'), local.get('Total Color', 'N/A')])

        # Exibir a tabela usando st.markdown para renderizar HTML
        df = pd.DataFrame(tabela, columns=colunas)
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)

        # Verificar se há um local selecionado
        params = st.query_params
        selected_local = params.get("local", [None])[0]

        if selected_local:
            exibir_detalhes_local(selected_local)

    elif choice == 'Relatórios':
        st.title('Relatórios')
        st.write('Página de Relatórios em construção...')

    elif choice == 'Helpdesk':
        st.title('Helpdesk')
        st.write('Página de Helpdesk em construção...')

    elif choice == 'Notificações':
        st.title('Notificações')
        st.write('Página de Notificações em construção...')

    elif choice == 'Suprimentos':
        st.title('Suprimentos')
        st.write('Página de Suprimentos em construção...')

    elif choice == 'Downloads':
        st.title('Downloads')
        st.write('Página de Downloads em construção...')

    elif choice == 'Ajuda':
        st.title('Ajuda')
        st.write('Página de Ajuda em construção...')
