import streamlit as st
import subprocess

def login():
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button('Login'):
        if username == 'admin' and password == 'admin':
            st.success('Logged in successfully!')
            st.write('Redirecting to dashboard...')
            # Iniciar dashboard.py usando subprocess
            subprocess.Popen(['streamlit', 'run', 'dashboard.py'])
            return True
        else:
            st.error('Invalid username or password.')
            return False

if __name__ == '__main__':
    if login():
        st.stop()  # Para encerrar o aplicativo Streamlit após o redirecionamento iniciar
