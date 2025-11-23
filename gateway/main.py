# gateway/main.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configurações dos serviços
REST_API_URL = "http://rest-api:5000"
SOAP_API_URL = "http://soap-api:8001"

# -----------------------------
# Rotas Gateway com HATEOAS
# -----------------------------

@app.route("/criar-sala", methods=["POST"])
def criar_sala_gateway():
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
        # Extraindo o RoomID do XML (simples regex)
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
    """Encaminha a requisição para o REST API com HATEOAS"""
    payload = request.json
    try:
        resp = requests.post(f"{REST_API_URL}/salas/{sala_id}/entrar", json=payload)
        data = resp.json()
        # Adicionando HATEOAS
        data["_links"] = {
            "jogar": f"/salas/{sala_id}/jogar",
            "consultar_sala": f"/salas/{sala_id}"
        }
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/salas/<sala_id>/jogar", methods=["POST"])
def jogar(sala_id):
    """Encaminha a jogada para o REST API com HATEOAS"""
    payload = request.json
    try:
        resp = requests.post(f"{REST_API_URL}/salas/{sala_id}/jogar", json=payload)
        data = resp.json()
        # Adicionando HATEOAS
        data["_links"] = {
            "consultar_sala": f"/salas/{sala_id}"
        }
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/salas/<sala_id>", methods=["GET"])
def consultar_sala(sala_id):
    """Consulta estado da sala via REST API com HATEOAS"""
    try:
        resp = requests.get(f"{REST_API_URL}/salas/{sala_id}")
        data = resp.json()
        # Adicionando HATEOAS
        data["_links"] = {
            "entrar_sala": f"/salas/{sala_id}/entrar",
            "jogar": f"/salas/{sala_id}/jogar"
        }
        return jsonify(data), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"erro": str(e)}), 500

# -----------------------------
# Rodar Gateway
# -----------------------------
if __name__ == "__main__":
    print("Gateway rodando na porta 8000...")
    app.run(host="0.0.0.0", port=8000)
