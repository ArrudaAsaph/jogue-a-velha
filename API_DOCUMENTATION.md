# 📚 Documentação da API Gateway - Jogo da Velha

## 🌐 Informações Gerais

- **Base URL:** `http://localhost:8000`
- **Protocolo:** HTTP/1.1
- **Formato de dados:** JSON
- **CORS:** Habilitado para todas as origens
- **HATEOAS:** Implementado em todas as respostas

---

## 📡 Endpoints

### 1. Criar Sala

Cria uma nova sala de jogo via SOAP API e retorna o ID com links HATEOAS.

**Endpoint:** `POST /criar-sala`

**Request:**
```json
{
  "porta": "8080"
}
```

**Response (200 OK):**
```json
{
  "msg": "Sala criada com sucesso",
  "room_id": "a89a87f8-5dc6-44f7-94a9-19926b5e7253",
  "_links": {
    "entrar_sala": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/entrar",
    "consultar_sala": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253",
    "jogar": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/jogar"
  }
}
```

**Exemplo curl:**
```bash
curl -X POST http://localhost:8000/criar-sala \
  -H "Content-Type: application/json" \
  -d '{"porta":"8080"}'
```

---

### 2. Entrar na Sala

Permite que um jogador entre em uma sala existente.

**Endpoint:** `POST /salas/{sala_id}/entrar`

**Request:**
```json
{
  "jogador": "Player1"
}
```

**Response (200 OK):**
```json
{
  "msg": "Jogador Player1 entrou como X",
  "sala": {
    "id": "a89a87f8-5dc6-44f7-94a9-19926b5e7253",
    "ip": "127.0.0.1",
    "porta": "8080",
    "jogadores": ["X"],
    "tabuleiro": ["","","","","","","","",""],
    "vez": "X",
    "nomes": {
      "X": "Player1"
    }
  },
  "_links": {
    "jogar": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/jogar",
    "consultar_sala": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253"
  }
}
```

**Exemplo curl:**
```bash
curl -X POST http://localhost:8000/salas/SALA_ID/entrar \
  -H "Content-Type: application/json" \
  -d '{"jogador":"Player1"}'
```

**Erros possíveis:**
- `400` - Jogador não informado
- `404` - Sala não encontrada
- `400` - Sala já está cheia (2 jogadores)

---

### 3. Fazer Jogada

Registra uma jogada no tabuleiro.

**Endpoint:** `POST /salas/{sala_id}/jogar`

**Request:**
```json
{
  "jogador": "Player1",
  "pos": 4
}
```

**Parâmetros:**
- `jogador` - Nome do jogador
- `pos` - Posição no tabuleiro (0 a 8)

**Layout do tabuleiro:**
```
0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8
```

**Response (200 OK):**
```json
{
  "msg": "Jogada registrada",
  "sala": {
    "id": "a89a87f8-5dc6-44f7-94a9-19926b5e7253",
    "tabuleiro": ["","","","","X","","","",""],
    "vez": "O",
    "jogadores": ["X", "O"],
    "nomes": {
      "X": "Player1",
      "O": "Player2"
    }
  },
  "_links": {
    "consultar_sala": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253"
  }
}
```

**Response em caso de vitória:**
```json
{
  "msg": "Jogador Player1 venceu!",
  "sala": {
    "id": "...",
    "vencedor": "X",
    "tabuleiro": ["X","X","X","O","O","","","",""]
  },
  "_links": {
    "consultar_sala": "/salas/..."
  }
}
```

**Exemplo curl:**
```bash
curl -X POST http://localhost:8000/salas/SALA_ID/jogar \
  -H "Content-Type: application/json" \
  -d '{"jogador":"Player1","pos":4}'
```

**Erros possíveis:**
- `400` - Jogador ou posição não informados
- `404` - Sala não encontrada
- `400` - Não é a vez do jogador
- `400` - Posição já ocupada
- `400` - Posição inválida (fora de 0-8)

---

### 4. Consultar Sala

Retorna o estado atual da sala.

**Endpoint:** `GET /salas/{sala_id}`

**Response (200 OK):**
```json
{
  "id": "a89a87f8-5dc6-44f7-94a9-19926b5e7253",
  "ip": "127.0.0.1",
  "porta": "8080",
  "jogadores": ["X", "O"],
  "tabuleiro": ["X","","","O","X","","","",""],
  "vez": "O",
  "nomes": {
    "X": "Player1",
    "O": "Player2"
  },
  "_links": {
    "entrar_sala": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/entrar",
    "jogar": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/jogar",
    "reiniciar": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/reiniciar"
  }
}
```

