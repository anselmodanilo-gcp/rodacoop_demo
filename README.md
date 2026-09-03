# 🚛 Agente de Compliance Documental Rodacoop (Google Cloud Agent Runtime)

Demonstração prática de um **Agente Autônomo de Inteligência Artificial para Compliance Documental e Logística**, desenvolvido com o ecossistema oficial **Google Cloud ADK (Agent Development Kit)**, **Google Agents CLI (`agents-cli`)** e **Gemini 2.5 Flash** na Vertex AI.

![Arquitetura da Solução](arquitetura_diagrama.png)

---

## 🎯 Objetivo da Solução

Automatizar a jornada de validação e liberação de viagens rodoviárias para cooperados e motoristas de transporte de cargas (grãos/agronegócio):
- **Zero Hardcode de Políticas:** O agente consulta regulamentos e normas de transporte diretamente de um repositório centralizado no **Google Cloud Storage (GCS)** em texto puro.
- **Validação Inteligente Multimodal:** Extração e conferência de CNH (categoria, validade e EAR), CRLV (exercício e chassi) e certificados ANTT/RNTRC.
- **Assinatura e Integridade 100% Nativa:** Geração de Termo Digital de Compliance assinado via Hash SHA-256 no GCS, sem custos de ferramentas terceiras.
- **Auditoria Corporativa em Tempo Real:** Registro estruturado de eventos e dados extraídos no **Google BigQuery** para dashboards executivos e governança.
- **Integração de Missão Crítica:** Liberação imediata de cadastros e viagens no **ERP Escalasoft**.

---

## 🏛️ Arquitetura e Tecnologias

| Camada | Tecnologia / Serviço | Papel na Solução |
| :--- | :--- | :--- |
| **Hospedagem & Runtime** | **Google Cloud Agent Runtime** (Reasoning Engines) | Execução serverless gerenciada com escalabilidade de 0 a 10 instâncias e suporte A2A. |
| **Ciclo de Vida (ADLC)** | **Google Agents CLI (`agents-cli`)** | Scaffolding enterprise, manifestos de deploy e automação de entrega contínua. |
| **Cérebro de IA** | **Gemini 2.5 Flash** (Vertex AI) | Modelo multimodal estável para raciocínio, Function Calling e extração documental. |
| **Armazenamento de Políticas** | **Google Cloud Storage (GCS)** | Repositório de texto das regras de compliance e cofre de termos assinados (SHA-256). |
| **Auditoria & Analytics** | **Google BigQuery** | Dataset `rodacoop_analytics` com tabela `audit_logs` para governança de decisões. |
| **Observabilidade Enterprise** | **OpenTelemetry & Cloud Trace** | Telemetria nativa ativada (`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`). |
| **Sistemas Legados** | **Escalasoft ERP** | Atualização do status cadastral e liberação operacional da viagem. |

Para mais detalhes, consulte a especificação técnica completa em [ARQUITETURA.md](ARQUITETURA.md).

---

## 📂 Estrutura do Repositório

```text
├── app/                           # Código do Agente e utilitários para Agent Runtime
│   ├── agent.py                   # Definição oficial do root_agent e tools no Google ADK
│   ├── fast_api_app.py            # Servidor FastAPI com webhook e A2A protocol
│   └── dashboard.py               # Dashboard de métricas e acompanhamento
├── adk_agents/rodacoop_agent/     # Workspace ADK para desenvolvimento local e testes
├── politica_compliance_transporte.txt # Políticas oficiais sincronizadas com o Cloud Storage
├── agents-cli-manifest.yaml       # Manifesto de governança do google-agents-cli
├── deployment_metadata.json       # Metadados do Agent Runtime implantado na GCP
├── pyproject.toml                 # Dependências e empacotamento do projeto
├── DEMO_SCRIPT.md                 # Roteiro passo a passo para apresentação da demo
├── ARQUITETURA.md                 # Especificação técnica completa de arquitetura
└── arquitetura_diagrama.png       # Diagrama visual de alta fidelidade
```

---

## 🚀 Como Executar Localmente

### 1. Pré-requisitos
- Python 3.10+
- Google Cloud CLI (`gcloud`) autenticado com permissões na Vertex AI
- Gerenciador de pacotes `uv` ou `pip`

### 2. Configurar o Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Iniciar a Interface Local do ADK Web
```bash
adk web --default_llm_model gemini-2.5-flash --port 8000 adk_agents/rodacoop_agent
```
Acesse `http://localhost:8000` para interagir com o agente no playground local.

---

## ☁️ Deploy no Google Cloud Agent Runtime

O projeto foi empacotado para o padrão oficial da Google com o `agents-cli`:

```bash
# Testar os parâmetros de deployment (dry-run)
uv tool run google-agents-cli deploy --dry-run --project demotelemetria --region us-central1

# Realizar o deploy no Google Cloud Agent Runtime
uv tool run google-agents-cli deploy --project demotelemetria --region us-central1
```

O runtime gera automaticamente:
- **Agent Card A2A:** `https://us-central1-aiplatform.googleapis.com/.../agent-card.json`
- **Dashboard no Console Vertex AI:** Acompanhamento de instâncias, logs e traces distribuídos.

---

## 📊 Consulta de Auditoria no BigQuery

Cada interação de validação pode ser auditada diretamente via SQL:

```sql
SELECT 
    event_timestamp,
    trip_id,
    cooperado_nome,
    doc_type,
    validation_status,
    gcs_uri,
    extracted_details
FROM `demotelemetria.rodacoop_analytics.audit_logs`
ORDER BY event_timestamp DESC;
```

---

## 🔒 Segurança e Privacidade
Este projeto foi desenvolvido estritamente para cenários de demonstração e homologação técnica. Todas as credenciais, domínios e nomes utilizados respeitam regras de privacidade, dados sintéticos e boas práticas de proteção de infraestrutura em nuvem.
