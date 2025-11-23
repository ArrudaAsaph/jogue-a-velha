import json
import redis
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import uuid


r = redis.Redis(host='redis_jogo', port=6379, decode_responses=True)

class JogoDaVelhaService(ServiceBase):

    @rpc(Unicode, _returns=Unicode)
    def criarSala(ctx, porta):
        """Cria uma sala no Redis usando SEMPRE localhost como IP."""
        sala_id = str(uuid.uuid4())

        ip_local = "127.0.0.1"   

        sala = {
            "id": sala_id,
            "ip": ip_local,
            "porta": porta,
            "jogadores": [],
            "tabuleiro": ["", "", "", "", "", "", "", "", ""],
            "vez": "X"
        }

        r.set(f"sala:{sala_id}", json.dumps(sala))
        return sala_id



application = Application(
    [JogoDaVelhaService],
    tns='http://jogovelha.com/soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

wsgi_app = WsgiApplication(application)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    print("SOAP rodando na porta 8001...")
    server = make_server('0.0.0.0', 8001, wsgi_app)
    server.serve_forever()
