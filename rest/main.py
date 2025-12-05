from flask import Flask, request, jsonify
from flasgger import Swagger
import redis
import json
import time
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Jogo da Velha - REST API",
        "description": "API REST para gerenciar jogadas e estado das salas com WebSocket",
        "version": "2.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
}

Swagger(app, config=swagger_config, template=swagger_template)

r = redis.Redis(host="redis", port=6379, decode_responses=True, socket_connect_timeout=5)

WEBSOCKET_CHANNEL = "jogo_velha_events"

def carregar_sala(sala_id):
    """Carrega uma sala do Redis"""
    try:
        data = r.get(f"sala:{sala_id}")
        if not data:
            return None
        return json.loads(data)
    except Exception as e:
        logger.error(f"Erro ao carregar sala {sala_id}: {str(e)}")
        return None

def salvar_sala(sala):
    """Salva uma sala no Redis"""
    try:
        r.set(f"sala:{sala['id']}", json.dumps(sala))
        logger.debug(f"Sala {sala['id']} salva no Redis")
    except Exception as e:
        logger.error(f"Erro ao salvar sala {sala['id']}: {str(e)}")
        raise

def publicar_evento_websocket(evento, sala_id, dados=None):
    """
    Publica um evento no Redis para o WebSocket notificar os clientes

    Args:
        evento: Tipo do evento (ex: "jogador_entrou", "jogada_realizada")
        sala_id: ID da sala
        dados: Dados adicionais do evento
    """
    try:
        mensagem = {
            "evento": evento,
            "sala_id": sala_id,
            "dados": dados or {},
            "timestamp": time.time()
        }

        r.publish(WEBSOCKET_CHANNEL, json.dumps(mensagem))
        logger.info(f"📢 Evento publicado: {evento} na sala {sala_id}")

    except Exception as e:
        logger.error(f"❌ Erro ao publicar evento WebSocket: {str(e)}")

def verificar_vitoria(tabuleiro):
    """Verifica se há um vencedor no tabuleiro"""
    combinacoes = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Linhas
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Colunas
        [0, 4, 8], [2, 4, 6]              # Diagonais
    ]

    for a, b, c in combinacoes:
        if tabuleiro[a] and tabuleiro[a] == tabuleiro[b] == tabuleiro[c]:
            return tabuleiro[a]
    return None

def verificar_empate(tabuleiro):
    """Verifica se o jogo terminou em empate"""
    return "" not in tabuleiro and not verificar_vitoria(tabuleiro)

@app.route("/salas/<sala_id>/entrar", methods=["POST"])
def entrar_sala(sala_id):
    """
    Entrar em uma sala existente
    ---
    tags:
      - Salas
    parameters:
      - name: sala_id
        in: path
        type: string
        required: true
        description: ID da sala
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - jogador
          properties:
            jogador:
              type: string
              example: "Player1"
              description: Nome do jogador
    responses:
      200:
        description: Jogador entrou na sala com sucesso
        schema:
          type: object
          properties:
            msg:
              type: string
            sala:
              type: object
      400:
        description: Jogador não informado
      404:
        description: Sala não encontrada
    """
    data = request.json
    jogador_nome = data.get("jogador")

    if not jogador_nome or jogador_nome.strip() == "":
        return jsonify({"erro": "É necessário informar o nome do jogador"}), 400

    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404

    if "espectadores" not in sala:
        sala["espectadores"] = []
    if "nomes" not in sala:
        sala["nomes"] = {}

    if len(sala["jogadores"]) < 2:
        # É um jogador
        simbolo = "X" if len(sala["jogadores"]) == 0 else "O"
        sala["jogadores"].append(simbolo)
        sala["nomes"][simbolo] = jogador_nome

        publicar_evento_websocket("jogador_entrou", sala_id, {
            "jogador_nome": jogador_nome,
            "simbolo": simbolo,
            "tipo": "jogador",
            "total_jogadores": len(sala["jogadores"]),
            "total_espectadores": len(sala["espectadores"]),
            "vez_atual": sala.get("vez", "X")
        })

        salvar_sala(sala)
        logger.info(f"Jogador '{jogador_nome}' entrou na sala {sala_id} como {simbolo}")

        return jsonify({
            "msg": f"Jogador {jogador_nome} entrou como {simbolo}",
            "sala": sala,
            "seu_simbolo": simbolo,
            "tipo": "jogador"
        })
    else:
        # É um espectador
        sala["espectadores"].append(jogador_nome)

        publicar_evento_websocket("espectador_entrou", sala_id, {
            "espectador_nome": jogador_nome,
            "tipo": "espectador",
            "total_jogadores": len(sala["jogadores"]),
            "total_espectadores": len(sala["espectadores"])
        })

        salvar_sala(sala)
        logger.info(f"Espectador '{jogador_nome}' entrou na sala {sala_id}")

        return jsonify({
            "msg": f"Você entrou como espectador",
            "sala": sala,
            "tipo": "espectador"
        })

