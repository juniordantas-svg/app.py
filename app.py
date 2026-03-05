import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Portal Universitas", layout="centered")

if "logado" not in st.session_state:
    st.session_state.logado = False

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

def tela_sistema():
    st.title("📚 Cadeia de Custódia - Sistema de Notas")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Sair"):
            st.session_state.logado = False
            st.rerun()

    st.markdown("---")
    df_alunos = gerar_alunos()
    st.subheader("📊 Notas dos Alunos")
    st.dataframe(df_alunos, use_container_width=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Alunos", len(df_alunos))
    with col2:
        aprovados = len(df_alunos[df_alunos["Status"] == "Aprovado"])
        st.metric("Aprovados", aprovados)
    with col3:
        reprovados = len(df_alunos[df_alunos["Status"] == "Reprovado"])
        st.metric("Reprovados", reprovados)

def tela_login():
    st.markdown("""
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .block-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 2rem;
        }
        .stTextInput > div > div > input {
            border-radius: 8px;
            padding: 12px 16px;
            border: 1px solid #ddd;
            font-size: 14px;
        }
        .stTextInput > label {
            font-weight: 600;
            color: #555;
            font-size: 14px;
        }
        .stSelectbox > label {
            font-weight: 600;
            color: #555;
            font-size: 14px;
        }
        .stButton > button {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            background: #0d6efd;
            color: white;
            font-size: 16px;
            font-weight: 600;
            border: none;
            margin-top: 10px;
        }
        .stButton > button:hover {
            background: #0b5ed7;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div style="background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); margin-top: 50px;">', unsafe_allow_html=True)
        
        st.markdown('<h2 style="text-align: center; color: #333; margin-bottom: 10px;">Portal Universitas</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666; font-size: 14px; margin-bottom: 30px;">Acesso exclusivo para alunos, professores e coordenadores</p>', unsafe_allow_html=True)

        with st.form("login_form"):
            portal = st.selectbox(
                "Portal",
                ["Portal da Graduação", "Portal da Pós-Graduação", "Portal Biblioteca", "Portal Extensão"]
            )

            perfil = st.selectbox(
                "Perfil",
                ["Aluno", "Egresso", "Professor"]
            )

            col_mat, col_senha = st.columns(2)
            
            with col_mat:
                matricula = st.text_input("Matrícula", placeholder="Informe a matrícula")
            
            with col_senha:
                senha = st.text_input("Senha", type="password", placeholder="Informe a senha")

            lembrar = st.checkbox("Lembrar-me", value=True)
            submit = st.form_submit_button("Entrar")

            if submit:
                if matricula == "dantas" and senha == "1234":
                    st.session_state.logado = True
                    st.success("✅ Login realizado com sucesso!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Matrícula ou senha inválidos")

        st.markdown('<p style="text-align: center; color: #666; font-size: 13px; margin-top: 20px;">Deseja trocar a senha? <a href="#" style="color: #0d6efd;">Trocar senha</a></p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<p style="text-align: center; color: white; font-size: 12px; margin-top: 30px;">© 2026. Todos os direitos reservados. Portal Universitas</p>', unsafe_allow_html=True)

if not st.session_state.logado:
    tela_login()
else:
    tela_sistema()
