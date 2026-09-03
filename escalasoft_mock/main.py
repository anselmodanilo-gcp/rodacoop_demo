import os
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Escalasoft ERP TMS - Mock Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado em memória simulando o banco de dados do ERP
TRIPS = {
    "V-98214": {
        "id": "V-98214",
        "cooperado": "Roberto Silva",
        "motorista": "Carlos Eduardo de Souza",
        "veiculo": "BRA2E19 (Scania R450)",
        "origem": "Rondonópolis - MT",
        "destino": "Porto de Santos - SP",
        "carga": "Soja a Granel (38.5 Ton)",
        "status": "LIBERADO", # Atualizado pelo Agente Gemini
        "status_color": "success",
        "cnh_status": "CONFORME (Validade 2028 / EAR Ativo)",
        "crlv_status": "CONFORME (Licenciamento 2026 OK)",
        "termo_compliance": "ASSINADO (SHA-256 no GCS)",
        "last_updated": "2026-09-03 13:30:00",
        "updated_by": "Agent: rodacoop-compliance-agent (Vertex AI)"
    },
    "V-98215": {
        "id": "V-98215",
        "cooperado": "AgroTrans Logística Ltda",
        "motorista": "Marcos Vinicius Lima",
        "veiculo": "RDC8B30 (Volvo FH 540)",
        "origem": "Sorriso - MT",
        "destino": "Paranaguá - PR",
        "carga": "Milho em Grãos (42.0 Ton)",
        "status": "BLOQUEADO",
        "status_color": "danger",
        "cnh_status": "PENDENTE",
        "crlv_status": "EM ANÁLISE",
        "termo_compliance": "NÃO ASSINADO",
        "last_updated": "2026-09-03 10:15:00",
        "updated_by": "Sistema Automático de Triagem"
    },
    "V-98216": {
        "id": "V-98216",
        "cooperado": "Cooperativa Grãos do Sul",
        "motorista": "José Fernando Ribeiro",
        "veiculo": "FST4C91 (DAF XF)",
        "origem": "Rio Verde - GO",
        "destino": "Santos - SP",
        "carga": "Farelo de Soja (36.0 Ton)",
        "status": "EM AVALIAÇÃO",
        "status_color": "warning",
        "cnh_status": "CONFORME",
        "crlv_status": "PENDENTE REGULARIZAÇÃO SEFAZ",
        "termo_compliance": "PENDENTE",
        "last_updated": "2026-09-03 11:45:00",
        "updated_by": "Escalasoft Bot"
    }
}

class UpdateTripRequest(BaseModel):
    trip_id: str
    doc_type: str = "DOCUMENTO_GERAL"
    status: str = "LIBERADO"
    gcs_uri: str = ""

@app.get("/api/v1/viagens")
def get_trips():
    return list(TRIPS.values())

@app.post("/api/v1/documentos")
def update_trip(req: UpdateTripRequest):
    if req.trip_id in TRIPS:
        TRIPS[req.trip_id]["status"] = req.status
        TRIPS[req.trip_id]["status_color"] = "success" if req.status == "LIBERADO" else "warning"
        TRIPS[req.trip_id]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        TRIPS[req.trip_id]["updated_by"] = f"Agente Google ADK ({req.doc_type})"
        return {"status": "SUCCESS", "message": f"Viagem {req.trip_id} atualizada para {req.status}", "trip": TRIPS[req.trip_id]}
    return JSONResponse(status_code=404, content={"status": "ERROR", "message": "Viagem não encontrada"})

