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
        },
        "V-99001": {
            "cooperado": "Fazenda Grão de Ouro / Cooperado João Pedro",
            "veiculo": "ABC9876",
            "motorista": "Fernando Alcantara",
            "status": "RETIDO NA BARREIRA FISCAL SEFAZ",
            "pendencias": ["Divergência de Peso de Balança (Excesso de Carga)", "Divergência Tributária SEFAZ/MDF-e"],
            "observacao": "Carga de 48 toneladas de soja retida no Posto Fiscal de Rio Verde. MDF-e emitido para 42 toneladas. Excesso de 6 toneladas não declaradas."
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

def tool_check_telemetry_and_scale_logs(trip_id: str) -> str:
    """Investiga os logs de telemetria IoT do caminhão e pesagem de balança de embarque na fazenda."""
    if trip_id.upper() == "V-99001":
        return (
            "LOG TELEMETRIA E BALANÇA (Viagem V-99001):\n"
            "- Ticket de Pesagem Balança Eletrônica Fazenda Grão de Ouro (14/10/2026 08:30): Peso Bruto 48.250 kg (Tara 14.100 kg = Carga Líquida 34.150 kg).\n"
            "- MDF-e N° 458911 emitido automaticamente pelo Escalasoft: Carga Declarada 28.000 kg.\n"
            "- Telemetria Rastreador GPS: O veículo fez uma parada não autorizada de 45 minutos no Armazém Central às 09:15 antes da barreira fiscal.\n"
            "- Diagnóstico IoT: Divergência de 6,15 toneladas entre a pesagem real da balança e a nota emitida pelo sistema."
        )
    return f"Sem anomalias de telemetria ou balança registradas para a viagem {trip_id}."

def tool_analyze_sefaz_tax_impact(trip_id: str, excess_weight_tons: float) -> str:
    """Simula o cálculo de multa fiscal SEFAZ e recolhimento complementar de ICMS no Google Cloud BigQuery."""
    val_multa = excess_weight_tons * 850.00
    val_icms_complementar = excess_weight_tons * 320.00
    total = val_multa + val_icms_complementar
    return (
        f"ANÁLISE DE IMPACTO FISCAL SEFAZ (Viagem {trip_id} - Excesso: {excess_weight_tons} ton):\n"
        f"1. Multa SEFAZ por Excesso de Peso em MDF-e: R$ {val_multa:.2f}\n"
        f"2. ICMS Complementar Diferido sobre Carga Adicional: R$ {val_icms_complementar:.2f}\n"
        f"3. Custo Total de Regularização: R$ {total:.2f}\n"
        f"4. Ação Exigida: Emissão de DARE Complementar e Retificação de MDF-e/CT-e no Escalasoft ERP para liberação no Posto Fiscal."
    )

def tool_issue_complementary_cte_and_release(trip_id: str, dare_receipt_code: str) -> str:
    """Emite o CT-e complementar, anexa o comprovante DARE e solicita a liberação imediata no ERP e Posto Fiscal."""
    return (
        f"AÇÃO CONCLUÍDA COM SUCESSO (Viagem {trip_id}):\n"
        f"1. DARE {dare_receipt_code} anexado e auditado no GCS (gs://rodacoop-documents-storage/dare/{trip_id}.pdf).\n"
        f"2. CT-e Complementar e MDF-e Retificado autorizados com sucesso na SEFAZ.\n"
        f"3. Sincronização em tempo real com Escalasoft ERP: Status alterado para LIBERADO EM TRÂNSITO.\n"
        f"4. Notificação enviada ao motorista Fernando Alcantara no WhatsApp com o novo QR Code de liberação."
    )

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
    description="Agente Especialista em Compliance Documental, Investigação Logística e Fiscal Rodacoop (Google Cloud ADK)",
    model="gemini-2.5-flash",
    instruction=(
        "Você é o Agente de Compliance e Investigação Operacional Rodacoop no Google Cloud ADK.\n"
        "Você é capaz de conduzir investigações complexas em múltiplos turnos de conversa para resolver sinistros, reterções fiscais e problemas operacionais de transporte.\n"
        "- Quando perguntado sobre regras ou exigências, consulte 'tool_read_compliance_policy_from_gcs'.\n"
        "- Para verificar qualquer viagem ou incidente no ERP, use 'tool_get_trip_context'.\n"
        "- Se a viagem apresentar inconsistências ou retenção na barreira fiscal/SEFAZ (ex: V-99001), use a ferramenta 'tool_check_telemetry_and_scale_logs' para investigar telemetria GPS e pesagem de balança.\n"
        "- Para calcular multas e impostos adicionais da retenção, execute 'tool_analyze_sefaz_tax_impact'.\n"
        "- Para emitir documentos complementares e regularizar a retenção junto à SEFAZ/ERP, execute 'tool_issue_complementary_cte_and_release'.\n"
        "- Para auditoria e métricas, utilize 'tool_save_to_gcs_and_bigquery'."
    ),
    tools=[
        tool_read_compliance_policy_from_gcs,
        tool_get_trip_context,
        tool_check_telemetry_and_scale_logs,
        tool_analyze_sefaz_tax_impact,
        tool_issue_complementary_cte_and_release,
        tool_generate_compliance_signature,
        tool_save_to_gcs_and_bigquery,
        tool_update_escalasoft_erp
    ]
)