@app.route("/salas/<sala_id>/jogar", methods=["POST"])
def jogar_sala(sala_id):
    """
    Fazer uma jogada no tabuleiro
    ---
    tags:
      - Jogadas
    parameters:
      - name: sala_id
        in: path
        type: string
        required: true
        description: ID da sala
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - jogador
            - pos
          properties:
            jogador:
              type: string
              example: "Player1"
              description: Nome do jogador
            pos:
              type: integer
              example: 4
              description: Posição no tabuleiro (0-8)
              minimum: 0
              maximum: 8
    responses:
      200:
        description: Jogada registrada com sucesso
        schema:
          type: object
          properties:
            msg:
              type: string
            sala:
              type: object
            resultado:
              type: string
      400:
        description: Jogador/posição inválida ou não é a vez do jogador
      404:
        description: Sala não encontrada
    """
    data = request.json
    nome = data.get("jogador")
    pos = data.get("pos")

    if nome is None or pos is None:
        return jsonify({"erro": "É necessário informar o jogador e a posição"}), 400

    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404

    simbolo = None
    for s, n in sala.get("nomes", {}).items():
        if n == nome:
            simbolo = s
            break

    if not simbolo:
        return jsonify({"erro": "Jogador não está na sala"}), 400

    if not isinstance(pos, int) or pos < 0 or pos > 8:
        return jsonify({"erro": "Posição inválida (deve ser um número entre 0 e 8)"}), 400

    if sala["tabuleiro"][pos] != "":
        return jsonify({"erro": "Posição já ocupada"}), 400

    if sala["vez"] != simbolo:
        jogador_da_vez = sala["nomes"].get(sala["vez"], "Desconhecido")
        return jsonify({"erro": f"Não é a sua vez. É a vez de {jogador_da_vez} ({sala['vez']})"}), 400

    sala["tabuleiro"][pos] = simbolo

    vencedor = verificar_vitoria(sala["tabuleiro"])
    resultado = None

    if vencedor:
        sala["vencedor"] = vencedor
        resultado = "vitoria"
        mensagem = f"🏆 Jogador {sala['nomes'][vencedor]} venceu!"


        publicar_evento_websocket("jogo_vitoria", sala_id, {
            "vencedor": vencedor,
            "vencedor_nome": sala['nomes'][vencedor],
            "posicao": pos,
            "tabuleiro": sala["tabuleiro"]
        })


    elif verificar_empate(sala["tabuleiro"]):
        sala["empate"] = True
        resultado = "empate"
        mensagem = "🤝 Empate!"


        publicar_evento_websocket("jogo_empate", sala_id, {
            "posicao": pos,
            "tabuleiro": sala["tabuleiro"]
        })

    else:

        sala["vez"] = "O" if sala["vez"] == "X" else "X"
        resultado = "jogada"
        mensagem = "Jogada registrada"


        publicar_evento_websocket("jogada_realizada", sala_id, {
            "jogador": nome,
            "simbolo": simbolo,
            "posicao": pos,
            "tabuleiro": sala["tabuleiro"],
            "proximo_a_jogar": sala["vez"],
            "proximo_nome": sala["nomes"].get(sala["vez"], "Aguardando jogador")
        })

    salvar_sala(sala)
    logger.info(f"Jogada: {nome} ({simbolo}) na posição {pos} na sala {sala_id}")

    return jsonify({
        "msg": mensagem,
        "sala": sala,
        "resultado": resultado,
        "proximo": sala.get("vez") if resultado == "jogada" else None
    })

