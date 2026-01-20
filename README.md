# Sistema Híbrido TCP + UDP - Sala de Atendimento

## 📊 Descrição

Sistema de atendimento com fila que utiliza **arquitetura híbrida** combinando TCP e UDP:
- **TCP**: Comunicação principal confiável (WebSocket + HTTP)
- **UDP**: Coleta de métricas de baixa latência

## 🔄 Arquitetura de Protocolos

### 🟢 TCP - Comunicação Principal (Confiável)

#### WebSocket (TCP) - Comunicação em Tempo Real
- **Porta**: 8000 (Gateway)
- **Protocolo**: WebSocket sobre TCP
- **Uso**: Atualização em tempo real do painel de senhas
- **Características**:
  - ✅ Conexão persistente bidirecional
  - ✅ Garantia de entrega e ordem dos pacotes
  - ✅ Handshake TCP inicial
  - ✅ Ideal para dados críticos que não podem ser perdidos

**Implementação no Gateway:**
```python
# gateway.py - WebSocket sobre TCP
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)  # Handshake TCP
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

#### HTTP/REST (TCP) - APIs dos Serviços
- **Portas**: 8001 (Tickets), 8002 (Stats), 8000 (Gateway)
- **Protocolo**: HTTP sobre TCP
- **Uso**: Operações CRUD e consultas críticas
- **Características**:
  - ✅ Request/Response confiável
  - ✅ Garantia de entrega
  - ✅ Stateless (cada requisição independente)
  - ✅ Retries automáticos em caso de falha

**Endpoints TCP:**
- `POST /entrar` - Gerar nova senha (crítico)
- `POST /chamar` - Chamar próxima senha (crítico)
- `GET /fila` - Consultar fila (crítico)
- `GET /estatisticas` - Calcular tempo de espera (crítico)
- `GET /painel` - Dados consolidados do painel (crítico)

### 🔵 UDP - Métricas e Monitoramento (Performance)

#### UDP Socket - Coleta de Métricas
- **Porta**: 9999 (Servidor de Métricas)
- **Protocolo**: UDP Datagram
- **Uso**: Envio de métricas e logs não críticos
- **Características**:
  - ✅ Sem overhead de conexão (fire-and-forget)
  - ✅ Baixa latência
  - ✅ Não bloqueia operações principais
  - ⚠️ Sem garantia de entrega (aceitável para métricas)

**Implementação do Cliente UDP:**
```python
# udp_client.py - Envio de métricas via UDP
def send_metric(self, event: str, data: dict, source: str):
    metric = {'event': event, 'data': data, 'source': source}
    message = json.dumps(metric).encode('utf-8')
    self.sock.sendto(message, (self.server_host, self.server_port))
    # Fire-and-forget: não espera confirmação
```

## 🎯 Métricas Coletadas via UDP

### Service Ticket (Porta 8001)
- **senha_gerada**: Quando um cliente pega uma nova senha
  - Dados: senha, posição, tamanho_fila
- **senha_chamada**: Quando uma senha é chamada para atendimento
  - Dados: senha, fila_restante

### Service Stats (Porta 8002)
- **consulta_estatisticas**: Quando alguém consulta tempo de espera
  - Dados: pessoas_na_frente, tempo_estimado_minutos

### Gateway (Porta 8000)
- **websocket_conectado**: Nova conexão WebSocket estabelecida
  - Dados: total_conexoes
- **websocket_desconectado**: Conexão WebSocket encerrada
  - Dados: total_conexoes

## 🚀 Como Executar

### 1. Iniciar o Servidor de Métricas UDP (Terminal 1)
```powershell
python udp_metrics_server.py
```

O servidor UDP iniciará na porta **9999** e começará a exibir métricas em tempo real.

### 2. Iniciar os Serviços HTTP/TCP (Terminais separados)

**Service Ticket - HTTP sobre TCP (Terminal 2):**
```powershell
uvicorn service_ticket:app --host 0.0.0.0 --port 8001 --reload
```

**Service Stats - HTTP sobre TCP (Terminal 3):**
```powershell
uvicorn service_stats:app --host 0.0.0.0 --port 8002 --reload
```

**Gateway - WebSocket sobre TCP (Terminal 4):**
```powershell
uvicorn gateway:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Testar o Sistema

Abra o navegador em `http://localhost:8000` e use o sistema normalmente.

**Fluxo de dados:**
1. 🌐 Navegador conecta via **WebSocket (TCP)** ao Gateway
2. 🔄 Gateway faz requisições **HTTP (TCP)** aos serviços
3. 📊 Serviços enviam métricas via **UDP** ao servidor de métricas
4. 📡 Gateway propaga atualizações via **WebSocket (TCP)** aos clientes

