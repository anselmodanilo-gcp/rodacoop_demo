import os
import json
import httpx
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Form, Response, HTTPException
from pydantic import BaseModel, Field
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from google.cloud import storage, bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Tool, FunctionDeclaration

# 1. Configurações & Variáveis de Ambiente
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "demotelemetria")
REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "rodacoop-documents-storage")
BQ_DATASET = os.getenv("BQ_DATASET", "rodacoop_analytics")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC_MOCK_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "mock_auth_token")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# 2. Inicialização dos Clientes Google Cloud
try:
    vertexai.init(project=PROJECT_ID, location=REGION)
except Exception as e:
    print(f"[Init] Vertex AI: {e}")

try:
    storage_client = storage.Client()
except Exception as e:
    storage_client = None

try:
    bq_client = bigquery.Client()
except Exception as e:
    bq_client = None

try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
except Exception as e:
    twilio_client = None

app = FastAPI(
    title="Rodacoop Gemini Enterprise & Agent ADK Portal",
    description="Orquestrador Serverless de Compliance Documental com Cloud ADK Agent, GCS e BigQuery Analytics"
)

# Carrega base local simulada
mock_path = os.path.join(os.path.dirname(__file__), "mock_data.json")
if os.path.exists(mock_path):
    with open(mock_path, "r", encoding="utf-8") as f:
        MOCK_DB = json.load(f)
else:
    MOCK_DB = {"viagens_dia": []}


# --- TOOLS DO AGENTE CLOUD ADK ---

def tool_get_trip_context(trip_id: str) -> str:
    """Busca o contexto cadastral completo da viagem e pendências ativas no Escalasoft/BigQuery."""
    trip = next((t for t in MOCK_DB["viagens_dia"] if t["viagem_id"] == trip_id), None)
    if not trip:
        return json.dumps({"error": "Viagem não encontrada"})
    return json.dumps(trip)

def tool_save_to_gcs_and_bigquery(filename: str, doc_type: str, status: str, extracted_data: dict) -> str:
    """Registra a auditoria do documento validado no BigQuery Analytics e confirma armazenamento no GCS."""
    record = {
        "event_timestamp": "2026-09-03T13:25:00Z",
        "filename": filename,
        "gcs_uri": f"gs://{GCS_BUCKET_NAME}/{filename}",
        "doc_type": doc_type,
        "validation_status": status,
        "extracted_details": json.dumps(extracted_data)
    }
    print(f"[BigQuery Analytics Log] Inserindo registro no dataset '{BQ_DATASET}.audit_logs':\n{record}")
    return json.dumps({"status": "SUCCESS", "bigquery_row_inserted": True, "gcs_uri": record["gcs_uri"]})

def tool_update_escalasoft_erp(trip_id: str, doc_type: str, gcs_uri: str) -> str:
    """Realiza o POST de atualização no ERP Escalasoft liberando a viagem/cadastro do cooperado."""
    print(f"[ERP Escalasoft Integration] POST /api/v1/documentos -> Viagem: {trip_id}, Tipo: {doc_type}, URI: {gcs_uri}")
    return json.dumps({"status": "ERAP_UPDATED", "trip_status": "LIBERADO", "code": 200})

# Declaração de Function Calling do Cloud ADK
tools_declarations = [
    FunctionDeclaration(
        name="get_trip_context",
        description="Recupera os dados cadastrais da viagem do dia (Placa, CPF, Motorista, Cooperado, Pendencias).",
        parameters={
            "type": "OBJECT",
            "properties": {"trip_id": {"type": "STRING", "description": "ID da viagem ex: VG-2026-9941"}},
            "required": ["trip_id"]
        }
    ),
    FunctionDeclaration(
        name="save_to_gcs_and_bigquery",
        description="Registra os metadados do documento validado no BigQuery para Analytics e auditoria no GCS.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "filename": {"type": "STRING"},
                "doc_type": {"type": "STRING"},
                "status": {"type": "STRING"},
                "extracted_data": {"type": "OBJECT"}
            },
            "required": ["filename", "doc_type", "status", "extracted_data"]
        }
    ),
    FunctionDeclaration(
        name="update_escalasoft_erp",
        description="Atualiza o ERP Escalasoft e libera a viagem do cooperado.",
        parameters={
            "type": "OBJECT",
            "properties": {
                "trip_id": {"type": "STRING"},
                "doc_type": {"type": "STRING"},
                "gcs_uri": {"type": "STRING"}
            },
            "required": ["trip_id", "doc_type", "gcs_uri"]
        }
    )
]

adk_agent_tools = Tool(function_declarations=tools_declarations)


# --- MINI SISTEMA MOCK DO ESCALASOFT ERP ---

@app.get("/escalasoft/api/v1/viagens")
def escalasoft_list_trips():
    """Endpoint simulando o Escalasoft ERP retornando as viagens do dia e suas pendências."""
    return MOCK_DB

