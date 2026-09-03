import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from google.cloud import bigquery

st.set_page_config(
    page_title="Rodacoop | Control Tower & Analytics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Personalizada CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3b82f6;
        color: white;
    }
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

st.title("🚚 Rodacoop — Control Tower & Compliance Analytics")
st.caption("Painel em Tempo Real de Onboarding e Validação Documental com Gemini Enterprise e BigQuery")

# MOCK DATA PARA DEMONSTRAÇÃO
mock_audit_data = [
    {"data": "2026-09-03 13:25:00", "viagem": "VG-2026-9941", "cooperado": "Roberto Silva", "tipo": "CRLV", "placa": "BRA2E19", "status": "APROVADO", "tempo_processamento_s": 1.4},
    {"data": "2026-09-03 12:10:12", "viagem": "VG-2026-9938", "cooperado": "Marcos Lima", "tipo": "CNH", "placa": "FXX4120", "status": "DIVERGENCIA_DADOS", "tempo_processamento_s": 1.8},
    {"data": "2026-09-03 11:45:00", "viagem": "VG-2026-9930", "cooperado": "Carlos Eduardo", "tipo": "CRLV", "placa": "GHY9822", "status": "APROVADO", "tempo_processamento_s": 1.2},
    {"data": "2026-09-03 10:05:43", "viagem": "VG-2026-9915", "cooperado": "Antônio Souza", "tipo": "ANTT", "placa": "JJL3301", "status": "ILEGIVEL", "tempo_processamento_s": 2.1},
    {"data": "2026-09-03 09:30:11", "viagem": "VG-2026-9902", "cooperado": "João Pedro Alcantara", "tipo": "CNH", "placa": "KKL1122", "status": "APROVADO", "tempo_processamento_s": 1.5}
]

df = pd.DataFrame(mock_audit_data)

# METRICAS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Documentos Auditados", len(df), "+100% hoje")
col2.metric("Taxa de Aprovação Gemini", f"{round((len(df[df['status'] == 'APROVADO'])/len(df))*100, 1)}%", "+5.2%")
col3.metric("Tempo Médio de Validação", f"{df['tempo_processamento_s'].mean():.2f}s", "-0.3s (SLA < 2s)")
col4.metric("Viagens Liberadas em Tempo Real", len(df[df['status'] == 'APROVADO']))

st.divider()

# GRAFICOS
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Distribuição dos Status de Validação")
    fig_status = px.pie(df, names="status", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_status.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_status, use_container_width=True)

with col_right:
    st.subheader("⏱️ SLA de Resposta Gemini 2.0 Flash (segundos)")
    fig_bar = px.bar(df, x="tipo", y="tempo_processamento_s", color="status", barmode="group")
    fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# TABELA DE LOGS EM TEMPO REAL
st.subheader("📋 Tabela de Auditoria e Logs do BigQuery Analytics")
st.dataframe(df, use_container_width=True)
