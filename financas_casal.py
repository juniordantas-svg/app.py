import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import os
import io
import time

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ================= CONFIG =================
st.set_page_config(page_title="💑 Finanças Casal JR & VIC", layout="wide")

USERS = {"junior": "9391", "victoria": "1612"}
DATA_FILE = "dados_financas.csv"

COLS = [
    "ID","Usuario","Descricao","Data","Valor Parcela","Valor Total",
    "Parcela","Total Parcelas","Pago","Data Pagamento"
]

# ================= CSS GLOBAL =================
st.markdown("""
<style>
.big-title{
text-align:center;
font-size:42px;
font-weight:800;
background:linear-gradient(90deg,#8a2be2,#00c6ff);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;
}

.login-container{
height:85vh;
display:flex;
justify-content:center;
align-items:center;
}

.login-box{
width:380px;
padding:40px;
border-radius:22px;
background:rgba(20,20,30,0.90);
backdrop-filter:blur(14px);
box-shadow:0 20px 60px rgba(0,0,0,0.45);
}
</style>
""", unsafe_allow_html=True)

# ================= BANCO =================
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        for c in COLS:
            if c not in df.columns:
                df[c] = None
        return df[COLS]
    return pd.DataFrame(columns=COLS)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# ================= SESSION =================
if "logged" not in st.session_state:
    st.session_state.logged = False
if "user" not in st.session_state:
    st.session_state.user = None
if "tentativas" not in st.session_state:
    st.session_state.tentativas = 0
if "bloqueado_ate" not in st.session_state:
    st.session_state.bloqueado_ate = None

# ================= LOGIN PREMIUM =================
def login():

    # 🔒 bloqueio
    if st.session_state.bloqueado_ate:
        if datetime.now() < st.session_state.bloqueado_ate:
            st.error("🔒 Muitas tentativas. Aguarde 30 segundos.")
            st.stop()
        else:
            st.session_state.tentativas = 0
            st.session_state.bloqueado_ate = None

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="big-title">💑 Finanças Casal</div>', unsafe_allow_html=True)

    lembrar = st.checkbox("Lembrar usuário")

    with st.form("login_form"):

        user = st.text_input("Usuário", key="login_user")
        pwd = st.text_input("Senha", type="password", key="login_pwd")

        submitted = st.form_submit_button("Entrar")

        if submitted:
            u = user.lower().strip()

            if u in USERS and USERS[u] == pwd:

                # loading premium
                with st.spinner("🔐 Entrando..."):
                    time.sleep(1)

                st.session_state.logged = True
                st.session_state.user = u
                st.session_state.tentativas = 0
                st.rerun()

            else:
                st.session_state.tentativas += 1
                st.error("Usuário ou senha inválidos")

                if st.session_state.tentativas >= 3:
                    st.session_state.bloqueado_ate = datetime.now() + pd.Timedelta(seconds=30)
                    st.error("🔒 Acesso bloqueado por 30s")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 🔥 ENTER FLOW + AUTOFOCUS
    st.components.v1.html(
        """
        <script>
        const inputs = window.parent.document.querySelectorAll('input');
        if (inputs.length >= 2){
            inputs[0].focus();
            inputs[0].addEventListener("keydown", function(e){
                if(e.key==="Enter"){
                    e.preventDefault();
                    inputs[1].focus();
                }
            });
        }
        </script>
        """,
        height=0,
    )

# ================= CHAMA LOGIN =================
if not st.session_state.logged:
    login()
    st.stop()

# ================= HEADER =================
st.markdown('<div class="big-title">💑 Finanças Casal JR & VIC</div>', unsafe_allow_html=True)

df_user = df[df["Usuario"] == st.session_state.user]

# ================= NOVA COMPRA =================
st.subheader("➕ Nova Compra")

