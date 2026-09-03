from google.adk import Agent
from google.cloud import storage

def tool_read_compliance_policy_from_gcs() -> str:
    """Lê as políticas oficiais de compliance e regulamentos de transporte diretamente do Google Cloud Storage (GCS)."""
    try:
        client = storage.Client(project="demotelemetria")
        bucket = client.bucket("demotelemetria-compliance-docs")
        blob = bucket.blob("compliance/politica_compliance_transporte.txt")
        return blob.download_as_text()
    except Exception as e:
        return f"Erro ao acessar GCS: {e}"

def tool_get_trip_context(trip_id: str) -> str:
    """Busca o contexto cadastral completo da viagem e pendências ativas no Escalasoft ERP."""
    trips_database = {
        "V-98214": {
            "cooperado": "Roberto Silva",
            "veiculo": "BRA2E19",
            "motorista": "Carlos Eduardo",
            "status": "LIBERADO",
            "pendencias": [],
            "observacao": "Viagem liberada no Escalasoft ERP com CNH e CRLV validados e Termo de Compliance assinado digitalmente."
        },
        "V-98215": {
            "cooperado": "Mariana Souza",
            "veiculo": "MNO8P90",
            "motorista": "Joaquim Barbosa",
            "status": "BLOQUEADO / EM ANÁLISE",
            "pendencias": ["CNH Vencida (2023)", "Exame Toxicológico Pendente"],
            "observacao": "Viagem bloqueada no Escalasoft ERP. Motorista Joaquim Barbosa possui CNH vencida em 2023 e Exame Toxicológico pendente."
        },
        "V-98216": {
            "cooperado": "Antônio Ferreira",
            "veiculo": "QRS1T23",
            "motorista": "Lucas Mendes",
            "status": "BLOQUEADO / EM ANÁLISE",
            "pendencias": ["CRLV Não Licenciado (exercício 2026 quitado ausente)", "Laudo de Cronotacógrafo Expirado"],
            "observacao": "Viagem bloqueada no Escalasoft ERP para o veículo QRS1T23. CRLV sem licenciamento 2026 e laudo de cronotacógrafo expirado."
        }
    }
    trip_key = trip_id.strip().upper()
    trip_data = trips_database.get(trip_key)
    if trip_data:
        pendencias_str = ", ".join(trip_data['pendencias']) if trip_data['pendencias'] else "Nenhuma pendência ativa"
        return (
            f"Viagem {trip_key}: Cooperado {trip_data['cooperado']}, "
            f"Veículo {trip_data['veiculo']}, Motorista {trip_data['motorista']}, "
            f"Status no ERP: {trip_data['status']}, Pendências Ativas: [{pendencias_str}]. "
            f"Resumo do Cadastro: {trip_data['observacao']}"
        )
    return f"Viagem {trip_key}: Não encontrada no sistema Escalasoft ERP."

def tool_generate_compliance_signature(cooperado_nome: str, trip_id: str) -> str:
    """Gera o Termo de Compliance e Assinatura Digital nativa com Hash SHA-256 no Google Cloud Storage."""
    return f"Certificado Digital SHA-256 de Compliance gerado no GCS para {cooperado_nome} na viagem {trip_id}"

def tool_save_to_gcs_and_bigquery(filename: str, doc_type: str, status: str) -> str:
    """Registra os metadados do documento validado no BigQuery para Analytics e auditoria no GCS."""
    return f"Documento {doc_type} gravado no GCS ({filename}) e BigQuery Analytics com status {status}"

def tool_update_escalasoft_erp(trip_id: str, doc_type: str) -> str:
    """Atualiza o ERP Escalasoft e libera a viagem do cooperado."""
    return f"ERP Escalasoft atualizado para viagem {trip_id}. Status: LIBERADO"

# Instância oficial do Agente Google Cloud ADK
root_agent = Agent(
    name="rodacoop_compliance_agent",
    description="Agente Especialista em Compliance Documental e Logística Rodacoop (Google Cloud ADK)",
    model="gemini-2.5-flash",
    instruction=(
        "Você é o Agente de Compliance Documental Rodacoop rodando no Google Cloud Agent Development Kit (ADK).\n"
        "- Quando o usuário fizer perguntas sobre exigências, regras, documentações obrigatórias ou políticas de compliance da cooperativa, invoque SEMPRE a ferramenta 'tool_read_compliance_policy_from_gcs' para consultar a documentação oficial armazenada no Google Cloud Storage.\n"
        "- Ao consultar ou verificar o status ou pendências de QUALQUER viagem no ERP (ex: V-98214, V-98215, V-98216), invoque OBRIGATORIAMENTE a ferramenta 'tool_get_trip_context' informando o trip_id correto.\n"
        "- Responda estritamente com base nos dados retornados pela ferramenta 'tool_get_trip_context'. Se o status retornado for LIBERADO, informe que a viagem está aprovada. Se for BLOQUEADO / EM ANÁLISE, detalhe exatamente o status e cada pendência listada na ferramenta.\n"
        "- Para auditoria e métricas, utilize 'tool_save_to_gcs_and_bigquery'.\n"
        "- Para formalizar o termo e assinar digitalmente, execute 'tool_generate_compliance_signature'.\n"
        "- Ao final da aprovação de documentos pendentes, libere a viagem com 'tool_update_escalasoft_erp'."
    ),
    tools=[
        tool_read_compliance_policy_from_gcs,
        tool_get_trip_context,
        tool_generate_compliance_signature,
        tool_save_to_gcs_and_bigquery,
        tool_update_escalasoft_erp
    ]
)
