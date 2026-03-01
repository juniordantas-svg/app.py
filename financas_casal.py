import streamlit as st
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from supabase import create_client
import pandas as pd
import plotly.express as px
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# =========================
# CONFIGURAÇÃO DE PÁGINA
# =========================
st.set_page_config(page_title="💜 Finanças Casal JR & VIC", layout="wide", page_icon="💜")

# =========================
# USUÁRIOS
# =========================
USERS = {"junior": "9391", "victoria": "1612"}

# =========================
# SUPABASE
# =========================
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# =========================
# LOGIN NUBANK MODERNO
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False

if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

def login_screen():
    st.markdown("""
    <style>
    body {background: linear-gradient(135deg, #6a0dad, #9b30ff);}
    .login-container {display:flex; justify-content:center; align-items:center; height:100vh;}
    .login-box {background-color:white; padding:40px 35px; border-radius:20px; box-shadow:0 12px 30px rgba(0,0,0,0.25); max-width:380px; width:100%; text-align:center;}
    .login-box h1 {color:#6a0dad; margin-bottom:25px; font-weight:700; font-size:30px;}
    .stTextInput>div>div>input {height:42px; font-size:16px; border-radius:10px; border:1px solid #ccc; padding:0 12px;}
    div.stButton>button {background-color:#6a0dad; color:white; width:100%; height:45px; font-size:16px; border-radius:10px; border:none; margin-top:20px; transition:0.3s;}
    div.stButton>button:hover {background-color:#5b00b0; cursor:pointer;}
    </style>
    <div class="login-container"><div class="login-box">
    <h1>💜 Finanças Casal JR & VIC</h1>
    """, unsafe_allow_html=True)

    with st.form(key="login_form"):
        user = st.text_input("Usuário", placeholder="Digite seu usuário")
        pwd = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        submit = st.form_submit_button("Entrar")

        if submit or st.session_state.login_attempted:
            st.session_state.login_attempted = True
            if USERS.get(user.lower()) == pwd:
                st.session_state.logged = True
            else:
                st.error("Usuário ou senha inválidos")
                st.session_state.login_attempted = False

    st.markdown("</div></div>", unsafe_allow_html=True)

if not st.session_state.logged:
    login_screen()
    st.stop()

# =========================
# FUNÇÕES DE BANCO
# =========================
def inserir_parcelas(descricao, valor_total, parcelas, data_compra, categoria):
    valor_parcela = round(valor_total / parcelas, 2)
    for i in range(parcelas):
        venc = data_compra + relativedelta(months=i)
        supabase.table("expenses").insert({
            "descricao": descricao,
            "valor_parcela": valor_parcela,
            "total_parcelas": parcelas,
            "parcela_atual": i+1,
            "data_vencimento": venc,
            "pago": False,
            "categoria": categoria
        }).execute()

def carregar_dados():
    res = supabase.table("expenses").select("*").order("data_vencimento").execute()
    if hasattr(res, "error") and res.error:
        st.error("Erro ao carregar dados")
        return pd.DataFrame()
    df = pd.DataFrame(res.data)
    if not df.empty:
        df["data_vencimento"] = pd.to_datetime(df["data_vencimento"])
    return df

def marcar_pago(id, status):
    if status:
        supabase.table("expenses").update({"pago": True,"data_pagamento": datetime.now()}).eq("id", id).execute()
    else:
        supabase.table("expenses").update({"pago": False,"data_pagamento": None}).eq("id", id).execute()

def excluir(id):
    supabase.table("expenses").delete().eq("id", id).execute()

# =========================
# NOVA COMPRA
# =========================
st.subheader("➕ Nova Compra")
c1, c2, c3, c4 = st.columns(4)
descricao = c1.text_input("Descrição")
valor_total = c2.number_input("Valor total", min_value=0.0, format="%.2f")
parcelas = c3.number_input("Parcelas", min_value=1, max_value=24, step=1)
categoria = c4.text_input("Categoria")
data_compra = st.date_input("Mês da compra", value=date.today())

if st.button("Salvar compra", use_container_width=True):
    if descricao and valor_total > 0 and categoria:
        inserir_parcelas(descricao, valor_total, parcelas, data_compra, categoria)
        st.success("Compra cadastrada!")
        st.experimental_rerun()

# =========================
# CARREGAR DADOS E FILTROS
# =========================
df = carregar_dados()
if df.empty:
    st.info("Nenhum registro encontrado")
    st.stop()