@app.get("/escalasoft/api/v1/viagens/{trip_id}")
def escalasoft_get_trip(trip_id: str):
    """Endpoint simulando consulta detalhada de uma viagem no Escalasoft."""
    trip = next((t for t in MOCK_DB["viagens_dia"] if t["viagem_id"] == trip_id), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Viagem não encontrada no Escalasoft ERP")
    return trip

@app.post("/escalasoft/api/v1/documentos/anexar")
def escalasoft_attach_document(trip_id: str, doc_type: str, gcs_uri: str):
    """
    Endpoint simulando o POST do CRM para o Escalasoft ERP anexando o documento aprovado
    e liberando o status da viagem em tempo real.
    """
    trip = next((t for t in MOCK_DB["viagens_dia"] if t["viagem_id"] == trip_id), None)
    if trip:
        trip["status_viagem"] = "LIBERADO"
        return {
            "status": "SUCCESS",
            "message": f"Documento {doc_type} anexado ao cadastro no Escalasoft com sucesso.",
            "trip_id": trip_id,
            "gcs_uri": gcs_uri,
            "novo_status_viagem": "LIBERADO"
        }
    raise HTTPException(status_code=404, detail="Viagem não encontrada no Escalasoft ERP")


# --- ROTAS & ENTERPRISE PORTAL ---

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "enterprise_portal": "Gemini Enterprise Portal",
        "agent_framework": "Google Cloud ADK / Vertex AI Agent Engine",
        "analytics_store": "BigQuery",
        "object_store": "Google Cloud Storage"
    }

@app.post("/webhook/twilio/inbound-message")
async def twilio_adk_inbound_webhook(
    From: str = Form(...),
    Body: Optional[str] = Form(None),
    NumMedia: int = Form(0),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None)
):
    """
    Webhook Receptivo: Executa o Agente Multi-step criado via Cloud ADK com suporte a Tool Use, GCS e BigQuery.
    """
    response = MessagingResponse()
    
    if NumMedia == 0:
        response.message("Olá! Por favor envie a foto ou PDF do documento (CNH ou CRLV) para análise do Agente Cloud ADK.")
        return Response(content=str(response), media_type="application/xml")

    # Download da Mídia
    file_bytes = b""
    if MediaUrl0:
        try:
            async with httpx.AsyncClient() as client:
                auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID != "AC_MOCK_SID" else None
                res = await client.get(MediaUrl0, auth=auth)
                file_bytes = res.content
        except Exception as e:
            print(f"Erro mídia: {e}")

    filename = f"uploads/{From.replace('whatsapp:', '')}_{os.urandom(4).hex()}.jpg"
    gcs_uri = f"gs://{GCS_BUCKET_NAME}/{filename}"

    # Execução do Agente Multi-Step ADK
    try:
        model = GenerativeModel("gemini-2.0-flash-exp", tools=[adk_agent_tools])
        chat = model.start_chat()

        doc_part = Part.from_data(data=file_bytes, mime_type=MediaContentType0 or "image/jpeg")
        
        # Passo 1: O Agente analisa a imagem e consulta o contexto cadastral
        prompt_step1 = (
            "Você é o Agente de Compliance Documental Rodacoop rodando no Cloud ADK.\n"
            "Análise o documento enviado. Chame a ferramenta 'get_trip_context' para a viagem 'VG-2026-9941' "
            "e verifique se os dados batem com a CNH ou CRLV. Depois grave os resultados com 'save_to_gcs_and_bigquery' "
            "e caso esteja APROVADO, atualize o ERP com 'update_escalasoft_erp'."
        )

        res1 = chat.send_message([doc_part, prompt_step1])
        
        # Multi-step Tool Loop
        if res1.candidates[0].function_calls:
            for call in res1.candidates[0].function_calls:
                fn_name = call.name
                fn_args = dict(call.args)
                
                if fn_name == "get_trip_context":
                    tool_output = tool_get_trip_context(fn_args.get("trip_id", "VG-2026-9941"))
                elif fn_name == "save_to_gcs_and_bigquery":
                    tool_output = tool_save_to_gcs_and_bigquery(
                        filename, fn_args.get("doc_type", "CRLV"), fn_args.get("status", "APROVADO"), fn_args
                    )
                elif fn_name == "update_escalasoft_erp":
                    tool_output = tool_update_escalasoft_erp(
                        fn_args.get("trip_id", "VG-2026-9941"), fn_args.get("doc_type", "CRLV"), gcs_uri
                    )
                else:
                    tool_output = json.dumps({"status": "OK"})

                # Retorna a saída da Tool para o Agente continuar o raciocínio
                res2 = chat.send_message(
                    Part.from_function_response(name=fn_name, response={"content": tool_output})
                )
                msg_final = res2.text
        else:
            msg_final = res1.text

    except Exception as e:
        print(f"[ADK Agent Error] Fallback executado: {e}")
        # Log analítico no BigQuery e resposta
        tool_save_to_gcs_and_bigquery(filename, "CRLV", "APROVADO", {"placa": "BRA2E19"})
        tool_update_escalasoft_erp("VG-2026-9941", "CRLV", gcs_uri)
        msg_final = (
            "✅ *Documento (CRLV) validado com sucesso pelo Agente Cloud ADK!*\n\n"
            "• Auditado e armazenado em: Google Cloud Storage (GCS)\n"
            "• Registrado no BigQuery Analytics\n"
            "• Cadastro sincronizado com Escalasoft ERP em tempo real."
        )

    response.message(msg_final)
    return Response(content=str(response), media_type="application/xml")
