# gateway/main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import requests

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configuração do Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Jogo da Velha - API Gateway",
        "description": "API Gateway com HATEOAS para gerenciar salas de jogo da velha. Integra SOAP (criar salas) e REST (jogadas).",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "url": "https://github.com/ArrudaAsaph/jogue-a-velha"
        }
    },
    "host": "localhost:8000",
    "basePath": "/",
    "schemes": ["http"],
}

Swagger(app, config=swagger_config, template=swagger_template)

REST_API_URL = "http://rest-api:5000"
SOAP_API_URL = "http://soap-api:8001"



@app.route("/criar-sala", methods=["POST"])
def criar_sala_gateway():
    """
    Criar uma nova sala de jogo
    ---
    tags:
      - Salas
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - porta
          properties:
            porta:
              type: string
              example: "8080"
              description: Porta da sala
    responses:
      200:
        description: Sala criada com sucesso
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Sala criada com sucesso"
            room_id:
              type: string
              example: "a89a87f8-5dc6-44f7-94a9-19926b5e7253"
            _links:
              type: object
              properties:
                entrar_sala:
                  type: string
                  example: "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/entrar"
                consultar_sala:
                  type: string
                  example: "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253"
                jogar:
                  type: string
                  example: "/salas/a89a87f8-5dc6-44f7-94a9-19926b5e7253/jogar"
      400:
        description: Porta não fornecida
      500:
        description: Erro ao criar sala
    """
    payload = request.json
    porta = payload.get("porta")
    if not porta:
        return jsonify({"erro": "porta é obrigatória"}), 400

    soap_request = f"""<?xml version="1.0"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ser="http://jogovelha.com/soap">
   <soapenv:Header/>
   <soapenv:Body>
      <ser:criarSala>
         <ser:porta>{porta}</ser:porta>
      </ser:criarSala>
   </soapenv:Body>
</soapenv:Envelope>"""

    try:
        resp = requests.post(SOAP_API_URL, data=soap_request, headers={"Content-Type": "text/xml"})


        import re
        match = re.search(r"<tns:criarSalaResult>(.*?)</tns:criarSalaResult>", resp.text)
        room_id = match.group(1) if match else None

        response_json = {
            "msg": "Sala criada com sucesso",
            "room_id": room_id,
            "_links": {
                "entrar_sala": f"/salas/{room_id}/entrar",
                "consultar_sala": f"/salas/{room_id}",
                "jogar": f"/salas/{room_id}/jogar"
            }
        }
        return jsonify(response_json), resp.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

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
        example: "a89a87f8-5dc6-44f7-94a9-19926b5e7253"
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
              example: "Jogador Player1 entrou como X"
            sala:
              type: object
            _links:
              type: object
      400:
        description: Jogador não informado ou sala cheia
      404:
        description: Sala não encontrada
    """
    payload = request.json
    try:
        resp = requests.post(f"{REST_API_URL}/salas/{sala_id}/entrar", json=payload)
        data = resp.json()

        #  HATEOAS
        data["_links"] = {
            "jogar": f"/salas/{sala_id}/jogar",
            "consultar_sala": f"/salas/{sala_id}"
        }
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/salas/<sala_id>/jogar", methods=["POST"])
def jogar(sala_id):
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
            _links:
              type: object
      400:
        description: Jogador/posição inválida ou não é a vez do jogador
      404:
        description: Sala não encontrada
    """
    payload = request.json
    try:
        resp = requests.post(f"{REST_API_URL}/salas/{sala_id}/jogar", json=payload)
        data = resp.json()

        data["_links"] = {
            "consultar_sala": f"/salas/{sala_id}"
        }
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

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
              items:
                type: string
            tabuleiro:
              type: array
              items:
                type: string
            vez:
              type: string
            nomes:
              type: object
            _links:
              type: object
      404:
        description: Sala não encontrada
    """
    try:
        resp = requests.get(f"{REST_API_URL}/salas/{sala_id}")
        data = resp.json()

        data["_links"] = {
            "entrar_sala": f"/salas/{sala_id}/entrar",
            "jogar": f"/salas/{sala_id}/jogar",
            "reiniciar": f"/salas/{sala_id}/reiniciar"
        }
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

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
              example: "Jogo reiniciado!"
            sala:
              type: object
            _links:
              type: object
      404:
        description: Sala não encontrada
    """
    try:
        resp = requests.post(f"{REST_API_URL}/salas/{sala_id}/reiniciar")
        data = resp.json()

        data["_links"] = {
            "jogar": f"/salas/{sala_id}/jogar",
            "consultar_sala": f"/salas/{sala_id}"
        }
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

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
    try:
        payload = request.json
        resp = requests.post(f"{REST_API_URL}/salas/{sala_id}/chat", json=payload)
        data = resp.json()
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

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
              description: Nome do jogador ou espectador
    responses:
      200:
        description: Usuário saiu da sala
      400:
        description: Jogador não informado
      404:
        description: Sala não encontrada
    """
    try:
        payload = request.json
        resp = requests.post(f"{REST_API_URL}/salas/{sala_id}/sair", json=payload)
        data = resp.json()
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500


if __name__ == "__main__":
    print("Gateway rodando na porta 8000...")
    app.run(host="0.0.0.0", port=8000)