anos = df["data_vencimento"].dt.year.sort_values().unique().tolist()
anos_sel = st.multiselect("Ano", anos, default=anos)
categorias = df["categoria"].unique().tolist()
categorias_sel = st.multiselect("Categoria", categorias, default=categorias)
df_filtrado = df[df["data_vencimento"].dt.year.isin(anos_sel) & df["categoria"].isin(categorias_sel)]

# =========================
# KPIs ESTILO NUBANK
# =========================
total = df_filtrado["valor_parcela"].sum()
pago = df_filtrado[df_filtrado["pago"] == True]["valor_parcela"].sum()
restante = total - pago
st.markdown("### 💜 Resumo Financeiro")
k1, k2, k3 = st.columns(3)
k1.metric("💰 Total", f"R$ {total:,.2f}")
k2.metric("✅ Pago", f"R$ {pago:,.2f}")
k3.metric("⏳ Restante", f"R$ {restante:,.2f}")

# =========================
# GRÁFICOS
# =========================
st.markdown("### 📊 Despesas por Categoria / Mês")
df_filtrado["mes"] = df_filtrado["data_vencimento"].dt.to_period("M")
grafico_mes = df_filtrado.groupby(["mes","categoria"])["valor_parcela"].sum().reset_index()
fig_mes = px.bar(grafico_mes, x="mes", y="valor_parcela", color="categoria",
                 title="Despesas por categoria / mês", labels={"mes":"Mês","valor_parcela":"Valor (R$)","categoria":"Categoria"},
                 text_auto=True, template="plotly_white")
st.plotly_chart(fig_mes, use_container_width=True)

st.markdown("### 📈 Resumo Anual")
df_anual = df_filtrado.groupby([df_filtrado["data_vencimento"].dt.year,"categoria"])["valor_parcela"].sum().reset_index()
df_anual.rename(columns={"data_vencimento":"Ano","valor_parcela":"Total"}, inplace=True)
fig_anual = px.bar(df_anual, x="Ano", y="Total", color="categoria",
                   title="Resumo anual de despesas por categoria", text_auto=True, template="plotly_white")
st.plotly_chart(fig_anual, use_container_width=True)

st.markdown("### 📊 Distribuição de Gastos por Categoria")
df_pizza = df_filtrado.groupby("categoria")["valor_parcela"].sum().reset_index()
fig_pizza = px.pie(df_pizza, names="categoria", values="valor_parcela", title="Percentual de Gastos por Categoria", hole=0.4)
st.plotly_chart(fig_pizza, use_container_width=True)

# =========================
# TABELA DETALHADA
# =========================
st.subheader("📋 Despesas detalhadas")
for _, row in df_filtrado.iterrows():
    c1,c2,c3,c4,c5 = st.columns([3,1,1,1,1])
    c1.write(f"{row['descricao']} ({row['categoria']})")
    c2.write(f"{int(row['parcela_atual'])}ª de {int(row['total_parcelas'])}x")
    c3.write(f"R$ {row['valor_parcela']:,.2f}")

    pago_check = c4.checkbox("Pago", value=row["pago"], key=f"pg_{row['id']}")
    if pago_check != row["pago"]:
        marcar_pago(row["id"], pago_check)
        st.experimental_rerun()

    if c5.button("🗑️", key=f"del_{row['id']}"):
        excluir(row["id"])
        st.experimental_rerun()

# =========================
# PDF ESTILIZADO
# =========================
st.divider()
def gerar_pdf(df_pdf):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = [Paragraph("💜 Finanças Casal JR & VIC", styles["Title"]),
                Paragraph(f"Gerado em: {datetime.now()}", styles["Normal"]), Spacer(1,12)]
    tabela = [["Descrição","Categoria","Parcela","Valor","Pago"]]
    for _, r in df_pdf.iterrows():
        tabela.append([r["descricao"], r["categoria"], f"{int(r['parcela_atual'])}/{int(r['total_parcelas'])}",
                        f"R$ {r['valor_parcela']:,.2f}","Sim" if r["pago"] else "Não"])
    table = Table(tabela)
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.purple),
                               ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                               ("ALIGN",(0,0),(-1,-1),"CENTER"),
                               ("GRID",(0,0),(-1,-1),0.25,colors.black)]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_file = gerar_pdf(df_filtrado)
st.download_button("📥 Baixar relatório completo (PDF)", pdf_file,
                   file_name=f"financas_{datetime.now().strftime('%Y%m%d')}.pdf",
                   mime="application/pdf", use_container_width=True)