@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Escalasoft ERP TMS - Gestão de Frotas & Compliance</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f1f5f9; color: #1e293b; }
        .sidebar { background: #0f172a; min-height: 100vh; color: #94a3b8; }
        .sidebar .nav-link { color: #94a3b8; font-weight: 500; border-radius: 8px; margin: 4px 12px; }
        .sidebar .nav-link.active, .sidebar .nav-link:hover { color: #fff; background-color: #1e293b; }
        .sidebar .brand { font-weight: 700; color: #38bdf8; font-size: 1.25rem; }
        .card-stat { border: none; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); transition: transform 0.2s; }
        .card-stat:hover { transform: translateY(-2px); }
        .badge-status { font-size: 0.85rem; padding: 6px 12px; border-radius: 20px; font-weight: 600; }
        .badge-liberado { background-color: #dcfce7; color: #15803d; border: 1px solid #86efac; }
        .badge-bloqueado { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
        .badge-avaliacao { background-color: #fef9c3; color: #a16207; border: 1px solid #fde047; }
        .table-custom { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
        .live-pulse {
            display: inline-block; width: 10px; height: 10px; border-radius: 50%;
            background: #22c55e; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
            animation: pulse 1.8s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 p-0 sidebar d-none d-md-block">
                <div class="p-3 border-bottom border-secondary mb-3">
                    <div class="brand"><i class="bi bi-truck-front-fill me-2"></i>ESCALASOFT</div>
                    <small class="text-secondary text-uppercase tracking-wider" style="font-size: 0.7rem;">TMS Transport Management</small>
                </div>
                <ul class="nav flex-column">
                    <li class="nav-item"><a class="nav-link active" href="#"><i class="bi bi-speedometer2 me-2"></i>Painel de Operações</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"><i class="bi bi-shield-check me-2"></i>Compliance & Validação</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"><i class="bi bi-journal-text me-2"></i>Ordens de Carregamento</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"><i class="bi bi-people me-2"></i>Cooperados & Frotas</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"><i class="bi bi-cpu me-2"></i>Google Agent AI (Ativo)</a></li>
                </ul>
                <div class="p-3 mt-5 text-secondary border-top border-secondary small">
                    <div><span class="live-pulse me-2"></span>Gemini Enterprise Agent</div>
                    <div class="text-white mt-1 fw-semibold">Rodacoop Compliance</div>
                    <div style="font-size: 0.75rem;">Status: Conectado (A2A)</div>
                </div>
            </div>

            <!-- Conteúdo Principal -->
            <div class="col-md-10 p-4">
                <!-- Header -->
                <div class="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom">
                    <div>
                        <h3 class="fw-bold mb-1">Módulo TMS & Validação de Viagens</h3>
                        <p class="text-muted mb-0">Integração em tempo real com o Agente de Inteligência Artificial Google Cloud ADK</p>
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-outline-primary btn-sm" onclick="fetchTrips()"><i class="bi bi-arrow-clockwise me-1"></i>Atualizar Dados</button>
                        <span class="badge bg-dark d-flex align-items-center px-3"><i class="bi bi-cloud-check-fill text-info me-2"></i>GCP: demotelemetria</span>
                    </div>
                </div>

                <!-- KPI Cards -->
                <div class="row g-3 mb-4">
                    <div class="col-md-3">
                        <div class="card card-stat p-3 bg-white">
                            <div class="text-muted small fw-semibold">VIAGENS MONITORADAS</div>
                            <div class="h3 fw-bold mt-2 text-dark">3 <small class="text-muted fs-6">ativas</small></div>
                            <span class="text-success small fw-medium"><i class="bi bi-check-circle me-1"></i>Sincronizado Escalasoft</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3 bg-white">
                            <div class="text-muted small fw-semibold">STATUS COMPLIANCE LIBERADO</div>
                            <div class="h3 fw-bold mt-2 text-success">1 <small class="text-muted fs-6">viagem</small></div>
                            <span class="text-success small fw-medium"><i class="bi bi-patch-check-fill me-1"></i>Assinado via SHA-256</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3 bg-white">
                            <div class="text-muted small fw-semibold">BLOQUEADAS / PENDENTES</div>
                            <div class="h3 fw-bold mt-2 text-danger">2 <small class="text-muted fs-6">em triagem</small></div>
                            <span class="text-muted small fw-medium"><i class="bi bi-clock-history me-1"></i>Aguardando documentação</span>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card card-stat p-3 bg-white">
                            <div class="text-muted small fw-semibold">DECISÕES AUTÔNOMAS DO AGENTE</div>
                            <div class="h3 fw-bold mt-2 text-primary">100% <small class="text-muted fs-6">precisão</small></div>
                            <span class="text-primary small fw-medium"><i class="bi bi-robot me-1"></i>Gemini 2.5 Flash</span>
                        </div>
                    </div>
                </div>

                <!-- Tabela de Viagens -->
                <div class="table-custom p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold mb-0">Viagens em Processamento Documental</h5>
                        <small class="text-muted"><i class="bi bi-info-circle me-1"></i>Atualizações feitas via Tool Call pelo Agente Gemini</small>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>CÓDIGO</th>
                                    <th>COOPERADO / MOTORISTA</th>
                                    <th>VEÍCULO & CARGA</th>
                                    <th>ROTA</th>
                                    <th>STATUS DO ERP</th>
                                    <th>AUDITORIA COMPLIANCE</th>
                                    <th>ÚLTIMA AÇÃO</th>
                                </tr>
                            </thead>
                            <tbody id="trips-table-body">
                                <tr><td colspan="7" class="text-center py-4 text-muted">Carregando dados do ERP Escalasoft...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Banner Demonstrativo -->
                <div class="alert alert-primary mt-4 border-0 shadow-sm d-flex align-items-center justify-content-between p-3 rounded-3" style="background-color: #e0f2fe;">
                    <div>
                        <strong class="text-primary"><i class="bi bi-shield-lock-fill me-2"></i>Fluxo Demonstrativo Rodacoop:</strong>
                        <span class="text-secondary small ms-2">Quando o cooperado envia o CRLV/CNH no WhatsApp ou ADK Web, a ferramenta <code>tool_update_escalasoft_erp</code> altera o status da viagem <strong>V-98214</strong> para <strong>LIBERADO</strong> e grava o log no BigQuery.</span>
                    </div>
                    <span class="badge bg-primary px-3 py-2">Pronto para Apresentação</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function fetchTrips() {
            try {
                const res = await fetch('/api/v1/viagens');
                const data = await res.json();
                const tbody = document.getElementById('trips-table-body');
                tbody.innerHTML = '';
                
                data.forEach(trip => {
                    let badgeClass = 'badge-avaliacao';
                    let icon = 'bi-exclamation-circle';
                    if (trip.status === 'LIBERADO') {
                        badgeClass = 'badge-liberado';
                        icon = 'bi-check-circle-fill';
                    } else if (trip.status === 'BLOQUEADO') {
                        badgeClass = 'badge-bloqueado';
                        icon = 'bi-x-circle-fill';
                    }

                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><span class="fw-bold text-primary">${trip.id}</span></td>
                        <td>
                            <div class="fw-semibold">${trip.cooperado}</div>
                            <small class="text-muted"><i class="bi bi-person me-1"></i>${trip.motorista}</small>
                        </td>
                        <td>
                            <div>${trip.veiculo}</div>
                            <small class="text-muted">${trip.carga}</small>
                        </td>
                        <td><small class="fw-medium">${trip.origem} <i class="bi bi-arrow-right text-muted"></i> ${trip.destino}</small></td>
                        <td><span class="badge-status ${badgeClass}"><i class="bi ${icon} me-1"></i>${trip.status}</span></td>
                        <td>
                            <div style="font-size: 0.8rem;"><span class="text-muted">CNH:</span> ${trip.cnh_status}</div>
                            <div style="font-size: 0.8rem;"><span class="text-muted">CRLV:</span> ${trip.crlv_status}</div>
                            <div style="font-size: 0.8rem;"><span class="text-muted">Termo:</span> ${trip.termo_compliance}</div>
                        </td>
                        <td>
                            <div class="small fw-semibold text-dark">${trip.updated_by}</div>
                            <div class="text-muted" style="font-size: 0.75rem;">${trip.last_updated}</div>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (err) {
                console.error('Erro ao carregar viagens:', err);
            }
        }

        // Carregar na inicialização e atualizar a cada 5 segundos
        fetchTrips();
        setInterval(fetchTrips, 5000);
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
