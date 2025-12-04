#!/usr/bin/env python3
"""
Teste completo do backend do Jogo da Velha
Inclui: REST API, SOAP, WebSocket e Redis
"""

import requests
import json
import time
import asyncio
import websockets
import threading
from datetime import datetime

# Configurações
GATEWAY_URL = "http://localhost:8000"
REST_URL = "http://localhost:5000"
SOAP_URL = "http://localhost:8001"
WS_URL = "ws://localhost:8002"

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.room_id = None
        self.websocket_messages = []
        
    def log_test(self, test_name, success, message=""):
        status = "✅" if success else "❌"
        result = f"{status} {test_name}: {message}"
        self.test_results.append(result)
        print(result)
        return success
    
    def test_rest_api(self):
        """Testa a API REST"""
        print("\n" + "="*60)
        print("TESTANDO API REST (porta 5000)")
        print("="*60)
        
        # Teste 1: Status da API
        try:
            response = requests.get(f"{REST_URL}/status", timeout=5)
            success = response.status_code == 200
            data = response.json()
            self.log_test("REST API Status", success, f"Código: {response.status_code}, Redis: {data.get('redis')}")
        except Exception as e:
            self.log_test("REST API Status", False, f"Erro: {str(e)}")
            return False
        
        # Teste 2: Criar sala via REST (se disponível)
        try:
            # Primeiro precisa criar sala via SOAP, então pulamos para entrada
            response = requests.get(f"{REST_URL}/", timeout=5)
            self.log_test("REST API Home", response.status_code == 200, 
                         f"Mensagem: {response.json().get('status', '')}")
        except Exception as e:
            self.log_test("REST API Home", False, f"Erro: {str(e)}")
        
        return True
    
    def test_gateway(self):
        """Testa o Gateway"""
        print("\n" + "="*60)
        print("TESTANDO GATEWAY (porta 8000)")
        print("="*60)
        
        # Teste 1: Status do Gateway
        try:
            response = requests.get(f"{GATEWAY_URL}/apidocs/", timeout=5)  # Documentação Swagger
            success = response.status_code == 200
            self.log_test("Gateway Status", success, f"Código: {response.status_code}")
        except Exception as e:
            self.log_test("Gateway Status", False, f"Erro: {str(e)}")
            return False
        
        # Teste 2: Criar sala via Gateway (chama SOAP)
        try:
            payload = {"porta": "8080"}
            response = requests.post(f"{GATEWAY_URL}/criar-sala", 
                                    json=payload, 
                                    timeout=10)
            
            success = response.status_code == 200
            data = response.json()
            
            if success and "room_id" in data:
                self.room_id = data["room_id"]
                self.log_test("Criar Sala via Gateway", True, 
                            f"Sala criada: {self.room_id}")
            else:
                self.log_test("Criar Sala via Gateway", False, 
                            f"Código: {response.status_code}, Resposta: {data}")
        except Exception as e:
            self.log_test("Criar Sala via Gateway", False, f"Erro: {str(e)}")
            return False
        
        return self.room_id is not None
    
    def test_soap_indirect(self):
        """Testa SOAP indiretamente (via Gateway)"""
        print("\n" + "="*60)
        print("TESTANDO SOAP API (indiretamente via Gateway)")
        print("="*60)
        
        # Se criamos uma sala via Gateway, o SOAP foi usado
        if self.room_id:
            self.log_test("SOAP via Gateway", True, 
                         f"Sala {self.room_id} criada com sucesso via SOAP")
            return True
        else:
            self.log_test("SOAP via Gateway", False, "Falha ao criar sala")
            return False
    
    def test_rest_endpoints(self):
        """Testa endpoints específicos da REST API"""
        if not self.room_id:
            self.log_test("REST Endpoints", False, "Sala não criada")
            return False
        
        print("\n" + "="*60)
        print(f"TESTANDO ENDPOINTS REST PARA SALA: {self.room_id}")
        print("="*60)
        
        # Teste 1: Consultar sala
        try:
            response = requests.get(f"{REST_URL}/salas/{self.room_id}", timeout=5)
            success = response.status_code == 200
            data = response.json()
            self.log_test("Consultar Sala", success, 
                         f"Jogadores: {len(data.get('jogadores', []))}, Tabuleiro: {data.get('tabuleiro', [])}")
        except Exception as e:
            self.log_test("Consultar Sala", False, f"Erro: {str(e)}")
        
        # Teste 2: Entrar jogador 1
        try:
            payload = {"jogador": "JogadorTeste1"}
            response = requests.post(f"{REST_URL}/salas/{self.room_id}/entrar", 
                                    json=payload, 
                                    timeout=5)
            
            success = response.status_code == 200
            data = response.json()
            self.log_test("Entrar Jogador 1", success, 
                         f"Mensagem: {data.get('msg', '')}, Símbolo: {data.get('seu_simbolo', '')}")
        except Exception as e:
            self.log_test("Entrar Jogador 1", False, f"Erro: {str(e)}")
        
        # Teste 3: Entrar jogador 2
        try:
            payload = {"jogador": "JogadorTeste2"}
            response = requests.post(f"{REST_URL}/salas/{self.room_id}/entrar", 
                                    json=payload, 
                                    timeout=5)
            
            success = response.status_code == 200
            data = response.json()
            self.log_test("Entrar Jogador 2", success, 
                         f"Mensagem: {data.get('msg', '')}, Símbolo: {data.get('seu_simbolo', '')}")
        except Exception as e:
            self.log_test("Entrar Jogador 2", False, f"Erro: {str(e)}")
        
        # Teste 4: Fazer jogada
        try:
            payload = {"jogador": "JogadorTeste1", "pos": 4}
            response = requests.post(f"{REST_URL}/salas/{self.room_id}/jogar", 
                                    json=payload, 
                                    timeout=5)
            
            success = response.status_code == 200
            data = response.json()
            self.log_test("Fazer Jogada", success, 
                         f"Mensagem: {data.get('msg', '')}, Resultado: {data.get('resultado', '')}")
        except Exception as e:
            self.log_test("Fazer Jogada", False, f"Erro: {str(e)}")
        
        # Teste 5: Verificar estado após jogada
        try:
            time.sleep(1)  # Aguardar processamento
            response = requests.get(f"{REST_URL}/salas/{self.room_id}", timeout=5)
            success = response.status_code == 200
            data = response.json()
            
            if success:
                tabuleiro = data.get('tabuleiro', [])
                jogada_ok = tabuleiro[4] == 'X'  # Posição 4 deve ter 'X'
                self.log_test("Verificar Jogada", jogada_ok, 
                            f"Tabuleiro: {tabuleiro}, Vez: {data.get('vez', '')}")
        except Exception as e:
            self.log_test("Verificar Jogada", False, f"Erro: {str(e)}")
        
        return True
    
    async def test_websocket_connection(self):
        """Testa conexão WebSocket"""
        if not self.room_id:
            return False
        
        print("\n" + "="*60)
        print("TESTANDO WEBSOCKET (porta 8002)")
        print("="*60)
        
        try:
            # Conectar ao WebSocket
            ws_url = f"{WS_URL}/ws/{self.room_id}"
            print(f"Conectando a: {ws_url}")
            
            async with websockets.connect(ws_url, timeout=10) as websocket:
                # Receber mensagem de conexão
                message = await websocket.recv()
                data = json.loads(message)
                
                success = data.get("type") == "connection_established"
                self.log_test("Conexão WebSocket", success, 
                            f"Mensagem: {data.get('message', '')}")
                
                # Enviar ping
                await websocket.send(json.dumps({"action": "ping"}))
                
                # Receber pong
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3)
                    data = json.loads(message)
                    # CORREÇÃO AQUI: estava checando type == "pong" mas recebeu outro
                    is_pong = data.get("type") == "pong"
                    self.log_test("Ping/Pong WebSocket", is_pong,
                                f"Resposta: {data.get('type', 'sem tipo')}")
                except asyncio.TimeoutError:
                    self.log_test("Ping/Pong WebSocket", False, "Timeout aguardando pong")
                    return False
                
                # Solicitar estado do jogo
                await websocket.send(json.dumps({"action": "get_state"}))
                
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3)
                    data = json.loads(message)
                    # CORREÇÃO: checar se é state_update
                    has_state = data.get("type") == "state_update"
                    self.log_test("Estado via WebSocket", has_state,
                                f"Tipo: {data.get('type')}")
                except asyncio.TimeoutError:
                    self.log_test("Estado via WebSocket", False, "Timeout aguardando estado")
                    return False
                
                # Manter conexão aberta por mais 2 segundos
                print("Aguardando eventos por 2 segundos...")
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2)
                    data = json.loads(message)
                    self.log_test("Evento Recebido", True,
                                f"Evento: {data.get('type')}")
                except asyncio.TimeoutError:
                    self.log_test("Eventos em Tempo Real", True,
                                "Nenhum evento recebido (normal se não houver atividade)")
                
                return True
                
        except Exception as e:
            self.log_test("Conexão WebSocket", False, f"Erro: {str(e)}")
            return False
        
    def test_integration(self):
        """Testa integração entre serviços"""
        print("\n" + "="*60)
        print("TESTANDO INTEGRAÇÃO ENTRE SERVIÇOS")
        print("="*60)
        
        # Testar se eventos são publicados no Redis
        if not self.room_id:
            return False
        
        try:
            # Fazer uma jogada para gerar evento
            payload = {"jogador": "JogadorTeste2", "pos": 0}
            response = requests.post(f"{REST_URL}/salas/{self.room_id}/jogar", 
                                    json=payload, 
                                    timeout=5)
            
            # Aguardar um pouco para o evento ser processado
            time.sleep(1)
            
            success = response.status_code == 200
            self.log_test("Integração REST→WebSocket", success,
                         f"Jogada feita, WebSocket deve receber evento (verifique logs)")
            
            # Testar reinício do jogo
            response = requests.post(f"{REST_URL}/salas/{self.room_id}/reiniciar", 
                                    timeout=5)
            self.log_test("Reiniciar Jogo", response.status_code == 200,
                         f"Mensagem: {response.json().get('msg', '')}")
            
            return True
            
        except Exception as e:
            self.log_test("Integração", False, f"Erro: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("\n" + "="*60)
        print("INICIANDO TESTES COMPLETOS DO BACKEND")
        print("="*60)
        print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Rodar testes síncronos
        self.test_rest_api()
        if self.test_gateway():
            self.test_soap_indirect()
            self.test_rest_endpoints()
            self.test_integration()
        
        # Rodar teste assíncrono do WebSocket
        try:
            asyncio.run(self.test_websocket_connection())
        except RuntimeError:
            # Já existe um loop em execução (em ambiente com event loop)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.test_websocket_connection())
            loop.close()
        
        # Resumo
        print("\n" + "="*60)
        print("RESUMO DOS TESTES")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if "✅" in r)
        failed = sum(1 for r in self.test_results if "❌" in r)
        total = len(self.test_results)
        
        print(f"✅ Passaram: {passed}/{total}")
        print(f"❌ Falharam: {failed}/{total}")
        print(f"📊 Taxa de sucesso: {(passed/total*100):.1f}%")
        
        if self.room_id:
            print(f"\n🔗 Sala de teste criada: {self.room_id}")
            print(f"🌐 Gateway: {GATEWAY_URL}/salas/{self.room_id}")
            print(f"🔄 REST: {REST_URL}/salas/{self.room_id}")
        
        return failed == 0

def main():
    """Função principal"""
    tester = BackendTester()
    
    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testes interrompidos pelo usuário")
        exit(130)

if __name__ == "__main__":
    main()