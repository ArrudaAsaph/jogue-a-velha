# 🎮 Jogo da Velha - Sistema Distribuído

Sistema de Jogo da Velha desenvolvido com arquitetura distribuída, utilizando serviços SOAP, REST e Gateway com HATEOAS, e frontend em Angular.

## 🏗️ Arquitetura

- **SOAP API** (porta 8001): Serviço para criação de salas
- **REST API** (porta 5000): Serviço para gerenciamento de jogadas
- **Gateway** (porta 8000): API Gateway com suporte a HATEOAS
- **Frontend** (porta 4200): Interface Angular com TailwindCSS e PrimeNG
- **Redis**: Banco de dados em memória para armazenar estado das salas

## 🚀 Quick Start

```bash
# 1. Iniciar serviços backend
docker-compose up -d

# 2. Iniciar frontend
cd frontend
npm install
npm start
```

Acesse: http://localhost:4200

## 📚 Documentação Completa

| Documento | Descrição |
|-----------|-----------|
| [REQUISITOS.md](./REQUISITOS.md) | ✅ Verificação de todos os requisitos do projeto |
| [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) | 📡 Documentação completa da API Gateway |
| [WSDL_ANALYSIS.md](./WSDL_ANALYSIS.md) | 📄 Análise detalhada do WSDL gerado |
| [VERIFICACAO.md](./VERIFICACAO.md) | 🔍 Resumo de implementação e testes |
| [frontend/FRONTEND.md](./frontend/FRONTEND.md) | 🎨 Documentação do cliente web |

## ✅ Verificação dos Serviços

Os serviços estão funcionando corretamente:
- ✅ SOAP API - Criação de salas funcionando
- ✅ REST API - Entrada em sala e jogadas funcionando
- ✅ Gateway - HATEOAS implementado com sucesso
- ✅ Frontend - Interface completa e responsiva

## 🎯 Funcionalidades

- Criar salas de jogo
- Entrar em salas via ID
- Jogar em tempo real com atualização automática
- Detecção de vitória e empate
- Interface moderna com TailwindCSS e PrimeNG
- Compartilhamento de sala via ID

## 📦 Tecnologias

**Backend:** Python, Flask, Spyne, Redis, Docker
**Frontend:** Angular 20, TypeScript, TailwindCSS, PrimeNG
Jogue a Velha é um jogo da velha online e em tempo real, onde você pode criar salas, convidar amigos e jogar partidas diretamente pelo navegador. O sistema foi desenvolvido com foco em comunicação distribuída e sincronização instantânea entre jogadores, utilizando Node.js, Express e Socket.IO.


# 🧼 SOAP API – Jogo da Velha
Serviço SOAP em Python utilizando Spyne e Redis para armazenamento do estado do jogo.
Todo o ambiente é preparado via Docker + Docker Compose.

---

## 📌 Funcionalidade

Este serviço expõe um endpoint SOAP responsável por:

- Criar novas salas de jogo
- Persistir estado no Redis
- Retornar o ID único da sala criada

A estrutura de cada sala no Redis é:

```json
{
  "id": "uuid",
  "ip": "127.0.0.1",
  "porta": "8000",
  "jogadores": [],
  "tabuleiro": ["", "", "", "", "", "", "", "", ""],
  "vez": "X"
}
```

---
## 📂 Estrutura do Projeto
```json
jogue-a-velha/
├── docker-compose.yml
└── soap/
     ├── main.py
     ├── requirements.txt
     └── dockerfile

```

---
## 🐳 Docker Compose

O ambiente possui dois serviços:

* soap_api → API SOAP rodando na porta 8001

* redis_jogo → Banco Redis rodando na porta 6379

---

## ▶️ Como executar

Na raiz do projeto (onde está o docker-compose.yml):
```bash
docker-compose up --build
```
A API ficará disponível em:

```bash
http://localhost:8001
```

E o Redis interno em:

```bash
docker exec -it redis_jogo redis-cli
```

---
## 📡 Endpoint SOAP

URL do endpoint:

http://localhost:8001/

---

## 🧪 Exemplo de requisição SOAP (criar sala)

Request

```bash
<?xml version="1.0"?>
<soapenv:Envelope
  xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:tns="http://jogovelha.com/soap">
  <soapenv:Body>
      <tns:criarSala>
          <porta>8080</porta>
      </tns:criarSala>
  </soapenv:Body>
</soapenv:Envelope>

```
cUrl

```bash
curl -X POST http://127.0.0.1:8001 \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
  <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                    xmlns:ser="http://jogovelha.com/soap">
     <soapenv:Body>
        <ser:criarSala>
           <ser:porta>8080</ser:porta>
        </ser:criarSala>
     </soapenv:Body>
  </soapenv:Envelope>'

```

Response
```bash
<?xml version='1.0' encoding='UTF-8'?>
<soap11env:Envelope xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="http://jogovelha.com/soap">
  <soap11env:Body>
    <tns:criarSalaResponse>
      <tns:criarSalaResult>e6317e9c-5947-4743-ab78-c864843eab5c</tns:criarSalaResult>
    </tns:criarSalaResponse>
  </soap11env:Body>
</soap11env:Envelope>
```
