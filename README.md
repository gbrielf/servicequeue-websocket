# Sistema Distribuído de Atendimento em Tempo Real

## 📋 Visão Geral

Sistema de gerenciamento de filas de atendimento desenvolvido com arquitetura distribuída baseada em microsserviços.

A aplicação utiliza diferentes mecanismos de comunicação para atender necessidades específicas:

* **HTTP/REST** para operações de negócio entre serviços.
* **WebSockets** para atualização em tempo real dos clientes conectados.
* **UDP** para coleta de métricas e monitoramento desacoplado.

O objetivo é demonstrar conceitos de comunicação cliente-servidor, integração entre serviços, monitoramento de aplicações e atualização em tempo real.

---

# 🏗️ Arquitetura

```text
┌─────────────┐
│ Navegador   │
└──────┬──────┘
       │ WebSocket + HTTP
       ▼
┌──────────────────┐
│     Gateway      │
│   FastAPI        │
└────────┬─────────┘
         │ HTTP
         ├──────────────► Service Ticket
         │                 (Fila de senhas)
         │
         └──────────────► Service Stats
                           (Tempo de espera)

Todos os serviços enviam métricas via UDP

         ┌──────────────────┐
         │ Metrics Server   │
         │ UDP Collector    │
         └──────────────────┘
```

---

# 🚀 Principais Funcionalidades

### Gestão de Fila

* Geração automática de senhas.
* Controle da fila de atendimento.
* Chamada da próxima senha.
* Consulta da posição na fila.

### Atualização em Tempo Real

* Comunicação bidirecional via WebSocket.
* Atualização automática dos painéis conectados.
* Notificação imediata de alterações na fila.

### Monitoramento

* Coleta de eventos do sistema via UDP.
* Registro de conexões WebSocket.
* Registro de geração e chamada de senhas.
* Consolidação de estatísticas operacionais.

### Integração entre Serviços

* Gateway centralizando o acesso aos serviços.
* Comunicação assíncrona entre APIs utilizando HTTP.
* Separação de responsabilidades entre componentes.

---

# 🔧 Tecnologias Utilizadas

### Backend

* Python
* FastAPI
* Uvicorn
* HTTPX

### Comunicação

* HTTP/REST
* WebSockets
* UDP

### Frontend

* HTML5
* JavaScript
* Tailwind CSS

### Arquitetura

* Microsserviços
* Cliente/Servidor
* Gateway Pattern
* Comunicação Assíncrona

---

# 📦 Componentes do Sistema

## Gateway

Responsável por:

* Servir a interface web.
* Gerenciar conexões WebSocket.
* Integrar os serviços internos.
* Consolidar informações para o painel.

### Endpoints

```http
GET /
GET /painel
POST /cliente/entrar
POST /admin/chamar
WS /ws
```

---

## Service Ticket

Serviço responsável pelo gerenciamento da fila.

### Endpoints

```http
GET /fila
POST /entrar
POST /chamar
```

### Responsabilidades

* Gerar novas senhas.
* Manter estado da fila.
* Controlar senha atualmente em atendimento.

---

## Service Stats

Serviço responsável pelo cálculo de estatísticas operacionais.

### Endpoint

```http
GET /estatisticas
```

### Responsabilidades

* Calcular tempo estimado de espera.
* Fornecer métricas de atendimento.

---

## Metrics Server

Servidor UDP dedicado ao monitoramento do sistema.

### Eventos Monitorados

#### Service Ticket

* senha_gerada
* senha_chamada

#### Gateway

* websocket_conectado
* websocket_desconectado

#### Service Stats

* consulta_estatisticas

---

# 📡 Comunicação Utilizada

## HTTP/REST

Utilizado para integração entre serviços e execução das operações de negócio.

Exemplos:

* Gerar senha
* Chamar próximo atendimento
* Consultar fila
* Consultar estatísticas

---

## WebSocket

Utilizado para atualização em tempo real dos clientes conectados.

Eventos enviados:

```text
FILA_ATUALIZADA

SENHA_ATUAL:A15
```

Benefícios:

* Comunicação bidirecional.
* Atualizações instantâneas.
* Redução de polling constante.

---

## UDP

Utilizado para envio de métricas e monitoramento.

Características:

* Baixo overhead.
* Não bloqueia operações principais.
* Adequado para eventos não críticos.

Exemplo de métrica:

```json
{
  "event": "senha_gerada",
  "source": "service_ticket",
  "data": {
    "senha": "A15",
    "posicao": 6
  }
}
```

---

# 🎯 Conceitos Demonstrados

Este projeto demonstra na prática:

* Arquitetura Cliente/Servidor
* Comunicação HTTP entre serviços
* WebSockets para comunicação em tempo real
* Monitoramento via UDP
* Microsserviços
* Gateway Pattern
* Comunicação Assíncrona
* Integração entre APIs
* Monitoramento de aplicações
* Separação de responsabilidades
* Desenvolvimento de sistemas distribuídos

---

# 💡 Objetivo Acadêmico

O projeto foi desenvolvido com foco no estudo de:

* Comunicação em redes de computadores.
* Protocolos de aplicação.
* Sistemas distribuídos.
* Arquitetura de software.
* Integração entre serviços.
* Monitoramento de aplicações em tempo real.
