import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Finanças JR e VIC", layout="wide")

# ---------------- LOGIN ----------------
USERS = {"Junior": "9391", "Victoria": "1612"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    st.markdown(
        """
        <style>
        .login-box {
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            padding: 40px;
            border-radius: 25px;
            width: 420px;
            margin: auto;
            margin-top: 80px;
            text-align: center;
            color: white;
            box-shadow: 0px 10px 35px rgba(0,0,0,0.4);
            font-family: 'Arial', sans-serif;
        }
        .login-box h2 {
            margin-bottom: 30px;
            font-family: 'Arial Black', sans-serif;
        }
        .stTextInput>div>div>input {
            height: 45px;
            border-radius: 12px;
            border: none;
            padding-left: 12px;
            font-size: 16px;
        }
        .stButton>button {
            background-color: #ffdd59;
            color: #333;
            font-weight: bold;
            height: 50px;
            width: 100%;
            border-radius: 15px;
            border: none;
            font-size: 18px;
            cursor: pointer;
            margin-top: 10px;
        }
        </style>
        <div class="login-box">
            <h2>💑 Finanças JR e VIC</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Usuário", placeholder="Digite seu usuário")
        password = st.text_input("Senha", placeholder="Digite sua senha", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos")

# ---------------- APP PRINCIPAL ----------------
else:
    st.sidebar.success(f"Logado como: {st.session_state.user}")

    if "despesas" not in st.session_state:
        st.session_state.despesas = pd.DataFrame(
            columns=["ID", "Nome", "Valor", "Data", "Parcelas", "Status", "Parcelas_restantes"]
        )

    def gerar_id():
        return len(st.session_state.despesas) + 1

    # ---------------- CADASTRO DE DESPESA ----------------
    st.markdown("<h2 style='color:#2575fc;'>📝 Cadastrar Despesa</h2>", unsafe_allow_html=True)
    with st.form("cadastro"):
        nome = st.text_input("Nome da despesa", placeholder="Ex: Conta de luz")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        data = st.date_input("Data de cadastro", datetime.today())
        parcelas = st.selectbox("Parcelas", ["1","2","3","4","5","10","24"])
        submit = st.form_submit_button("Cadastrar", help="Clique para cadastrar a despesa")
        if submit:
            id_novo = gerar_id()
            st.session_state.despesas = pd.concat([
                st.session_state.despesas,
                pd.DataFrame([{
                    "ID": id_novo,
                    "Nome": nome,
                    "Valor": valor,
                    "Data": data,
                    "Parcelas": int(parcelas),
                    "Status": "Pendente",
                    "Parcelas_restantes": int(parcelas)
                }])
            ], ignore_index=True)
            st.success("Despesa cadastrada!")

    # ---------------- PARCELAS AUTOMÁTICAS ----------------
    if not st.session_state.despesas.empty:
        df = st.session_state.despesas
        novas_linhas = []
        for idx, row in df.iterrows():
            if row["Parcelas_restantes"] > 1:
                data_atual = pd.Timestamp(row["Data"])
                proximo_mes = data_atual + pd.DateOffset(months=1)
                existe = ((df["Nome"] == row["Nome"]) &
                          (pd.to_datetime(df["Data"]).dt.month == proximo_mes.month) &
                          (pd.to_datetime(df["Data"]).dt.year == proximo_mes.year)).any()
                if not existe:
                    novas_linhas.append({
                        "ID": len(df) + len(novas_linhas) + 1,
                        "Nome": row["Nome"],
                        "Valor": row["Valor"],
                        "Data": proximo_mes,
                        "Parcelas": row["Parcelas"],
                        "Status": "Pendente",
                        "Parcelas_restantes": row["Parcelas_restantes"]-1
                    })
        if novas_linhas:
            st.session_state.despesas = pd.concat([df, pd.DataFrame(novas_linhas)], ignore_index=True)

    # ---------------- DASHBOARD PREMIUM ----------------
    st.markdown("<h2 style='color:#2575fc;'>📈 Dashboard Executivo</h2>", unsafe_allow_html=True)
    despesas = st.session_state.despesas.copy()
    despesas = despesas.sort_values(by="Data", ascending=True)

    # Cards de resumo
    if not despesas.empty:
        filtro_mes = st.selectbox("Filtrar mês", options=sorted(despesas["Data"].dt.strftime("%Y-%m").unique()))
        filtro_status = st.selectbox("Filtrar status", options=["Todos","Pendente","Pago"])
        df_dash = despesas.copy()
        if filtro_status != "Todos":
            df_dash = df_dash[df_dash["Status"] == filtro_status]
        df_dash = df_dash[df_dash["Data"].dt.strftime("%Y-%m") == filtro_mes]

        total = df_dash["Valor"].sum()
        pago = df_dash[df_dash["Status"]=="Pago"]["Valor"].sum()
        pendente = total - pago

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total", f"R${total:.2f}", delta_color="off")
        col2.metric("✅ Pago", f"R${pago:.2f}", delta_color="normal")
        col3.metric("⏳ Pendente", f"R${pendente:.2f}", delta_color="inverse")

        # Gráfico Pizza
        fig_pizza = px.pie(values=[pago, pendente], names=["Pago","Pendente"],
                           color_discrete_map={"Pago":"green","Pendente":"red"})
        fig_pizza.update_layout(title_text="Distribuição de Pagamentos", title_x=0.5)
        st.plotly_chart(fig_pizza, use_container_width=True)

        # Gráfico Barra
        fig_bar = px.bar(df_dash, x=df_dash["Data"].dt.strftime("%d/%m/%Y"), y="Valor",
                         color="Status", barmode="group", text="Valor",
                         color_discrete_map={"Pago":"green","Pendente":"red"})
        fig_bar.update_layout(title_text="Despesas por Dia", title_x=0.5)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------- TABELA DE DESPESAS PREMIUM ----------------
    st.markdown("<h2 style='color:#2575fc;'>📊 Despesas</h2>", unsafe_allow_html=True)
    for i, row in despesas.iterrows():
        bg_color = "#d4edda" if row["Status"]=="Pago" else "#f8d7da"
        cols = st.columns([3,1,1,1,1,1])
        info = f"{row['Nome']} - R${row['Valor']:.2f} - {row['Data'].strftime('%d/%m/%Y')} - {row['Parcelas']}x"
        cols[0].markdown(f"<div style='padding:8px; background-color:{bg_color}; border-radius:8px'>{info}</div>", unsafe_allow_html=True)
        if cols[1].button("💚 Pagar", key=f"pagar_{i}"):
            st.session_state.despesas.at[i, "Status"] = "Pago"
        if cols[2].button("✏️ Editar", key=f"editar_{i}"):
            novo_nome = st.text_input("Novo nome", value=row["Nome"], key=f"edit_nome_{i}")
            novo_valor = st.number_input("Novo valor", value=row["Valor"], key=f"edit_valor_{i}")
            if st.button("Salvar", key=f"salvar_{i}"):
                st.session_state.despesas.at[i, "Nome"] = novo_nome
                st.session_state.despesas.at[i, "Valor"] = novo_valor
                st.success("Despesa atualizada")
        if cols[3].button("❌ Excluir", key=f"excluir_{i}"):
            st.session_state.despesas = st.session_state.despesas.drop(i)
            st.experimental_rerun()
        cols[4].markdown(f"<div style='color:#00cc66;font-weight:bold'>{row['Status']}</div>", unsafe_allow_html=True)
        cols[5].markdown(f"<div style='color:#ff4d4d'>{row['Parcelas_restantes']} restantes</div>", unsafe_allow_html=True)

    # ---------------- EXPORTAR CSV ----------------
    if not despesas.empty:
        st.markdown("<h3 style='color:#2575fc;'>📄 Exportar relatório</h3>", unsafe_allow_html=True)
        csv = df_dash.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name=f"relatorio_{filtro_mes}.csv", mime="text/csv")
