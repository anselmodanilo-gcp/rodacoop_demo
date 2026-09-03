# 🎬 Roteiro de Demonstração (Demo Script): Agente Rodacoop no Gemini Agent Platform

Este roteiro guia a apresentação da demo mostrando o fluxo **Event-Driven**, o agente **Multi-Step Cloud ADK**, o armazenamento de mídias no **Google Cloud Storage (GCS)** e o registro de auditoria no **BigQuery Analytics**.

---

## ⚙️ Pré-requisito: Executando o Servidor Localmente

Abra o terminal no diretório do projeto e inicie o servidor com as variáveis do projeto **`demotelemetria`**:

```bash
cd /home/anselmodanilo/dev/rodacoop_demo
source venv/bin/activate
export GOOGLE_CLOUD_PROJECT="demotelemetria"
export GCS_BUCKET_NAME="rodacoop-documents-storage"
export BQ_DATASET="rodacoop_analytics"

# Iniciar aplicação
uvicorn main:app --reload --port 8080
```

---

## 🎭 Cenário da Demonstração

**Situação:** O ERP Escalasoft publica as viagens do dia. A viagem **`VG-2026-9941`** possui pendências de documento para o veículo (CRLV da placa **`BRA2E19`**) e para o motorista (CNH de **`Carlos Eduardo Gomes`**). O **Cooperado Roberto Silva Alcantara** é notificado no WhatsApp para regularizar tudo.

---

## 📍 Etapa 1: Disparo Event-Driven de Sincronização de Viagem (ERP -> WhatsApp)

Simule a notificação enviada do ERP/CRM ao Cooperado via Webhook.

### 💻 Comando Terminal (cURL):
```bash
curl -X POST "http://localhost:8080/webhook/escalasoft/trip-sync?trip_id=VG-2026-9941"
```

### 📩 O que acontece / O que falar no pitch:
> *"Assim que a viagem é gerada no Escalasoft, o webhook consolida as pendências do veículo e do motorista e notifica diretamente o **Cooperado Roberto** via Twilio WhatsApp. O Cooperado é o ponto centralizador da cobrança."*

---

## 📍 Etapa 2: Envio de Documento Válido pelo Cooperado (WhatsApp -> Cloud ADK Agent)

O Cooperado responde no WhatsApp enviando a foto do **CRLV** do veículo **`BRA2E19`**.

### 💻 Comando Terminal (Simulando Webhook do Twilio):
```bash
curl -X POST "http://localhost:8080/webhook/twilio/inbound-message" \
  -d "From=whatsapp%3A%2B5511988887777" \
  -d "NumMedia=1" \
  -d "MediaUrl0=https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" \
  -d "MediaContentType0=application/pdf"
```

### ⚙️ Execução Interna do Agente Cloud ADK (Multi-Step):
1. **Gemini 2.0 Flash:** Identifica que o arquivo é um CRLV.
2. **Tool Call `get_trip_context`:** Busca as informações da viagem `VG-2026-9941` no cadastro.
3. **Tool Call `save_to_gcs_and_bigquery`:** 
   - Salva o arquivo em `gs://rodacoop-documents-storage/uploads/...`
   - Grava o evento de compliance na tabela `rodacoop_analytics.audit_logs` no **BigQuery**.
4. **Tool Call `update_escalasoft_erp`:** Envia um `POST` atualizando o status da viagem para `LIBERADO` no Escalasoft.

### 📱 Resposta Recebida pelo Cooperado no WhatsApp:
```text
✅ *Documento (CRLV) validado com sucesso pelo Agente Cloud ADK!*

• Auditado e armazenado em: Google Cloud Storage (GCS)
• Registrado no BigQuery Analytics
• Cadastro sincronizado com Escalasoft ERP em tempo real.
```

---

## 📍 Etapa 3: Verificação de Analytics no BigQuery

Abra o **Console do Google Cloud** no projeto **`demotelemetria`** e acesse o BigQuery.

### 🔍 Query para Mostrar na Apresentação:
```sql
SELECT 
    event_timestamp,
    doc_type,
    validation_status,
    gcs_uri,
    extracted_details
FROM `demotelemetria.rodacoop_analytics.audit_logs`
ORDER BY event_timestamp DESC;
```

> **Mensagem Chave no Pitch:** *"Todas as interações e decisões do Agente no Gemini Enterprise são auditáveis e geram métricas no BigQuery para dashboards de SLA e compliance em tempo real."*
