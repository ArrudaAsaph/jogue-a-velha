import asyncio
import websockets
import json
import redis
import logging
from datetime import datetime
from typing import Dict, Set

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

rooms: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}


try:
    redis_client = redis.Redis(
        host='redis',
        port=6379,
        decode_responses=True
    )
    redis_client.ping()
    logger.info("✅ Conectado ao Redis")
except Exception as e:
    logger.error(f"❌ ERRO Redis: {str(e)}")
    redis_client = None

async def broadcast_to_room(room_id: str, message: dict):
    """Envia mensagem para todos na sala"""
    if room_id in rooms and rooms[room_id]:
        message_json = json.dumps(message)
        disconnected = []

        for client in rooms[room_id]:
            try:
                await client.send(message_json)
                logger.debug(f"📤 Mensagem enviada para cliente na sala {room_id}")
            except Exception as e:
                logger.error(f"Erro ao enviar: {str(e)}")
                disconnected.append(client)


        for client in disconnected:
            if room_id in rooms:
                rooms[room_id].discard(client)
                logger.info(f"🧹 Cliente removido da sala {room_id}")

async def handler(websocket, path):
    """Manipula conexões WebSocket"""
    client_ip = websocket.remote_address[0]
    logger.info(f"🔗 Nova conexão de {client_ip}")

    try:

        if not path.startswith('/ws/'):
            await websocket.close(1008, "Path inválido. Use /ws/{room_id}")
            return

        room_id = path[4:]

        if not room_id:
            await websocket.close(1008, "Room ID não especificado")
            return


        if room_id not in rooms:
            rooms[room_id] = set()
        rooms[room_id].add(websocket)

        logger.info(f"✅ Cliente conectado à sala {room_id}. Total: {len(rooms[room_id])}")

        await websocket.send(json.dumps({
            "type": "connection_established",
            "room_id": room_id,
            "message": f"Conectado à sala {room_id}",
            "timestamp": datetime.now().isoformat()
        }))


        if redis_client:
            try:
                room_data = redis_client.get(f"sala:{room_id}")
                if room_data:
                    room_state = json.loads(room_data)
                    await websocket.send(json.dumps({
                        "type": "initial_state",
                        "room": room_state,
                        "timestamp": datetime.now().isoformat()
                    }))
            except Exception as e:
                logger.error(f"Erro ao buscar estado inicial: {str(e)}")


        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action")

                if action == "ping":

                    await websocket.send(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))

                elif action == "get_state":
                    # Buscar estado atual do Redis
                    if redis_client:
                        room_data = redis_client.get(f"sala:{room_id}")
                        if room_data:
                            room_state = json.loads(room_data)
                            await websocket.send(json.dumps({
                                "type": "state_update",
                                "room": room_state,
                                "timestamp": datetime.now().isoformat()
                            }))

                elif action == "chat":
                    # Broadcast de mensagem de chat
                    chat_data = {
                        "type": "chat_message",
                        "sender": data.get("sender"),
                        "message": data.get("message"),
                        "timestamp": datetime.now().isoformat()
                    }
                    await broadcast_to_room(room_id, chat_data)
                    logger.info(f"💬 Chat na sala {room_id}: {data.get('sender')}: {data.get('message')}")

                elif action == "player_update":
                    # Broadcast de atualização de jogadores/espectadores
                    update_data = {
                        "type": "player_update",
                        "data": data.get("data", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                    await broadcast_to_room(room_id, update_data)

            except json.JSONDecodeError:
                logger.warning("Mensagem JSON inválida recebida")
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {str(e)}")

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"🔌 Conexão fechada de {client_ip}")
    except Exception as e:
        logger.error(f"Erro na conexão: {str(e)}")
    finally:
        # Remover conexão
        if 'room_id' in locals() and room_id in rooms:
            rooms[room_id].discard(websocket)
            if not rooms[room_id]:
                del rooms[room_id]
            logger.info(f"📴 Cliente desconectado da sala {room_id}")

async def monitor_redis_events():
    """Monitora mudanças no Redis (Pub/Sub)"""
    if not redis_client:
        logger.warning("Redis não disponível, monitoramento desativado")
        return

    pubsub = redis_client.pubsub()

    try:
        pubsub.subscribe('jogo_velha_events')

        logger.info("👂 Monitorando eventos do jogo no Redis (canal: jogo_velha_events)...")

        while True:
            loop = asyncio.get_event_loop()
            message = await loop.run_in_executor(
                None,
                lambda: pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            )

            if message and message['type'] == 'message':
                try:
                    event = json.loads(message['data'])
                    sala_id = event.get('sala_id')
                    evento = event.get('evento')
                    dados = event.get('dados', {})

                    if sala_id and evento:
                        logger.info(f"📡 Evento Redis: {evento} na sala {sala_id}")

                        # Broadcast para a sala
                        await broadcast_to_room(sala_id, {
                            "type": "game_event",
                            "evento": evento,
                            "dados": dados,
                            "timestamp": datetime.now().isoformat()
                        })

                except Exception as e:
                    logger.error(f"Erro ao processar evento Redis: {str(e)}")

            await asyncio.sleep(0.01)  # evita sobrecarregar

    except Exception as e:
        logger.error(f"Erro no monitoramento Redis: {str(e)}")

async def health_check():
    """Verificação periódica de saúde"""
    while True:
        await asyncio.sleep(30)
        total_connections = sum(len(clients) for clients in rooms.values())
        logger.info(f"📊 Status: {total_connections} conexões em {len(rooms)} salas")

async def main():
    """Inicia o servidor WebSocket"""

    asyncio.create_task(monitor_redis_events())
    asyncio.create_task(health_check())


    server = await websockets.serve(
        handler,
        host="0.0.0.0",
        port=8002,
        ping_interval=20,
        ping_timeout=30
    )

    logger.info("🚀 WebSocket Server iniciado na porta 8002")
    logger.info("📌 Endpoints disponíveis:")
    logger.info("  - ws://localhost:8002/ws/{room_id} - Conectar a uma sala")

    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Servidor WebSocket encerrado")
