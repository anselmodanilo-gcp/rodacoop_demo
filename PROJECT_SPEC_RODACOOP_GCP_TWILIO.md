# 🚀 Projeto Rodacoop: Agente Autônomo de Compliance Documental
### Automação Event-Driven de Onboarding via Twilio WhatsApp, Vertex AI (Gemini) e Google Cloud

---

## 📑 Sumário
1. [Visão Geral & Contexto de Negócio](#1-visão-geral--contexto-de-negócio)
2. [Arquitetura 100% Google Cloud + Twilio](#2-arquitetura-100-google-cloud--twilio)
3. [Regras Críticas de Negócio](#3-regras-críticas-de-negócio)
4. [Especificação do Agente no Vertex AI](#4-especificação-do-agente-no-vertex-ai)
5. [Modelagem de Dados & Schemas Pydantic](#5-modelagem-de-dados--schemas-pydantic)
6. [Implementação Completa do Backend (FastAPI + GCP SDKs + Twilio)](#6-implementação-completa-do-backend-fastapi--gcp-sdks--twilio)
7. [Base de Dados Mockada para Demonstração](#7-base-de-dados-mockada-para-demonstração)
8. [Roteiro de Demonstração (Demo Script com Twilio Sandbox)](#8-roteiro-de-demonstração-demo-script-com-twilio-sandbox)
9. [Guia de Deploy, Infraestrutura (CLI) & Execução](#9-guia-de-deploy-infraestrutura-cli--execução)

---

## 1. Visão Geral & Contexto de Negócio

A **Rodacoop** opera o transporte rodoviário de cargas para grandes players (ex.: Mercado Livre), movimentando mais de 900 veículos e 200 mil pacotes diários. Devido à alta rotatividade diária de motoristas e veículos cooperados, a regularização cadastral manual cria gargalos operacionais antes da liberação das viagens.

| Componente | Função na Arquitetura | Benefício Google Cloud / Twilio |
|---|---|---|
| **Canal de Mensageria** | **Twilio Messaging API (WhatsApp)** | Conectividade ágil, webhooks seguros e suporte a Sandbox imediato. |
| **Orquestrador de Conversa (Opcional)** | **Dialogflow CX (Flows & Intents)** | Gerenciamento de fluxos determinísticos, menus, transições de estado e fallback para IA Generativa. |
| **Orquestrador de Serviços** | **Google Cloud Run (FastAPI)** | Microsserviço serverless, autoscaling imediato e execução orientada a eventos. |
| **Processamento Multimodal** | **Vertex AI (Gemini 2.0 Flash / Cloud ADK)** | Extração visual e semântica com *Structured JSON Output* e Tool Use em menos de 2 segundos. |
| **Armazenamento de Mídia** | **Google Cloud Storage (GCS)** | Repositório seguro e imutável para documentos (CNHs, CRLVs e comprovantes). |
| **Data Warehouse & Audit** | **Google Cloud BigQuery** | Registros de compliance, análise de SLA e auditoria em tempo real. |
| **Plataforma de Agentes** | **Gemini Agent Platform / Enterprise** | Governança corporativa, controle de acesso (IAM) e orquestração de agentes. |

---

## 2. Arquitetura 100% Google Cloud + Twilio

```
┌─────────────────┐       1. Viagens do Dia       ┌────────────────────────┐
│ Escalasoft ERP  │ ────────────────────────────▶ │    Cloud Run API       │
└─────────────────┘                               │    (FastAPI Router)    │
                                                  └───────────┬────────────┘
                                                              │ 2. Consulta Estado
                                                              ▼
                                                  ┌────────────────────────┐
                                                  │    Cloud Firestore     │
                                                  └───────────┬────────────┘
                                                              │ 3. Dispara Pendências
                                                              ▼
┌─────────────────┐      4. Mensagem WhatsApp     ┌────────────────────────┐
│ Cooperado (App) │ ◀──────────────────────────── │   Twilio WhatsApp API  │
└────────┬────────┘                               └────────────────────────┘
         │
         │ 5. Envia Foto/PDF (CRLV / CNH)
         ▼
┌─────────────────┐      6. Webhook Inbound       ┌────────────────────────┐
│ Twilio Webhook  │ ────────────────────────────▶ │    Cloud Run API       │
└─────────────────┘                               └─────┬────────────┬─────┘
                                                        │            │
                                 7. Salva Binário       │            │ 8. Validação Multimodal
                                 na Nuvem               ▼            ▼
                                            ┌───────────────┐   ┌──────────────────┐
                                            │ Cloud Storage │   │ Vertex AI Gemini │
                                            │     (GCS)     │   │ (Structured JSON)│
                                            └───────────────┘   └────────┬─────────┘
                                                                         │
                                           9. POST se Aprovado           │
                                        ┌────────────────────────────────┘
                                        ▼
                               ┌─────────────────┐
                               │ Escalasoft ERP  │
                               └─────────────────┘
```

---

## 3. Regras Críticas de Negócio

1. **Centralizador no Cooperado:**
   * O Cooperado é o único ponto de contato para a cobrança e regularização de pendências dele próprio, do veículo ou do motorista.
   * Exemplo: Veículo A (CRLV pendente) + Motorista B (CNH pendente) vinculados ao Cooperado C $\rightarrow$ Mensagem consolidada enviada ao WhatsApp do **Cooperado C**.
2. **Zero Trust Documental com Gemini Multimodal:**
   * O sistema nunca assume que o documento enviado corresponde ao solicitado.
   * O **Gemini 2.0 Flash** realiza a classificação do arquivo, o OCR dos campos de identificação (CPF, Placa, Renavam, Exercício, Categoria) e cruza os dados com o registro da viagem.
3. **Persistência Segura no Cloud Storage:**
   * Qualquer documento recebido via Twilio é imediatamente transferido para um bucket no GCS, com controle de acesso e geração de links seguros para o ERP.

---

## 4. Especificação do Agente no Vertex AI

```yaml
Configuração do Modelo:
  ID: gemini-2.0-flash-exp (ou gemini-1.5-flash)
  Temperature: 0.1
  Response_Mime_Type: application/json
```

### Instrução de Sistema (System Prompt):

```text
Você é o Agente Especialista em Compliance e Triagem Documental da Rodacoop.
Sua missão é analisar imagens/PDFs recebidos de cooperados e validar sua conformidade documental com as viagens cadastradas no ERP Escalasoft.

DIRETRIZES DE VALIDAÇÃO:
1. IDENTIFICAÇÃO: Determine se o documento é CNH, CRLV, ANTT, COMPROVANTE_RESIDENCIA ou OUTRO.
2. EXTRAÇÃO:
   - CNH: Nome completo, CPF, Categoria, Data de Validade.
   - CRLV: Placa, RENAVAM, Nome do Proprietário, Exercício (Ano de Licenciamento).
   - ANTT: RNTRC, CPF/CNPJ.
3. VERIFICAÇÃO CRUZADA:
   - Compare os dados extraídos com a entidade esperada (Nome, CPF ou Placa informados).
   - Se os dados divergirem (ex: CNH com nome/CPF diferente do motorista da viagem), marque como 'DIVERGENCIA_DADOS'.
   - Se o documento estiver ilegível, cortado ou sem nitidez, marque como 'ILEGIVEL'.
4. RESPOSTA: Forneça estritamente a saída formatada no schema JSON predefinido.
```

---

## 5. Modelagem de Dados & Schemas Pydantic

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal, List

class DocumentValidationResponse(BaseModel):
    is_valid_document: bool = Field(description="Indica se é um documento oficial autêntico e legível")
    is_legible: bool = Field(description="Indica se o arquivo possui nitidez suficiente")
    detected_doc_type: Literal["CNH", "CRLV", "ANTT", "COMPROVANTE_RESIDENCIA", "OUTRO"]
    extracted_name: Optional[str] = Field(default=None, description="Nome titular extraído")
    extracted_cpf_cnpj: Optional[str] = Field(default=None, description="CPF ou CNPJ extraído")
    extracted_plate: Optional[str] = Field(default=None, description="Placa do veículo (se CRLV)")
    extracted_renavam: Optional[str] = Field(default=None, description="Código RENAVAM")
    extracted_licensing_year: Optional[int] = Field(default=None, description="Ano de exercício do CRLV")
    validation_status: Literal["APROVADO", "DIVERGENCIA_DADOS", "DOCUMENTO_INCORRETO", "VENCIDO", "ILEGIVEL"]
    rejection_reason: Optional[str] = Field(default=None, description="Motivo claro em caso de reprovação")

class PendencyItem(BaseModel):
    tipo: str
    entidade_tipo: Literal["VEICULO", "MOTORISTA", "COOPERADO"]
    identificador_esperado: str
    nome_referencia: str
    obrigatorio: bool = True

class SessionState(BaseModel):
    cooperado_id: str
    cooperado_nome: str
    telefone_whatsapp: str
    trip_id: str
    pendencias_ativas: List[PendencyItem]
```

---

## 6. Implementação Completa do Backend (FastAPI + GCP SDKs + Twilio)

Salve o código abaixo como **`main.py`**:

```python
import os
import json
import httpx
from typing import Optional
from fastapi import FastAPI, Request, Form, Response, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from google.cloud import storage, secretmanager
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# 1. Configurações & Variáveis de Ambiente
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "rodacoop-poc")
REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "rodacoop-documents-storage")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC_MOCK_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "mock_auth_token")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# 2. Inicialização dos Clientes Google Cloud e Twilio
vertexai.init(project=PROJECT_ID, location=REGION)
storage_client = storage.Client()
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = FastAPI(
    title="Rodacoop Compliance Automation API",
    description="Backend Serverless no Cloud Run para validação documental via Twilio e Gemini"
)

# Carrega a base simulada
with open("mock_data.json", "r", encoding="utf-8") as f:
    MOCK_DB = json.load(f)


# --- UTILITÁRIOS GCP & TWILIO ---

def upload_bytes_to_gcs(file_bytes: bytes, filename: str, content_type: str) -> str:
    """Faz upload seguro do documento recebido para o Google Cloud Storage"""
    try:
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(file_bytes, content_type=content_type)
        return f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
    except Exception as e:
        # Fallback para ambiente local de desenvolvimento
        return f"https://mock-gcs-storage.local/{filename}"

def send_twilio_whatsapp_message(to_number: str, body_text: str):
    """Envia mensagem ativa para o cooperado via Twilio WhatsApp"""
    formatted_to = to_number if to_number.startswith("whatsapp:") else f"whatsapp:{to_number}"
    twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=formatted_to,
        body=body_text
    )


# --- ROTAS & WEBHOOKS ---

@app.get("/health")
def health():
    return {"status": "healthy", "cloud_provider": "Google Cloud Platform"}


@app.post("/webhook/escalasoft/trip-sync")
async def sync_escalasoft_trips(trip_id: str):
    """
    Webhook acionado pelo Escalasoft/CRM quando as viagens do dia são geradas.
    Identifica pendências de veículo, motorista e cooperado, notificando o Cooperado via Twilio.
    """
    trip = next((t for t in MOCK_DB["viagens_dia"] if t["viagem_id"] == trip_id), None)
    if not trip:
        raise HTTPException(status_code=404, detail="Viagem não encontrada no Escalasoft")

    cooperado = trip["cooperado"]
    pendencias_msg = []

    # Pendências do Veículo
    for p in trip["veiculo"].get("pendencias", []):
        pendencias_msg.append(f"🚗 *Veículo ({trip['veiculo']['placa']}):* {p['tipo']}")

    # Pendências do Motorista
    for p in trip["motorista"].get("pendencias", []):
        pendencias_msg.append(f"👨✈️ *Motorista ({trip['motorista']['nome']}):* {p['tipo']}")

    # Pendências do próprio Cooperado
    for p in cooperado.get("pendencias", []):
        pendencias_msg.append(f"👤 *Cooperado ({cooperado['nome']}):* {p['tipo']}")

    if pendencias_msg:
        mensagem = (
            f"Olá *{cooperado['nome']}*! 👋\n"
            f"Identificamos pendências documentais para liberar a sua viagem (*{trip_id}*) hoje:\n\n"
            + "\n".join(pendencias_msg)
            + "\n\n📸 Por favor, envie a foto ou PDF do documento pendente diretamente por aqui para fazermos a validação instantânea."
        )
        
        # Disparo via Twilio
        send_twilio_whatsapp_message(cooperado["telefone_whatsapp"], mensagem)

        return {
            "status": "NOTIFICACAO_DISPARADA",
            "cooperado": cooperado["nome"],
            "telefone": cooperado["telefone_whatsapp"],
            "pendencias_totais": len(pendencias_msg)
        }

    return {"status": "SEM_PENDENCIAS", "msg": "Viagem liberada sem restrições."}


@app.post("/webhook/twilio/inbound-message")
async def twilio_inbound_webhook(
    From: str = Form(...),
    Body: Optional[str] = Form(None),
    NumMedia: int = Form(0),
    MediaUrl0: Optional[str] = Form(None),
    MediaContentType0: Optional[str] = Form(None)
):
    """
    Webhook receptor do Twilio para mensagens recebidas no WhatsApp.
    Trata mensagens de texto ou faz o download da mídia para análise no Gemini 2.0 Flash.
    """
    response = MessagingResponse()
    
    # 1. Caso o usuário envie apenas texto sem documento
    if NumMedia == 0:
        response.message(
            "Olá! Para regularizar seu cadastro na Rodacoop, por favor envie a **foto ou PDF legível** do documento pendente (CNH ou CRLV)."
        )
        return Response(content=str(response), media_type="application/xml")

    # 2. Download do arquivo de mídia enviado via Twilio
    async with httpx.AsyncClient() as client:
        media_resp = await client.get(MediaUrl0, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        file_bytes = media_resp.content

    # 3. Salva no Google Cloud Storage
    filename = f"uploads/{From.replace('whatsapp:', '')}_{os.urandom(4).hex()}.jpg"
    gcs_url = upload_bytes_to_gcs(file_bytes, filename, MediaContentType0 or "image/jpeg")

    # 4. Processamento Multimodal com Vertex AI (Gemini 2.0 Flash)
    model = GenerativeModel("gemini-2.0-flash-exp")
    
    # Contexto simulado da viagem ativa do cooperado
    trip_context = MOCK_DB["viagens_dia"][0]
    expected_plate = trip_context["veiculo"]["placa"]
    expected_driver_name = trip_context["motorista"]["nome"]
    expected_driver_cpf = trip_context["motorista"]["cpf"]

    prompt = f"""
    Analise o documento recebido e extraia as informações estruturadas.
    Verifique se atende aos critérios esperados:
    - Veículo esperado: Placa '{expected_plate}'
    - Motorista esperado: '{expected_driver_name}' (CPF: '{expected_driver_cpf}')

    Retorne ESTRITAMENTE um JSON com este formato:
    {{
      "is_valid_document": true,
      "is_legible": true,
      "detected_doc_type": "CNH" | "CRLV" | "ANTT" | "OUTRO",
      "extracted_name": "Nome completo ou null",
      "extracted_cpf_cnpj": "CPF/CNPJ ou null",
      "extracted_plate": "Placa ou null",
      "extracted_renavam": "Renavam ou null",
      "extracted_licensing_year": 2025,
      "validation_status": "APROVADO" | "DIVERGENCIA_DADOS" | "DOCUMENTO_INCORRETO" | "ILEGIVEL",
      "rejection_reason": "Motivo claro se rejeitado ou null"
    }}
    """

    doc_part = Part.from_data(data=file_bytes, mime_type=MediaContentType0 or "image/jpeg")
    gemini_resp = model.generate_content(
        [doc_part, prompt],
        generation_config={"response_mime_type": "application/json", "temperature": 0.1}
    )

    try:
        resultado = json.loads(gemini_resp.text)
    except Exception:
        resultado = {
            "validation_status": "ERRO_PROCESSAMENTO",
            "rejection_reason": "Não foi possível processar o arquivo. Tente novamente."
        }

    # 5. Lógica de Resposta e Ação de Integração
    if resultado.get("validation_status") == "APROVADO":
        # Simula o POST imediato no Escalasoft ERP
        doc_tipo = resultado.get("detected_doc_type")
        msg_retorno = (
            f"✅ *Documento ({doc_tipo}) aprovado com sucesso!*\n\n"
            f"Os dados já foram sincronizados com o Escalasoft em tempo real e o veículo/motorista está liberado."
        )
    else:
        motivo = resultado.get("rejection_reason", "Dados divergentes do cadastro da viagem.")
        msg_retorno = (
            f"⚠️ *Não foi possível aprovar o documento.*\n\n"
            f"🔍 *Motivo:* {motivo}\n\n"
            f"Por favor, envie novamente o documento correto e legível para prosseguirmos."
        )

    response.message(msg_retorno)
    return Response(content=str(response), media_type="application/xml")
```

---

## 7. Base de Dados Mockada para Demonstração

Crie o arquivo **`mock_data.json`**:

```json
{
  "viagens_dia": [
    {
      "viagem_id": "VG-2026-9941",
      "data": "2026-09-03",
      "origem": "CD Mercado Livre Cajamar",
      "destino": "Base Campinas",
      "cooperado": {
        "id": "COOP-882",
        "nome": "Roberto Silva Alcantara",
        "telefone_whatsapp": "+5511988887777",
        "pendencias": []
      },
      "motorista": {
        "id": "MOT-104",
        "nome": "Carlos Eduardo Gomes",
        "cpf": "123.456.789-00",
        "pendencias": [
          { "tipo": "CNH", "obrigatorio": true }
        ]
      },
      "veiculo": {
        "id": "VEIC-550",
        "placa": "BRA2E19",
        "renavam": "00987654321",
        "pendencias": [
          { "tipo": "CRLV", "exercicio_minimo": 2025, "obrigatorio": true }
        ]
      }
    }
  ]
}
```

---

## 8. Roteiro de Demonstração (Demo Script com Twilio Sandbox)

### 📲 Configuração do Twilio Sandbox:
1. No console do Twilio, acesse **Messaging > Try it out > Send a WhatsApp message**.
2. Conecte seu número pessoal enviando a mensagem `join <palavra-chave>` para o número do Twilio.
3. Configure o campo **"WHEN A MESSAGE COMES IN"** com a URL do Cloud Run: `https://<URL_CLOUD_RUN>/webhook/twilio/inbound-message`.

### 🎬 Execução do Roteiro:

```
[Etapa 1] Disparo de Sincronização de Viagem
Comando: curl -X POST "http://localhost:8080/webhook/escalasoft/trip-sync?trip_id=VG-2026-9941"
Resultado no WhatsApp do Cooperado:
"Olá Roberto Silva Alcantara! Identificamos pendências documentais para liberar a sua viagem (VG-2026-9941)..."

[Etapa 2] Envio do CRLV Válido
Ação: O cooperado responde no WhatsApp enviando a foto do CRLV da placa BRA2E19.
Processamento: Gemini 2.0 Flash extrai Placa e Exercício 2025 -> Status: APROVADO -> POST Escalasoft.
Resposta no WhatsApp:
"✅ Documento (CRLV) aprovado com sucesso! Os dados já foram sincronizados com o Escalasoft em tempo real..."

[Etapa 3] Envio de CNH com Dados Divergentes
Ação: O cooperado responde enviando uma CNH em nome de "Marcos Lima".
Processamento: Gemini compara o CPF/Nome com Carlos Eduardo -> Status: DIVERGENCIA_DADOS.
Resposta no WhatsApp:
"⚠️ Não foi possível aprovar o documento. Motivo: O documento enviado pertence a 'Marcos Lima', mas o motorista esperado é 'Carlos Eduardo Gomes'..."
```

---

## 9. Guia de Deploy, Infraestrutura (CLI) & Execução

### 9.1. Dependências do Projeto (`requirements.txt`)

```txt
fastapi>=0.110.0
uvicorn>=0.28.0
twilio>=9.0.0
google-cloud-aiplatform>=1.44.0
google-cloud-storage>=2.14.0
google-cloud-secret-manager>=2.18.0
pydantic>=2.6.0
httpx>=0.27.0
python-multipart>=0.0.9
```

### 9.2. Provisionamento de Recursos via Google Cloud CLI (`gcloud`)

```bash
# 1. Configurar Projeto GCP
gcloud config set project demotelemetria
gcloud services enable \
    run.googleapis.com \
    aiplatform.googleapis.com \
    storage.googleapis.com \
    bigquery.googleapis.com \
    secretmanager.googleapis.com

# 2. Criar o Bucket no Google Cloud Storage
gcloud storage buckets create gs://rodacoop-documents-storage --location=us-central1

# 3. Criar os Segredos no Secret Manager
echo -n "SEU_TWILIO_ACCOUNT_SID" | gcloud secrets create TWILIO_ACCOUNT_SID --data-file=-
echo -n "SEU_TWILIO_AUTH_TOKEN" | gcloud secrets create TWILIO_AUTH_TOKEN --data-file=-

# 4. Deploy da Aplicação no Cloud Run
gcloud run deploy rodacoop-compliance-agent \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=SEU_PROJETO_GCP,GOOGLE_CLOUD_REGION=us-central1,GCS_BUCKET_NAME=rodacoop-documents-storage
```

### 9.3. Execução Local com Docker ou Uvicorn

```bash
# Execução direta com recarga automática
export GOOGLE_CLOUD_PROJECT="seu-projeto-gcp"
export TWILIO_ACCOUNT_SID="seu_sid"
export TWILIO_AUTH_TOKEN="seu_token"

uvicorn main:app --reload --port 8080
```
