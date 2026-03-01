import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Finanças do Casal", layout="wide")

# ---------------- LOGIN ----------------
USERS = {"Junior": "9391", "Victoria": "1612"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    st.markdown(
        """
        <div style="display:flex; justify-content:center; align-items:center; height:100vh;">
            <div style="background-color:#f0f2f6; padding:40px; border-radius:15px; text-align:center; width:350px; box-shadow: 0px 0px 10px rgba(0,0,0,0.2);">
            <h2>💑 Finanças do Casal</h2>
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Bem-vindo(a), {username}!")
        else:
            st.error("Usuário ou senha incorretos")
else:
    st.sidebar.success(f"Logado como: {st.session_state.user}")

    # ---------------- DESPESAS ----------------
    if "despesas" not in st.session_state:
        st.session_state.despesas = pd.DataFrame(
            columns=["ID", "Nome", "Valor", "Data", "Parcelas", "Status", "Parcelas_restantes"]
        )

    def gerar_id():
        return len(st.session_state.despesas) + 1

    st.markdown("## 📝 Cadastrar Despesa")
    with st.form("cadastro"):
        nome = st.text_input("Nome da despesa")
        valor = st.number_input("Valor", min_value=0.0, step=0.01)
        data = st.date_input("Data de cadastro", datetime.today())
        parcelas = st.selectbox("Parcelas", ["1","2","3","4","5","10","24"])
        submit = st.form_submit_button("Cadastrar")
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

    # ---------------- TABELA INTERATIVA ----------------
    st.markdown("## 📊 Despesas")
    despesas = st.session_state.despesas.copy()
    despesas = despesas.sort_values(by="Data", ascending=True)

    for i, row in despesas.iterrows():
        cols = st.columns([2,1,1,1,1,1])
        info = f"{row['Nome']} - R${row['Valor']:.2f} - {row['Data'].strftime('%d/%m/%Y')} - {row['Parcelas']}x"
        if row["Status"] == "Pago":
            info = f"✅ {info}"
        cols[0].write(info)
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
        cols[4].write(row["Status"])
        cols[5].write(f"{row['Parcelas_restantes']} restantes")

    # ---------------- DASHBOARD INTERATIVO ----------------
    st.markdown("## 📈 Dashboard")
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

        st.metric("Total", f"R${total:.2f}")
        st.metric("Pago", f"R${pago:.2f}")
        st.metric("Pendente", f"R${pendente:.2f}")

        # Gráfico pizza
        fig_pizza = px.pie(values=[pago, pendente], names=["Pago","Pendente"],
                           color_discrete_map={"Pago":"green","Pendente":"red"})
        st.plotly_chart(fig_pizza, use_container_width=True)

        # Gráfico de barras (Despesas por dia)
        fig_bar = px.bar(df_dash, x=df_dash["Data"].dt.strftime("%d/%m/%Y"), y="Valor",
                         color="Status", barmode="group")
        st.plotly_chart(fig_bar, use_container_width=True)

        # ---------------- EXPORTAÇÃO CSV ----------------
        st.markdown("## 📄 Exportar relatório")
        csv = df_dash.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name=f"relatorio_{filtro_mes}.csv", mime="text/csv")