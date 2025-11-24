from flask import Flask, request, jsonify
from flasgger import Swagger
import redis
import json

app = Flask(__name__)

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
        "description": "API REST para gerenciar jogadas e estado das salas",
        "version": "1.0.0"
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
}

Swagger(app, config=swagger_config, template=swagger_template)

r = redis.Redis(host="redis_jogo", port=6379, decode_responses=True)


def carregar_sala(sala_id):
    data = r.get(f"sala:{sala_id}")
    if not data:
        return None
    return json.loads(data)

def salvar_sala(sala):
    r.set(f"sala:{sala['id']}", json.dumps(sala))

def verificar_vitoria(tab):
    combinacoes = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    for a,b,c in combinacoes:
        if tab[a] != "" and tab[a] == tab[b] == tab[c]:
            return tab[a]
    return None



@app.route("/salas/<sala_id>/entrar", methods=["POST"])
def entrar_sala(sala_id):
    data = request.json
    jogador_nome = data.get("jogador")

    if not jogador_nome:
        return jsonify({"erro": "É necessário informar o nome do jogador"}), 400

    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404

    if len(sala["jogadores"]) >= 2:
        return jsonify({"erro": "A sala já está cheia"}), 400

    simbolo = "X" if len(sala["jogadores"]) == 0 else "O"
    sala["jogadores"].append(simbolo)

    if "nomes" not in sala:
        sala["nomes"] = {}
    sala["nomes"][simbolo] = jogador_nome

    salvar_sala(sala)
    return jsonify({"msg": f"Jogador {jogador_nome} entrou como {simbolo}", "sala": sala})

@app.route("/salas/<sala_id>/jogar", methods=["POST"])
def jogar_sala(sala_id):
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

    if pos < 0 or pos > 8:
        return jsonify({"erro": "Posição inválida (0 a 8)"}), 400
    if sala["tabuleiro"][pos] != "":
        return jsonify({"erro": "Posição já ocupada"}), 400
    if sala["vez"] != simbolo:
        return jsonify({"erro": f"Não é a vez do jogador {nome}"}), 400

    sala["tabuleiro"][pos] = simbolo

    # Verificar vitória
    vencedor = verificar_vitoria(sala["tabuleiro"])
    if vencedor:
        sala["vencedor"] = vencedor
        salvar_sala(sala)
        return jsonify({"msg": f"Jogador {sala['nomes'][vencedor]} venceu!", "sala": sala})

    # Verificar empate
    if "" not in sala["tabuleiro"]:
        sala["empate"] = True
        salvar_sala(sala)
        return jsonify({"msg": "Empate!", "sala": sala})

    # Trocar turno
    sala["vez"] = "O" if sala["vez"] == "X" else "X"
    salvar_sala(sala)
    return jsonify({"msg": "Jogada registrada", "sala": sala})

@app.route("/salas/<sala_id>", methods=["GET"])
def consultar_sala(sala_id):
    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404
    return jsonify(sala)

@app.route("/salas/<sala_id>/reiniciar", methods=["POST"])
def reiniciar_sala(sala_id):
    sala = carregar_sala(sala_id)
    if not sala:
        return jsonify({"erro": "Sala não encontrada"}), 404

    # Reiniciar o tabuleiro mantendo os jogadores
    sala["tabuleiro"] = ["", "", "", "", "", "", "", "", ""]
    sala["vez"] = "X"

    # Remover flags de fim de jogo
    if "vencedor" in sala:
        del sala["vencedor"]
    if "empate" in sala:
        del sala["empate"]

    salvar_sala(sala)
    return jsonify({"msg": "Jogo reiniciado!", "sala": sala})

@app.route("/")
def index():
    return jsonify({"status": "REST API do jogo da velha está rodando!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