## 📈 Visualização das Métricas

O servidor UDP exibe:
- ✅ Eventos em **tempo real** conforme acontecem
- 📊 **Estatísticas consolidadas** a cada 30 segundos
- 📋 Últimos 10 eventos recentes

### Exemplo de saída:
```
[14:32:15] 📨 SENHA_GERADA - service_ticket
         └─ senha: A15
         └─ posicao: 6
         └─ tamanho_fila: 6

[14:32:18] 📨 WEBSOCKET_CONECTADO - gateway
         └─ total_conexoes: 2

[14:32:25] 📨 SENHA_CHAMADA - service_ticket
         └─ senha: A10
         └─ fila_restante: 5
```

## 🆚 TCP vs UDP - Quando usar cada um?

### ✅ Use TCP quando:
- Dados **críticos** que não podem ser perdidos
- Ordem dos pacotes é importante
- Precisa de confirmação de entrega
- **Exemplos neste projeto**: 
  - Gerar/chamar senhas
  - Consultar fila
  - WebSocket para updates em tempo real

### ✅ Use UDP quando:
- Performance é mais importante que confiabilidade
- Dados podem ser perdidos ocasionalmente
- Baixa latência é crítica
- Fire-and-forget é aceitável
- **Exemplos neste projeto**:
  - Envio de métricas
  - Logs não críticos
  - Estatísticas de uso

## 🔧 Comparação Técnica

| Característica | TCP (WebSocket/HTTP) | UDP (Métricas) |
|----------------|----------------------|----------------|
| **Conexão** | Orientado à conexão | Sem conexão |
| **Confiabilidade** | Garantia de entrega | Sem garantia |
| **Ordem** | Mantém ordem | Pode chegar fora de ordem |
| **Overhead** | Alto (handshake, ACKs) | Baixo (direto) |
| **Velocidade** | Mais lento | Mais rápido |
| **Uso no projeto** | Operações críticas | Métricas/logs |
| **Portas** | 8000, 8001, 8002 | 9999 |

## 📁 Arquivos do Projeto

### Comunicação TCP (Principal):
- `gateway.py` - Gateway WebSocket (TCP) + HTTP requests
- `service_ticket.py` - API REST HTTP (TCP) para senhas
- `service_stats.py` - API REST HTTP (TCP) para estatísticas
- `index.html` - Frontend com WebSocket (TCP)

### Comunicação UDP (Métricas):
- `udp_metrics_server.py` - Servidor UDP que coleta métricas
- `udp_client.py` - Cliente UDP reutilizável

## 🎓 Conceitos Demonstrados

### TCP:
- **WebSocket Programming** - Conexão persistente full-duplex
- **HTTP REST APIs** - Stateless request/response
- **Connection-oriented communication** - Handshake e estado
- **Reliable data transfer** - Retransmissão automática

### UDP:
- **UDP Socket Programming** - Datagram sockets
- **Fire-and-forget messaging** - Envio sem confirmação
- **Connectionless communication** - Sem handshake
- **Non-blocking I/O** - Timeout configurável

### Arquitetura:
- **Hybrid protocol design** - TCP + UDP complementares
- **Metrics collection** - Monitoramento sem impacto
- **Separation of concerns** - Serviço vs monitoramento
- **Microservices pattern** - Serviços independentes

## 🌐 Diagrama de Comunicação

```
┌─────────────┐
│  Navegador  │
└──────┬──────┘
       │ WebSocket (TCP:8000)
       ↓
┌──────────────────┐
│     Gateway      │────UDP:9999───→ ┌────────────────┐
└────────┬─────────┘                  │ UDP Metrics    │
         │ HTTP (TCP)                 │    Server      │
         ├──→ service_ticket:8001─────┤                │
         │        (TCP)               │  (Porta 9999)  │
         └──→ service_stats:8002──────┤                │
                  (TCP)               └────────────────┘
                                             ↑
                                             │
                              Todas as métricas via UDP
```

## 💡 Vantagens da Arquitetura Híbrida

1. **Confiabilidade + Performance**: TCP garante dados críticos, UDP otimiza métricas
2. **Resiliência**: Falha no sistema de métricas não afeta operações principais
3. **Escalabilidade**: Métricas UDP não sobrecarregam serviços
4. **Monitoramento Real**: Visibilidade completa sem degradação
5. **Aprendizado**: Demonstra uso prático de ambos protocolos
