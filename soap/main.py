import json
import redis
from spyne import Application, rpc, ServiceBase, Unicode, Fault
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import uuid

try:
    redis = redis.Redis(host='redis_jogo', port=6379, decode_responses=True)
    redis.ping()
except Exception as e:
    print("❌ ERRO: Não foi possível conectar ao Redis:", str(e))
    raise SystemExit("Finalizando API SOAP...")


class JogoDaVelhaService(ServiceBase):

    @rpc(Unicode, _returns=Unicode)
    def criarSala(ctx, porta):
       
        if porta is None or porta.strip() == "":
            raise Fault(faultcode="Client.PortMissing",
                        faultstring="O campo 'porta' é obrigatório.")

        if not porta.isdigit():
            raise Fault(faultcode="Client.PortInvalid",
                        faultstring="A porta deve ser um número inteiro.")

        porta_int = int(porta)

        if porta_int < 1 or porta_int > 65535:
            raise Fault(faultcode="Client.PortOutOfRange",
                        faultstring="A porta deve estar entre 1 e 65535.")

        # Criar ID da sala
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

 
        try:
            redis.set(f"sala:{sala_id}", json.dumps(sala))


            check = redis.get(f"sala:{sala_id}")
            if check is None:
                raise Exception("Falha ao gravar no Redis")

        except Exception as e:
            raise Fault(faultcode="Server.RedisError",
                        faultstring=f"Erro ao salvar sala no Redis: {str(e)}")

        return sala_id




# Configuração SOAP
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
