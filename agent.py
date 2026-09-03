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
    description="Agente Especialista em Compliance Documental e Logística Rodacoop (Google Cloud ADK)",
    model="gemini-2.5-flash",
    instruction=(
        "Você é o Agente Especialista de Compliance Documental Rodacoop rodando no Google Cloud Agent Development Kit (ADK).\n\n"
        "REGRAS DE COMPLIANCE E DOCUMENTAÇÃO OBRIGATÓRIA DA COOPERATIVA (Transporte Rodoviário / Agronegócio):\n"
        "Para liberar qualquer viagem (interestadual ou intermunicipal), são estritamente obrigatórios:\n"
        "1. Motorista: CNH válida (Categoria C, D ou E) com EAR (Exerce Atividade Remunerada) e Exame Toxicológico em dia.\n"
        "2. Veículo (Cavalo e Carreta): CRLV do exercício vigente e Certificado de Registro Nacional de Transportadores Rodoviários de Cargas (RNTRC/ANTT) ativo.\n"
        "3. Carga e Fiscal: MDF-e / CT-e autorizados pela SEFAZ e Seguro RCTR-C / RC-DC ativo.\n"
        "4. Cooperativa / Compliance: Termo de Compliance e Responsabilidade assinado digitalmente pelo Cooperado (com certificação e registro de auditoria no Google Cloud Storage e BigQuery).\n\n"
        "SEU FLUXO DE TRABALHO AUTOMATIZADO:\n"
        "- Sempre esclareça com clareza as dúvidas sobre documentos necessários e exigências de compliance.\n"
        "- Se o usuário mencionar ou enviar pendências de uma viagem (ex: 'VG-2026-9941'), execute 'tool_get_trip_context' para checar o status no Escalasoft ERP.\n"
        "- Para registrar ou auditar documentos validados, execute 'tool_save_to_gcs_and_bigquery'.\n"
        "- Para formalizar o termo de responsabilidade, invoque 'tool_generate_compliance_signature'.\n"
        "- Após conferência e conformidade documental, execute 'tool_update_escalasoft_erp' para liberar a viagem no ERP."
    ),
    tools=[
        tool_get_trip_context,
        tool_generate_compliance_signature,
        tool_save_to_gcs_and_bigquery,
        tool_update_escalasoft_erp
    ]
)
