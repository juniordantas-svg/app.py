import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import bcrypt
import os
import io

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Finanças Casal JR & VIC",
    layout="wide",
    page_icon="💑"
)

DATA_FILE = "dados_financas.csv"

# =========================
# CSS PREMIUM
# =========================

st.markdown("""
<style>
.main-title {
    text-align:center;
    font-size:42px;
    font-weight:800;
    background: linear-gradient(90deg,#7c3aed,#06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.card {
    background: #111827;
    padding:20px;
    border-radius:16px;
    box-shadow:0 10px 25px rgba(0,0,0,0.4);
}

.status-pago {color:#10b981;font-weight:700;}
.status-vencer {color:#f59e0b;font-weight:700;}
.status-atrasado {color:#ef4444;font-weight:700;}
</style>
""", unsafe_allow_html=True)

# =========================
# USUÁRIOS COM HASH
# =========================

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

USERS = {
    "junior": hash_password("9391"),
    "victoria": hash_password("1612"),
}

# =========================
# DATA
# =========================

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Vencimento"] = pd.to_datetime(df["Vencimento"])
        df["Data Pagamento"] = pd.to_datetime(df["Data Pagamento"], errors="coerce")
        return df
    return pd.DataFrame(columns=[
        "Descrição","Vencimento","Valor Parcela",
        "Parcela Atual","Total Parcelas",
        "Pago","Data Pagamento"
    ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# =========================
# SESSION
# =========================

if "logged" not in st.session_state:
    st.session_state.logged = False

if "df" not in st.session_state:
    st.session_state.df = load_data()

# =========================
# LOGIN PREMIUM
# =========================

def login():

    st.markdown("<h1 class='main-title'>💑 Finanças Casal JR & VIC</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("### 🔐 Acesso seguro")

        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):

            user_key = username.lower()

            if user_key in USERS and check_password(password, USERS[user_key]):
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

if not st.session_state.logged:
    login()
    st.stop()

# =========================
# HEADER
# =========================

colA, colB = st.columns([6,1])
colA.markdown("<h1 class='main-title'>💑 Finanças Casal JR & VIC</h1>", unsafe_allow_html=True)

if colB.button("🚪 Logout"):
    st.session_state.logged = False
    st.rerun()

# =========================
# CADASTRO
# =========================

st.markdown("## ➕ Nova Despesa")

c1,c2,c3 = st.columns(3)
descricao = c1.text_input("Descrição")
vencimento = c2.date_input("Vencimento", value=date.today())
valor_total = c3.number_input("Valor total", min_value=0.0)

parcelas = st.selectbox("Parcelamento", ["Única"]+[f"{i}x" for i in range(2,25)])

if parcelas == "Única":
    total_parcelas = 1
else:
    total_parcelas = int(parcelas.replace("x",""))

parcela_atual = 1
if total_parcelas > 1:
    parcela_atual = st.number_input("Parcela atual",1,total_parcelas)

valor_parcela = valor_total / total_parcelas if total_parcelas else 0

if st.button("💾 Salvar despesa", use_container_width=True):

    nova = {
        "Descrição": descricao,
        "Vencimento": pd.to_datetime(vencimento),
        "Valor Parcela": valor_parcela,
        "Parcela Atual": parcela_atual,
        "Total Parcelas": total_parcelas,
        "Pago": False,
        "Data Pagamento": None
    }

    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([nova])],
        ignore_index=True
    )

    save_data(st.session_state.df)
    st.success("Despesa registrada!")
    st.rerun()

# =========================
# STATUS
# =========================

def status_conta(row):
    hoje = date.today()
    if row["Pago"]:
        return "Pago"
    elif row["Vencimento"].date() < hoje:
        return "Atrasado"
    return "A vencer"

# =========================
# LISTAGEM PREMIUM
# =========================

st.markdown("## 📋 Suas despesas")

df = st.session_state.df.copy()

for idx,row in df.iterrows():

    status = status_conta(row)

    if status=="Pago":
        css="status-pago"
    elif status=="Atrasado":
        css="status-atrasado"
    else:
        css="status-vencer"

    progresso = (row["Parcela Atual"]/row["Total Parcelas"])*100 if row["Total Parcelas"] else 100

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns([3,2,2,2])

        c1.write(f"**{row['Descrição']}**")
        c1.progress(progresso/100)

        c2.markdown(f"<span class='{css}'>{status}</span>", unsafe_allow_html=True)

        c3.write(f"{int(row['Parcela Atual'])}ª de {int(row['Total Parcelas'])}x")
        c3.write(f"R$ {row['Valor Parcela']:.2f}")

        pago_check = c4.checkbox("Pago", value=row["Pago"], key=f"pg{idx}")

        if pago_check and not row["Pago"]:
            st.session_state.df.at[idx,"Pago"]=True
            st.session_state.df.at[idx,"Data Pagamento"]=datetime.now()
            save_data(st.session_state.df)

        if c4.button("Excluir", key=f"del{idx}"):
            st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
            save_data(st.session_state.df)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# DASHBOARD PREMIUM
# =========================

st.markdown("## 📊 Dashboard Inteligente")

if not df.empty:

    df["Mes"] = df["Vencimento"].dt.to_period("M")
    mes = st.selectbox("Mês", sorted(df["Mes"].astype(str).unique()))
    df_mes = df[df["Mes"].astype(str)==mes]

    total = df_mes["Valor Parcela"].sum()
    pago = df_mes[df_mes["Pago"]==True]["Valor Parcela"].sum()
    restante = total - pago

    m1,m2,m3 = st.columns(3)
    m1.metric("💰 Total", f"R$ {total:,.2f}")
    m2.metric("✅ Pago", f"R$ {pago:,.2f}")
    m3.metric("⏳ Restante", f"R$ {restante:,.2f}")

    fig = px.pie(
        names=["Pago","Restante"],
        values=[pago,restante],
        title="Distribuição do mês"
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# PDF PREMIUM
# =========================

if not df.empty and st.button("📥 Baixar relatório premium"):

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Finanças Casal JR e VIC", styles["Title"]))
    elements.append(Paragraph(f"Mês: {mes}", styles["Normal"]))
    elements.append(Paragraph(f"Gerado em: {datetime.now()}", styles["Normal"]))
    elements.append(Spacer(1,12))

    data = [df_mes.columns.tolist()] + df_mes.astype(str).values.tolist()
    table = Table(data)
    table.setStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('GRID',(0,0),(-1,-1),0.5,colors.black)
    ])

    elements.append(table)
    doc.build(elements)

    st.download_button(
        "Download PDF",
        data=buffer.getvalue(),
        file_name=f"Financas_{mes}.pdf",
        mime="application/pdf"
    )
