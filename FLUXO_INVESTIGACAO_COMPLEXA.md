# 🕵️‍♂️ Fluxo de Demonstração Interativo: Investigação em Múltiplos Turnos (Rodacoop + Gemini Agent)

Este guia apresenta um **cenário avançado de resolução de problemas e sinistro fiscal/operacional** em que o agente da Rodacoop no **Gemini Enterprise (GE)** atua como um investigador inteligente. 

Através de **diálogo progressivo em múltiplos turnos**, o operador vai montando o caso junto com o Agente, invocando ferramentas do **Google Cloud ADK**, consultando **Google Cloud Storage (GCS)**, **BigQuery**, **Telemetria IoT** e o **ERP Escalasoft**.

---

## 🎭 Cenário do Problema: Retenção na Barreira Fiscal SEFAZ (Viagem `V-99001`)

**Situação:** O caminhão do motorista **Fernando Alcantara** (placa `ABC9876`), transportando carga de soja da **Fazenda Grão de Ouro**, foi parado e **retido no Posto Fiscal da SEFAZ** em Rio Verde-GO por autuação de **excesso de carga e divergência de MDF-e**. O cooperado João Pedro não sabe por que o veículo foi retido se a nota fiscal foi emitida pelo ERP.

---

## 💬 Roteiro de Prompts Turno-a-Turno no Gemini Enterprise

### 📍 Turno 1: Descoberta e Diagnóstico Inicial do Problema
**Prompt do Usuário:**
> *"Recebi um alerta urgente da SEFAZ! O caminhão da viagem V-99001 com carga de soja foi retido na barreira fiscal de Rio Verde. O motorista Fernando Alcantara disse que a nota fiscal estava emitida. Pode verificar o que está acontecendo no ERP e o motivo do bloqueio?"*

**O que o Agente Executa Internamente (Tool Call):**
* Executa `tool_get_trip_context("V-99001")`.

**Resposta Esperada do Agente:**
> ⚠️ **Alerta de Retenção Fiscal Detectado!**
> 
> * **Viagem:** `V-99001`
> * **Cooperado:** Fazenda Grão de Ouro (João Pedro)
> * **Motorista:** Fernando Alcantara (Veículo `ABC9876`)
> * **Status no ERP Escalasoft:** `RETIDO NA BARREIRA FISCAL SEFAZ`
> * **Motivos Registrados:** 
>   1. Divergência de Peso de Balança (Excesso de Carga).
>   2. Divergência Tributária no Manifesto Eletrônico (SEFAZ/MDF-e).
> 
> **Observação:** O MDF-e foi emitido para 42 toneladas, mas a SEFAZ acusou excesso de peso não declarado. Deseja que eu investigue a telemetria do veículo e os tickets de pesagem da balança de embarque para entender onde ocorreu a divergência?

---

### 📍 Turno 2: Investigação Causal (Cruzando Telemetria IoT + Balança)
**Prompt do Usuário:**
> *"Sim, investigue os logs de pesagem da balança e a telemetria do caminhão. Precisamos entender porque o peso do MDF-e está diferente do peso fiscal retido."*

**O que o Agente Executa Internamente (Tool Call):**
* Executa `tool_check_telemetry_and_scale_logs("V-99001")`.

**Resposta Esperada do Agente:**
> 🔎 **Resultado da Investigação Combinada (Balança + IoT GPS):**
> 
> 1. **Ticket da Balança Eletrônica na Fazenda:** Registrou **48.250 kg** brutos (Carga Líquida: **34.150 kg**).
> 2. **MDF-e N° 458911 no Escalasoft:** Foi emitido automaticamente informando apenas **28.000 kg**.
> 3. **Telemetria GPS:** O veículo realizou uma parada não autorizada de 45 minutos no Armazém Central às 09:15 antes de seguir para a rodovia.
> 
> 💡 **Causa Raiz Identificada:** Ocorreu um erro no faturamento do ERP, gerando a nota com base na estimativa padrão (28 ton) em vez da leitura automática da balança da fazenda. Há um **excesso real de 6,15 toneladas** de soja não declaradas no documento fiscal.
> 
> Deseja que eu simule o cálculo do impacto fiscal (multa SEFAZ + ICMS) para regularização?

