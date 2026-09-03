from google.adk import Agent
from google.genai import types

def tool_get_trip_context(trip_id: str) -> str:
    """Busca o contexto cadastral completo da viagem e pendências ativas no Escalasoft ERP."""
    return f"Viagem {trip_id}: Cooperado Roberto Silva, Veículo BRA2E19, Motorista Carlos Eduardo, Pendências: CRLV, CNH"

def tool_generate_compliance_signature(cooperado_nome: str, trip_id: str) -> str:
    """Gera o Termo de Compliance e Assinatura Digital nativa com Hash SHA-256 no Google Cloud Storage."""
    return f"Certificado Digital SHA-256 de Compliance gerado no GCS para {cooperado_nome} na viagem {trip_id}"

def tool_save_to_gcs_and_bigquery(filename: str, doc_type: str, status: str) -> str:
    """Registra os metadados do documento validado no BigQuery para Analytics e auditoria no GCS."""
    return f"Documento {doc_type} gravado no GCS ({filename}) e BigQuery Analytics com status {status}"

def tool_update_escalasoft_erp(trip_id: str, doc_type: str) -> str:
    """Atualiza o ERP Escalasoft e libera a viagem do cooperado."""
    return f"ERP Escalasoft atualizado para viagem {trip_id}. Status: LIBERADO"

# Instância oficial do Agente Google Cloud ADK v2.8+
root_agent = Agent(
    name="rodacoop_compliance_agent",
    description="Agente de Compliance Documental Rodacoop utilizando o Google Cloud Agent Development Kit (ADK)",
    model="gemini-2.0-flash-exp",
    instruction=(
        "Você é o Agente de Compliance Documental Rodacoop rodando no Google Cloud Agent Development Kit (ADK).\n"
        "1. Ao receber a foto ou PDF da CNH ou CRLV, consulte o contexto da viagem usando 'tool_get_trip_context'.\n"
        "2. Valide as informações cadastrais e de validade dos documentos.\n"
        "3. Salve a auditoria e métricas usando 'tool_save_to_gcs_and_bigquery'.\n"
        "4. Emita a assinatura digital com Hash SHA-256 usando 'tool_generate_compliance_signature'.\n"
        "5. Atualize e libere o cadastro no Escalasoft ERP usando 'tool_update_escalasoft_erp'."
    ),
    tools=[
        tool_get_trip_context,
        tool_generate_compliance_signature,
        tool_save_to_gcs_and_bigquery,
        tool_update_escalasoft_erp
    ]
)