**Exemplo curl:**
```bash
curl http://localhost:8000/salas/SALA_ID
```

**Erros possíveis:**
- `404` - Sala não encontrada

---

### 5. Reiniciar Jogo

Reinicia o jogo mantendo os mesmos jogadores.

**Endpoint:** `POST /salas/{sala_id}/reiniciar`

**Request:** `{}` (corpo vazio)

**Response (200 OK):**
```json
{
  "msg": "Jogo reiniciado!",
  "sala": {
    "id": "a89a87f8-5dc6-44f7-94a9-19926b5e7253",
    "jogadores": ["X", "O"],
    "tabuleiro": ["","","","","","","","",""],
    "vez": "X",
    "nomes": {
      "X": "Player1",
      "O": "Player2"
    }
  },
  "_links": {
    "jogar": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/jogar",
    "consultar_sala": "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253"
  }
}
```

**Exemplo curl:**
```bash
curl -X POST http://localhost:8000/salas/SALA_ID/reiniciar \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 🔗 HATEOAS

Todas as respostas incluem o campo `_links` com hipermídia, seguindo o princípio HATEOAS (Hypermedia as the Engine of Application State).

**Benefícios:**
- ✅ Cliente descobre ações disponíveis dinamicamente
- ✅ Reduz acoplamento entre cliente e servidor
- ✅ API auto-documentada
- ✅ Facilita evolução da API

**Exemplo de navegação:**
1. `POST /criar-sala` → recebe links para `entrar`, `consultar`, `jogar`
2. Usa link `entrar_sala` → recebe links para `jogar`, `consultar`
3. Usa link `jogar` → recebe link para `consultar`

---

## 🏗️ Arquitetura

```
Cliente Web (Angular)
        │
        │ HTTP/JSON
        ▼
┌───────────────────┐
│   API Gateway     │  ← Este documento
│   (Flask + CORS)  │
│   + HATEOAS       │
└─────────┬─────────┘
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
┌────────┐  ┌────────┐
│  SOAP  │  │  REST  │
│  API   │  │  API   │
└────────┘  └────────┘
    │            │
    └─────┬──────┘
          ▼
      ┌───────┐
      │ Redis │
      └───────┘
```

---

## 🧪 Testando a API

### Fluxo completo de um jogo:

```bash
# 1. Criar sala
curl -X POST http://localhost:8000/criar-sala \
  -H "Content-Type: application/json" \
  -d '{"porta":"8080"}'
# Anote o room_id retornado

# 2. Jogador 1 entra
curl -X POST http://localhost:8000/salas/ROOM_ID/entrar \
  -H "Content-Type: application/json" \
  -d '{"jogador":"Alice"}'

# 3. Jogador 2 entra
curl -X POST http://localhost:8000/salas/ROOM_ID/entrar \
  -H "Content-Type: application/json" \
  -d '{"jogador":"Bob"}'

# 4. Alice joga (X)
curl -X POST http://localhost:8000/salas/ROOM_ID/jogar \
  -H "Content-Type: application/json" \
  -d '{"jogador":"Alice","pos":0}'

# 5. Bob joga (O)
curl -X POST http://localhost:8000/salas/ROOM_ID/jogar \
  -H "Content-Type: application/json" \
  -d '{"jogador":"Bob","pos":4}'

# 6. Consultar estado
curl http://localhost:8000/salas/ROOM_ID
```

---

## 📝 Notas Técnicas

- **CORS:** Habilitado para permitir acesso do frontend
- **Persistência:** Dados armazenados em Redis
- **Validações:** Todas as entradas são validadas
- **Erros:** Retornam JSON com campo `erro`
- **Stateless:** Gateway não mantém estado, apenas roteia
- **Docker:** Todos os serviços rodam em containers

---

## 🔐 Segurança

**Ambiente de Desenvolvimento:**
- Sem autenticação (para fins didáticos)
- CORS aberto para todas as origens
- Sem rate limiting

**Para Produção, adicionar:**
- Autenticação (JWT, OAuth)
- Rate limiting
- HTTPS/TLS
- Validação de input mais rigorosa
- Logs de auditoria
