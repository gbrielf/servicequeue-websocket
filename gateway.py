from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import httpx 
from typing import List

app = FastAPI(title="Gateway de Atendimento")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Lógica do WebSocket ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def serve_html():
    return FileResponse("index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Mantém conexão viva
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/painel")
async def get_painel_info(perfil: str = Query("cliente"), minha_senha: str = Query(None)):  # Padrão é "cliente"
    async with httpx.AsyncClient() as client:
        r_ticket = await client.get("http://localhost:8001/fila")
        ticket_data = r_ticket.json()
        
        pessoas_na_frente = ticket_data["tamanho"]

        if minha_senha and minha_senha in ticket_data["lista_completa"]:
            pessoas_na_frente = ticket_data["lista_completa"].index(minha_senha)

        r_stats = await client.get(f"http://localhost:8002/estatisticas?pessoas_na_frente={pessoas_na_frente}")
        stats_data = r_stats.json()


    links = [
        {"rel": "self", "method": "GET", "href": "http://localhost:8000/painel"},
    ]

    if perfil == "admin":
        if ticket_data["tamanho"] > 0:
            links.append({
                "rel": "chamar_proximo",
                "method": "POST",
                "href": "http://localhost:8000/admin/chamar",
                "title": "Chamar Próxima Senha"
            })
    else:
        if not minha_senha:
            links.append({
                "rel": "pegar_senha",
                "method": "POST",
                "href": "http://localhost:8000/cliente/entrar", 
                "title": "Retirar senha",
            })
        else:
            links.append({"rel": "aguardar", "title": f"Sua senha: {minha_senha}"})
    return {
        "dados": {
            "fila": ticket_data,
            "performance": stats_data,
            "minha_posicao_real": pessoas_na_frente
        },
        "_links": links
        }


@app.post("/cliente/entrar")
async def cliente_pegar_senha():
    # O Gateway recebe o pedido do cliente e repassa para o Service Ticket
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://localhost:8001/entrar")
        
        if resp.status_code != 200:
            return {"erro": "Falha ao gerar senha no serviço interno"}
            
        dados = resp.json()
    
    # Avisa todo mundo (WebSocket) que a fila mudou
    await manager.broadcast("FILA_ATUALIZADA")
    
    return {
        "senha": dados["senha"],
        "posicao": dados["posicao"],
        "_links": [
            {
                "rel": "self",
                "method": "GET",
                "href": f"http://localhost:8000/painel?minha_senha={dados['senha']}",
                "title": "Ver sua posição na fila"
            }
        ]
    }


@app.post("/admin/chamar")
async def chamar_senha():
    # Chama a API de Ticket
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://localhost:8001/chamar")
        
        if resp.status_code != 200:
            return {"erro": "Falha ao chamar próxima senha"}
            
        result = resp.json()
        nova_senha = result["senha"]

    await manager.broadcast(f"SENHA_ATUAL:{nova_senha}")
    await manager.broadcast("FILA_ATUALIZADA")
    
    return {
        "status": "sucesso",
        "senha_chamada": nova_senha,
        "_links": [
            {
                "rel": "painel",
                "method": "GET",
                "href": "http://localhost:8000/painel?perfil=admin",
                "title": "Voltar ao painel admin"
            }
        ]
    }


