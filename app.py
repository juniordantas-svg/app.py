# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
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
    # HTML + CSS do login
    html_code = """
    <style>
      body {background-color:#f5f5f5; font-family: Arial, sans-serif;}
      .login-container {
        background-color:#fff; padding:40px; border-radius:12px; 
        box-shadow:0 4px 12px rgba(0,0,0,0.15); width:350px; text-align:center;
        margin:auto; margin-top:100px;
      }
      h2 {color:#333; margin-bottom:20px;}
      input {width:80%; padding:10px; margin:10px 0; border-radius:6px; border:1px solid #ccc;}
      button {width:85%; padding:12px; margin-top:15px; border:none; border-radius:6px; background-color:#4CAF50; color:white; font-size:16px; cursor:pointer;}
      button:hover {background-color:#45a049;}
    </style>
    <div class="login-container">
      <h2>CADEIA DE CUSTÓDIA NA ERA DIGITAL</h2>
      <p>Painel Acadêmico Demonstrativo</p>
    </div>
    """
    components.html(html_code, height=200)
    
    # Formulário de login Streamlit
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
# DASHBOARD (APÓS LOGIN)
# =============================
def tela_sistema():
    st.title("📊 Dashboard Acadêmico")
    
    col1, col2 = st.columns([9,1])
    with col2:
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()
    
    st.markdown("---")
    
    # Gerar dados apenas uma vez
    if "df_alunos" not in st.session_state:
        st.session_state.df_alunos = gerar_alunos()
    df = st.session_state.df_alunos
    
    st.subheader("Lista de Alunos (Edite as notas)")
    
    df_editado = st.data_editor(
        df,
        use_container_width=True,
        disabled=["Aluno","Média","Status"],
        num_rows="fixed"
    )
    
    # Recalcular média e status
    df_editado["Média"] = round((df_editado["Nota 1"] + df_editado["Nota 2"])/2,1)
    df_editado["Status"] = df_editado["Média"].apply(lambda x: "Aprovado" if x>=6 else "Reprovado")
    st.session_state.df_alunos = df_editado
    
    st.markdown("---")
    
    # Métricas
    total_alunos = len(df_editado)
    aprovados = len(df_editado[df_editado["Status"]=="Aprovado"])
    reprovados = len(df_editado[df_editado["Status"]=="Reprovado"])
    media_geral = round(df_editado["Média"].mean(),2)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Alunos", total_alunos)
    col2.metric("Aprovados", aprovados)
    col3.metric("Reprovados", reprovados)
    col4.metric("Média Geral", media_geral)
    
    st.markdown("---")
    
    # Gráficos
    st.subheader("Distribuição Aprovados x Reprovados")
    st.bar_chart(df_editado["Status"].value_counts())
    
    st.subheader("Média por Aluno")
    st.bar_chart(df_editado.set_index("Aluno")["Média"])

# =============================
# CONTROLE
# =============================
if not st.session_state.logado:
    tela_login()
else:
    tela_sistema()
