import streamlit as st
import pandas as pd
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
from dateutil.relativedelta import relativedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="💑 Finanças Casal JR & VIC", layout="wide")

USERS = {
    "junior": "9391",
    "victoria": "1612"
}

# =========================
# DB CONNECTION (ROBUSTA)
# =========================
@st.cache_resource
def get_conn():
    try:
        conn = psycopg2.connect(
            st.secrets["DATABASE_URL"],
            cursor_factory=RealDictCursor,
            sslmode="require",
            connect_timeout=10
        )
        return conn
    except Exception as e:
        st.error("❌ Erro ao conectar no banco de dados.")
        st.exception(e)
        st.stop()

def init_db():
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            descricao TEXT,
            valor_parcela NUMERIC,
            total_parcelas INTEGER,
            parcela_atual INTEGER,
            data_vencimento DATE,
            pago BOOLEAN DEFAULT FALSE,
            data_pagamento TIMESTAMP
        )
        """)

        conn.commit()
        cur.close()

    except Exception as e:
        st.error("❌ Falha ao inicializar banco.")
        st.exception(e)
        st.stop()

init_db()

# =========================
# LOGIN PREMIUM
# =========================
if "logged" not in st.session_state:
    st.session_state.logged = False

def login_screen():
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.markdown("## 💑 Finanças Casal JR & VIC")

        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")

        if user and pwd:
            if USERS.get(user.lower()) == pwd:
                st.session_state.logged = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

if not st.session_state.logged:
    login_screen()
    st.stop()

# =========================
# FUNÇÕES DB (SEGURAS)
# =========================
def inserir_parcelas(descricao, valor_total, parcelas, data_compra):
    conn = get_conn()
    cur = conn.cursor()

    try:
        valor_parcela = round(valor_total / parcelas, 2)

        for i in range(parcelas):
            venc = data_compra + relativedelta(months=i)
            cur.execute("""
                INSERT INTO expenses
                (descricao, valor_parcela, total_parcelas, parcela_atual, data_vencimento)
                VALUES (%s,%s,%s,%s,%s)
            """, (descricao, valor_parcela, parcelas, i+1, venc))

        conn.commit()

    except Exception as e:
        st.error("Erro ao inserir parcelas")
        st.exception(e)

    finally:
        cur.close()

def carregar_dados():
    conn = get_conn()
    try:
        df = pd.read_sql("SELECT * FROM expenses ORDER BY data_vencimento", conn)
        return df
    except Exception as e:
        st.error("Erro ao carregar dados")
        st.exception(e)
        return pd.DataFrame()

def marcar_pago(id, status):
    conn = get_conn()
    cur = conn.cursor()

    try:
        if status:
            cur.execute("""
                UPDATE expenses
                SET pago = TRUE,
                    data_pagamento = NOW()
                WHERE id=%s
            """, (id,))
        else:
            cur.execute("""
                UPDATE expenses
                SET pago = FALSE,
                    data_pagamento = NULL
                WHERE id=%s
            """, (id,))

        conn.commit()
    finally:
        cur.close()

def excluir(id):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM expenses WHERE id=%s", (id,))
        conn.commit()
    finally:
        cur.close()

# =========================
# HEADER
# =========================
st.title("💑 Finanças Casal JR & VIC")

# =========================
# NOVA COMPRA
# =========================
st.subheader("➕ Nova Compra")

c1, c2, c3 = st.columns(3)

descricao = c1.text_input("Descrição")
valor_total = c2.number_input("Valor total da compra", min_value=0.0, format="%.2f")
parcelas = c3.number_input("Parcelas", min_value=1, max_value=24, step=1)

data_compra = st.date_input("Mês da compra", value=date.today())

if st.button("Salvar compra", use_container_width=True):
    if descricao and valor_total > 0:
        inserir_parcelas(descricao, valor_total, parcelas, data_compra)
        st.success("Compra cadastrada!")
        st.rerun()

# =========================
# FILTRO MENSAL
# =========================
st.subheader("📅 Filtro mensal")

df = carregar_dados()

meses = df["data_vencimento"].dt.strftime("%Y-%m").unique().tolist() if not df.empty else []
mes_sel = st.selectbox("Selecione o mês", meses)

if mes_sel:
    df_mes = df[df["data_vencimento"].dt.strftime("%Y-%m") == mes_sel]
else:
    df_mes = df

# =========================
# KPIs
# =========================
total = df_mes["valor_parcela"].sum() if not df_mes.empty else 0
pago = df_mes[df_mes["pago"] == True]["valor_parcela"].sum() if not df_mes.empty else 0
restante = total - pago

k1, k2, k3 = st.columns(3)
k1.metric("💰 Total", f"R$ {total:,.2f}")
k2.metric("✅ Pago", f"R$ {pago:,.2f}")
k3.metric("⏳ Restante", f"R$ {restante:,.2f}")

# =========================
# TABELA
# =========================
st.subheader("📋 Despesas do mês")

for _, row in df_mes.iterrows():
    c1, c2, c3, c4, c5 = st.columns([3,1,1,1,1])

    c1.write(row["descricao"])
    c2.write(f"{int(row['parcela_atual'])}ª de {int(row['total_parcelas'])}x")
    c3.write(f"R$ {row['valor_parcela']:,.2f}")

    pago_check = c4.checkbox(
        "Pago",
        value=row["pago"],
        key=f"pg_{row['id']}"
    )
    if pago_check != row["pago"]:
        marcar_pago(row["id"], pago_check)
        st.rerun()

    if c5.button("🗑️", key=f"del_{row['id']}"):
        excluir(row["id"])
        st.rerun()

# =========================
# PDF
# =========================
st.divider()

def gerar_pdf(df_pdf, mes):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("Finanças Casal JR e VIC", styles["Title"]))
    elements.append(Paragraph(f"Mês: {mes}", styles["Normal"]))
    elements.append(Paragraph(f"Gerado em: {datetime.now()}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    tabela = [["Descrição", "Parcela", "Valor", "Pago"]]

    for _, r in df_pdf.iterrows():
        tabela.append([
            r["descricao"],
            f"{int(r['parcela_atual'])}/{int(r['total_parcelas'])}",
            f"R$ {r['valor_parcela']:,.2f}",
            "Sim" if r["pago"] else "Não"
        ])

    table = Table(tabela)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.purple),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.25,colors.black),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer

if not df_mes.empty:
    pdf_file = gerar_pdf(df_mes, mes_sel)
    st.download_button(
        "📥 Baixar relatório mensal (PDF)",
        pdf_file,
        file_name=f"financas_{mes_sel}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