@app.route("/salas/<sala_id>", methods=["GET"])
def consultar_sala(sala_id):
    """
    Consultar estado atual da sala
    ---
    tags:
      - Salas
    parameters:
      - name: sala_id
        in: path
        type: string
        required: true
        description: ID da sala
    responses:
      200:
        description: Estado da sala
        schema:
          type: object
          properties:
            id:
              type: string
            jogadores:
              type: array
            tabuleiro:
              type: array
            vez:
              type: string
            nomes:
              type: object
            vencedor:
              type: string
            empate:
              type: boolean
      404:
        description: Sala não encontrada
    """
    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404

    sala_info = sala.copy()

    if "vencedor" in sala:
        sala_info["status"] = "finalizado_vitoria"
        sala_info["vencedor_nome"] = sala["nomes"].get(sala["vencedor"])
    elif sala.get("empate"):
        sala_info["status"] = "finalizado_empate"
    elif len(sala.get("jogadores", [])) < 2:
        sala_info["status"] = "aguardando_jogadores"
    else:
        sala_info["status"] = "em_andamento"


    if "vez" in sala and "nomes" in sala:
        sala_info["vez_nome"] = sala["nomes"].get(sala["vez"], "Aguardando jogador")

    return jsonify(sala_info)

@app.route("/salas/<sala_id>/reiniciar", methods=["POST"])
def reiniciar_sala(sala_id):
    """
    Reiniciar o jogo na sala
    ---
    tags:
      - Salas
    parameters:
      - name: sala_id
        in: path
        type: string
        required: true
        description: ID da sala
    responses:
      200:
        description: Jogo reiniciado com sucesso
        schema:
          type: object
          properties:
            msg:
              type: string
            sala:
              type: object
      404:
        description: Sala não encontrada
    """
    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404


    sala["tabuleiro"] = ["", "", "", "", "", "", "", "", ""]
    sala["vez"] = "X"
    sala.pop("vencedor", None)
    sala.pop("empate", None)

    salvar_sala(sala)

    publicar_evento_websocket("jogo_reiniciado", sala_id, {
        "tabuleiro": sala["tabuleiro"],
        "vez": sala["vez"]
    })

    logger.info(f"Jogo reiniciado na sala {sala_id}")

    return jsonify({
        "msg": "Jogo reiniciado!",
        "sala": sala
    })

@app.route("/salas/<sala_id>/chat", methods=["POST"])
def enviar_chat(sala_id):
    """
    Enviar mensagem no chat da sala
    ---
    tags:
      - Chat
    parameters:
      - name: sala_id
        in: path
        type: string
        required: true
        description: ID da sala
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - jogador
            - mensagem
          properties:
            jogador:
              type: string
              description: Nome do jogador ou espectador
            mensagem:
              type: string
              description: Mensagem a ser enviada
    responses:
      200:
        description: Mensagem enviada com sucesso
      400:
        description: Jogador ou mensagem não informados
      404:
        description: Sala não encontrada
    """
    data = request.json
    jogador_nome = data.get("jogador")
    mensagem = data.get("mensagem")

    if not jogador_nome or not mensagem:
        return jsonify({"erro": "É necessário informar o jogador e a mensagem"}), 400

    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404

    # Verificar se o usuário está na sala (jogador ou espectador)
    is_player = any(sala.get("nomes", {}).get(s) == jogador_nome for s in ["X", "O"])
    is_spectator = jogador_nome in sala.get("espectadores", [])

    if not is_player and not is_spectator:
        return jsonify({"erro": "Você não está na sala"}), 400

    # Publicar mensagem de chat
    publicar_evento_websocket("chat_mensagem", sala_id, {
        "jogador_nome": jogador_nome,
        "mensagem": mensagem,
        "tipo": "jogador" if is_player else "espectador",
        "timestamp": time.time()
    })

    logger.info(f"Chat na sala {sala_id}: {jogador_nome}: {mensagem}")

    return jsonify({
        "msg": "Mensagem enviada",
        "jogador": jogador_nome,
        "mensagem": mensagem
    })

