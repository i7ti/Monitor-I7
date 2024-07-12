import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Verificar se o Firebase já está inicializado
if not firebase_admin._apps:
    # Inicializar Firebase Admin SDK
    cred = credentials.Certificate(r'C:\Users\Moises\Documents\Novo\serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

# Inicializar Firestore
db = firestore.client()

# Layout do Streamlit
st.set_page_config(layout="wide")
st.sidebar.title('PrintScout')
st.sidebar.markdown('### Menu')
menu = ['Dashboard', 'Locais', 'Relatórios', 'Helpdesk', 'Contas', 'Notificações', 'Suprimentos', 'Downloads', 'Ajuda']
choice = st.sidebar.selectbox('Selecione uma opção', menu)

# Função para obter dados do Firestore
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

    # Exibir tabela com tamanho das células ajustado
    st.markdown("""
    <style>
    .dataframe {
        width: 100% !important;
    }
    .dataframe td, .dataframe th {
        width: 176px !important;
        height: 70px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Converte a tabela para DataFrame e usa st.write com unsafe_allow_html para renderizar o HTML no status
    df = pd.DataFrame(tabela, columns=colunas)
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Verificar se há um local selecionado
    query_params = st.experimental_get_query_params()
    selected_local = query_params.get("local", [None])[0]

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
