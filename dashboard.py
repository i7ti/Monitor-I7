import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
import os

# Carregar variáveis de ambiente do sistema
# As variáveis já estão carregadas no ambiente de produção do Render

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

    try:
        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
        st.success("Pyrebase configurado com sucesso.")
    except Exception as e:
        st.error(f"Erro ao configurar o Pyrebase: {e}")

    # Verificar se o Firebase já está inicializado
    if not firebase_admin._apps:
        try:
            # Configurar as credenciais diretamente com variáveis de ambiente
            cred = credentials.Certificate({
                "type": os.getenv("FIREBASE_TYPE"),
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
            })
            firebase_admin.initialize_app(cred)
            st.success("Firebase inicializado com sucesso.")
        except Exception as e:
            st.error(f"Erro ao inicializar Firebase: {e}")

    # Função para obter dados do Firestore
    @st.cache_data
    def get_data():
        try:
            db = firestore.client()
            printers_ref = db.collection('impressoras')
            docs = printers_ref.stream()
            data = [doc.to_dict() for doc in docs]
            return data
        except Exception as e:
            st.error(f"Erro ao obter dados: {e}")
            return []

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
            status = local.get('Status', 'Offline')
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