@app.route("/salas/<sala_id>/sair", methods=["POST"])
def sair_sala(sala_id):
    """
    Sair de uma sala
    ---
    tags:
      - Salas
    parameters:
      - name: sala_id
        in: path
        type: string
        required: true
        description: ID da sala
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - jogador
          properties:
            jogador:
              type: string
              description: Nome do jogador
    responses:
      200:
        description: Jogador saiu da sala
      400:
        description: Jogador não informado ou não está na sala
      404:
        description: Sala não encontrada
    """
    data = request.json
    jogador_nome = data.get("jogador")

    if not jogador_nome:
        return jsonify({"erro": "É necessário informar o nome do jogador"}), 400

    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404

    # Verificar se é jogador ou espectador
    simbolo_remover = None
    for simbolo, nome in sala.get("nomes", {}).items():
        if nome == jogador_nome:
            simbolo_remover = simbolo
            break

    is_spectator = jogador_nome in sala.get("espectadores", [])

    if not simbolo_remover and not is_spectator:
        return jsonify({"erro": "Usuário não está na sala"}), 400

    if simbolo_remover:
        # Remover jogador
        if simbolo_remover in sala["jogadores"]:
            sala["jogadores"].remove(simbolo_remover)

        if "nomes" in sala and simbolo_remover in sala["nomes"]:
            del sala["nomes"][simbolo_remover]

        if len(sala["jogadores"]) == 0:
            pass
        else:
            if sala.get("vez") == simbolo_remover and sala["jogadores"]:
                sala["vez"] = sala["jogadores"][0]

        salvar_sala(sala)

        # Publicar evento
        publicar_evento_websocket("jogador_saiu", sala_id, {
            "jogador_nome": jogador_nome,
            "simbolo": simbolo_remover,
            "tipo": "jogador",
            "jogadores_restantes": len(sala["jogadores"]),
            "espectadores_restantes": len(sala.get("espectadores", []))
        })

        logger.info(f"Jogador '{jogador_nome}' saiu da sala {sala_id}")

        return jsonify({
            "msg": f"Jogador {jogador_nome} saiu da sala",
            "jogadores_restantes": len(sala["jogadores"])
        })
    else:
        # Remover espectador
        sala["espectadores"].remove(jogador_nome)

        salvar_sala(sala)

        # Publicar evento
        publicar_evento_websocket("espectador_saiu", sala_id, {
            "espectador_nome": jogador_nome,
            "tipo": "espectador",
            "jogadores_restantes": len(sala["jogadores"]),
            "espectadores_restantes": len(sala["espectadores"])
        })

        logger.info(f"Espectador '{jogador_nome}' saiu da sala {sala_id}")

        return jsonify({
            "msg": f"Espectador {jogador_nome} saiu da sala",
            "espectadores_restantes": len(sala["espectadores"])
        })

@app.route("/status", methods=["GET"])
def status():
    """
    Verificar status da API
    ---
    tags:
      - Sistema
    responses:
      200:
        description: Status da API
    """
    try:

        redis_status = "online" if r.ping() else "offline"

        return jsonify({
            "status": "online",
            "api": "REST API Jogo da Velha",
            "versao": "2.0.0",
            "redis": redis_status,
            "websocket_support": True,
            "endpoints": {
                "criar_sala": "via SOAP (porta 8001)",
                "entrar_sala": "POST /salas/{id}/entrar",
                "jogar": "POST /salas/{id}/jogar",
                "consultar": "GET /salas/{id}",
                "reiniciar": "POST /salas/{id}/reiniciar",
                "sair": "POST /salas/{id}/sair"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "online",
            "api": "REST API Jogo da Velha",
            "redis": "error",
            "erro": str(e)
        }), 500

@app.route("/")
def index():
    """Página inicial"""
    return jsonify({
        "status": "REST API do jogo da velha está rodando!",
        "versao": "2.0.0",
        "websocket": True,
        "documentacao": "/apidocs/",
        "status_api": "/status"
    })


@app.route("/health", methods=["GET"])
def health_check():
    """Health check para monitoramento"""
    try:
        r.ping()
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "redis": "disconnected", "erro": str(e)}), 500

if __name__ == "__main__":
    logger.info("🚀 Iniciando REST API do Jogo da Velha com WebSocket...")
    logger.info(f"📡 WebSocket Channel: {WEBSOCKET_CHANNEL}")
    app.run(host="0.0.0.0", port=5000, debug=True)