c1,c2,c3 = st.columns(3)
desc = c1.text_input("Descrição")
valor_total = c2.number_input("Valor total da compra", min_value=0.0, format="%.2f")
parcelas = c3.number_input("Parcelas", 1, 24, 1)
data_compra = st.date_input("Mês da compra", datetime.today())

if st.button("Salvar compra"):
    if desc and valor_total > 0:
        valor_parcela = valor_total / parcelas
        novos = []

        for i in range(parcelas):
            data_parcela = data_compra + relativedelta(months=i)
            novos.append({
                "ID": datetime.now().timestamp()+i,
                "Usuario": st.session_state.user,
                "Descricao": desc,
                "Data": data_parcela.strftime("%Y-%m"),
                "Valor Parcela": round(valor_parcela,2),
                "Valor Total": valor_total,
                "Parcela": i+1,
                "Total Parcelas": parcelas,
                "Pago": False,
                "Data Pagamento": ""
            })

        df = pd.concat([df,pd.DataFrame(novos)], ignore_index=True)
        save_data(df)
        st.success("Compra salva!")
        st.rerun()

# ================= FILTRO =================
st.subheader("📅 Filtro mensal")
mes = st.text_input("Mês (YYYY-MM)", datetime.today().strftime("%Y-%m"))
df_mes = df_user[df_user["Data"] == mes]

# ================= DASHBOARD =================
total = df_mes["Valor Parcela"].sum()
pago = df_mes[df_mes["Pago"]==True]["Valor Parcela"].sum()
restante = total - pago

m1,m2,m3 = st.columns(3)
m1.metric("💰 Total", f"R$ {total:,.2f}")
m2.metric("✅ Pago", f"R$ {pago:,.2f}")
m3.metric("⏳ Restante", f"R$ {restante:,.2f}")

# ================= LISTA =================
st.subheader("📋 Despesas do mês")

for idx,row in df_mes.iterrows():
    cols = st.columns([3,2,2,1,1])

    cols[0].write(row["Descricao"])
    cols[1].write(f"R$ {row['Valor Parcela']:,.2f}")
    cols[2].write(f"{int(row['Parcela'])}ª de {int(row['Total Parcelas'])}x")

    pago_chk = cols[3].checkbox("Pago", bool(row["Pago"]), key=f"pg_{idx}")

    if pago_chk != row["Pago"]:
        df.loc[idx,"Pago"] = pago_chk
        df.loc[idx,"Data Pagamento"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        save_data(df)
        st.rerun()

    if cols[4].button("🗑️", key=f"del_{idx}"):
        df = df.drop(idx)
        save_data(df)
        st.rerun()

# ================= GRÁFICO =================
if not df_mes.empty:
    graf = df_mes.groupby("Descricao")["Valor Parcela"].sum().reset_index()
    fig = px.pie(graf, names="Descricao", values="Valor Parcela")
    st.plotly_chart(fig, use_container_width=True)

# ================= PDF =================
st.subheader("📄 Relatório")

if st.button("Baixar PDF"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elems = [
        Paragraph("Finanças Casal JR & VIC", styles["Title"]),
        Paragraph(f"Mês: {mes}", styles["Normal"]),
        Paragraph(f"Gerado em: {datetime.now()}", styles["Normal"]),
        Spacer(1,12)
    ]

    dados = [["Descrição","Valor","Parcela","Pago"]]
    for _,r in df_mes.iterrows():
        dados.append([
            r["Descricao"],
            f"R$ {r['Valor Parcela']:.2f}",
            f"{int(r['Parcela'])}/{int(r['Total Parcelas'])}",
            "Sim" if r["Pago"] else "Não"
        ])

    tabela = Table(dados)
    tabela.setStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.grey),
        ('GRID',(0,0),(-1,-1),0.5,colors.black)
    ])

    elems.append(tabela)
    doc.build(elems)

    st.download_button(
        "⬇️ Download",
        data=buffer.getvalue(),
        file_name=f"Relatorio_{mes}.pdf",
        mime="application/pdf"
    )
