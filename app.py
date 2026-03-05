# streamlit_app.py
import streamlit as st
import pandas as pd
import random
import streamlit.components.v1 as components

st.set_page_config(page_title="Cadeia de Custódia", layout="wide")

# =============================
# ESTADO
# =============================
if "logado" not in st.session_state:
    st.session_state.logado = False

# =============================
# FUNÇÃO DADOS ALUNOS
# =============================
def gerar_alunos():
    nomes = [
        "Ana Silva", "Bruno Costa", "Carla Mendes",
        "Daniel Souza", "Eduarda Lima", "Felipe Rocha",
        "Gabriela Alves", "Henrique Martins",
        "Isabela Ramos", "João Ferreira"
    ]
    dados = []
    for nome in nomes:
        nota1 = random.randint(4,10)
        nota2 = random.randint(4,10)
        media = round((nota1 + nota2)/2,1)
        status = "Aprovado" if media >=6 else "Reprovado"
        dados.append([nome, nota1, nota2, media, status])
    df = pd.DataFrame(dados, columns=["Aluno","Nota 1","Nota 2","Média","Status"])
    return df

# =============================
# LOGIN ESTILIZADO
# =============================
def tela_login():
    # HTML + CSS moderno inspirado no portal
    html_code = """
    <style>
      body {
        margin:0;
        padding:0;
        font-family: 'Nunito', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
      .login-container {
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
      }
      .login-card {
        background-color: #fff;
        padding: 40px 30px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        width: 360px;
        text-align: center;
        transition: all 0.3s ease;
      }
      .login-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.25);
      }
      .login-card h2 {
        font-size: 22px;
        font-weight: 700;
        color: #333;
        margin-bottom: 10px;
      }
      .login-card p {
        font-size: 14px;
        color: #666;
        margin-bottom: 25px;
      }
      .stTextInput>div>div>input {
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #ddd;
        font-size: 16px;
        width: 100%;
        margin-bottom: 15px;
      }
      .stButton>button {
        width: 100%;
        padding: 14px;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        font-size: 17px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
      }
      .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
      }
    </style>

    <div class="login-container">
      <div class="login-card">
        <h2>Portal Universitas</h2>
        <p>Acesso exclusivo para alunos, professores e coordenadores</p>
      </div>
    </div>
    """
    components.html(html_code, height=250)

    # Formulário Streamlit
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        usuario = st.text_input("Matrícula / Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if usuario == "dantas" and senha == "1234":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

# =============================
# CONTROLE
# =============================
if not st.session_state.logado:
    tela_login()
else:
    tela_sistema()