---

### 📍 Turno 3: Análise Financeira e Fiscal (Cálculo no BigQuery)
**Prompt do Usuário:**
> *"Perfeito, excelente descoberta! Faça a análise de impacto fiscal e calcule o valor da multa e dos impostos para a liberação da carga."*

**O que o Agente Executa Internamente (Tool Call):**
* Executa `tool_analyze_sefaz_tax_impact("V-99001", excess_weight_tons=6.15)`.

**Resposta Esperada do Agente:**
> 📊 **Análise de Impacto Fiscal e Custos de Regularização (SEFAZ):**
> 
> * 💵 **Multa SEFAZ por Excesso de Carga em MDF-e:** R$ 5.227,50
> * 📄 **ICMS Complementar Diferido (6,15 ton soja):** R$ 1.968,00
> * 💰 **Custo Total para Regularização:** **R$ 7.195,50**
> 
> **Ações Necessárias para Desbloqueio:**
> 1. Recolhimento da DARE (Documento de Arrecadação de Receitas Estaduais).
> 2. Emissão do CT-e Complementar e retificação do MDF-e no ERP Escalasoft.
> 
> Caso a cooperativa autorize o pagamento e informe o código da DARE recolhida, posso gerar os documentos fiscais complementares e solicitar o desbloqueio imediato na barreira.

---

### 📍 Turno 4: Resolução do Problema e Liberação da Viagem
**Prompt do Usuário:**
> *"O pagamento foi autorizado pelo financeiro da Rodacoop. O comprovante da DARE é 'DARE-GO-2026-889123'. Pode emitir o CT-e complementar, atualizar o Escalasoft ERP e liberar a viagem!"*

**O que o Agente Executa Internamente (Tool Call):**
* Executa `tool_issue_complementary_cte_and_release("V-99001", dare_receipt_code="DARE-GO-2026-889123")`.
* Executa `tool_save_to_gcs_and_bigquery("dare_v99001.pdf", "DARE_RECOLHIMENTO", "APROVADO")`.

**Resposta Esperada do Agente:**
> ✅ **Problema Resolvido com Sucesso! Viagem Liberação em Trânsito!**
> 
> 1. 📑 **Comprovante DARE `DARE-GO-2026-889123`** auditado e salvo no **Google Cloud Storage** (`gs://rodacoop-documents-storage/dare/V-99001.pdf`).
> 2. 📝 **CT-e Complementar** e **MDF-e Retificado** transmitidos e autorizados na SEFAZ-GO.
> 3. 🔄 **Sincronização em Tempo Real:** Status atualizado no **Escalasoft ERP** para **`LIBERADO EM TRÂNSITO`**.
> 4. 📊 Evento de auditoria e resolução de sinistro registrado na tabela `rodacoop_analytics.audit_logs` no **BigQuery**.
> 5. 📲 Notificação e novo QR Code de trânsito enviados via WhatsApp ao motorista Fernando Alcantara.

---

## 🎯 Por que este fluxo impressiona em uma Demonstração de IA Generativa?

1. **Raciocínio Investigativo (Multi-Turn Reasoning):** O agente não dá uma resposta pronta; ele orienta a investigação passo a passo conforme o operador faz perguntas.
2. **Orquestração Multi-Sistema:** Integra dados do **ERP (Escalasoft)**, **IoT (Balança/GPS)**, **BigQuery (Cálculo Fiscal)** e **GCS (Auditoria Documental)**.
3. **Resolução de Ponta a Ponta:** O problema começa com um bloqueio fiscal crítico e termina com a liberação automática da frota no Posto Fiscal.
