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
    # Caixa de login centralizada com cores modernas
    html_code = """
    <style>
      body {
        margin:0;
        padding:0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height:100vh;
        display:flex;
        justify-content:center;
        align-items:center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      }
      .login-box {
        background-color:#ffffff;
        padding:50px 40px;
        border-radius:20px;
        box-shadow:0 10px 30px rgba(0,0,0,0.2);
        width:360px;
        text-align:center;
        transition: all 0.3s ease;
      }
      .login-box:hover {
        transform: translateY(-5px);
        box-shadow:0 15px 35px rgba(0,0,0,0.25);
      }
      .login-box h2 {
        margin-bottom:20px;
        color:#333;
        font-weight: 700;
        font-size:22px;
      }
      .login-box p {
        color:#666;
        font-size:14px;
        margin-bottom:25px;
      }
      .stTextInput>div>div>input {
        border-radius:10px;
        padding:12px;
        border:1px solid #ddd;
        width:100%;
        font-size:16px;
      }
      .stButton>button {
        width:100%;
        padding:14px;
        margin-top:15px;
        border-radius:10px;
        border:none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color:white;
        font-size:17px;
        font-weight:bold;
        cursor:pointer;
        transition: all 0.3s ease;
      }
      .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
      }
    </style>
    <div class="login-box">
        <h2>CADEIA DE CUSTÓDIA NA ERA DIGITAL</h2>
        <p>Painel Acadêmico Demonstrativo</p>
    </div>
    """
    components.html(html_code, height=300)

    # Formulário Streamlit centralizado
    col1, col2, col3 = st.columns([2,1,2])
    with col2:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
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
