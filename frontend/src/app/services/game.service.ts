import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subscription } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

export interface Sala {
  id: string;
  ip: string;
  porta: string;
  jogadores: string[];
  tabuleiro: string[];
  vez: string;
  nomes?: { [key: string]: string };
  vencedor?: string;
  empate?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private readonly apiUrl = `http://${window.location.hostname}:8000`;
  private readonly wsBaseUrl = `ws://${window.location.hostname}:8002`;

  currentRoom = signal<string | null>(null);
  currentPlayer = signal<string | null>(null);
  currentSymbol = signal<string | null>(null);
  gameState = signal<Sala | null>(null);
  wsConnected = signal<boolean>(false);
  chatMessages = signal<Array<{ sender: string; message: string; timestamp: string }>>([]);

  private ws$?: WebSocketSubject<any>;
  private wsSub?: Subscription;

  constructor(private http: HttpClient) {}

  createRoom(porta: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/criar-sala`, { porta });
  }

  joinRoom(roomId: string, playerName: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/salas/${roomId}/entrar`, { jogador: playerName });
  }

  makeMove(roomId: string, playerName: string, position: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/salas/${roomId}/jogar`, {
      jogador: playerName,
      pos: position
    });
  }

  getRoomState(roomId: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/salas/${roomId}`);
  }

  restartGame(roomId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/salas/${roomId}/reiniciar`, {});
  }

  setCurrentRoom(roomId: string) {
    this.currentRoom.set(roomId);
  }

  setCurrentPlayer(playerName: string, symbol: string) {
    this.currentPlayer.set(playerName);
    this.currentSymbol.set(symbol);
  }

  updateGameState(state: Sala) {
    this.gameState.set(state);
  }

  resetGame() {
    this.currentRoom.set(null);
    this.currentPlayer.set(null);
    this.currentSymbol.set(null);
    this.gameState.set(null);
    this.chatMessages.set([]);
    this.disconnectFromRoom();
  }

  connectToRoom(roomId: string) {
    if (this.ws$) return;
    const url = `${this.wsBaseUrl}/ws/${roomId}`;
    this.ws$ = webSocket({
      url,
      deserializer: (e) => JSON.parse((e as MessageEvent).data),
      serializer: (value) => JSON.stringify(value),
      openObserver: { next: () => this.wsConnected.set(true) },
      closeObserver: { next: () => this.wsConnected.set(false) }
    });

    this.wsSub = this.ws$.subscribe({
      next: (msg) => this.handleWsMessage(msg),
      error: () => this.wsConnected.set(false),
      complete: () => this.wsConnected.set(false)
    });

    this.requestState();
  }

  disconnectFromRoom() {
    try {
      this.wsSub?.unsubscribe();
      this.ws$?.complete();
    } finally {
      this.wsSub = undefined;
      this.ws$ = undefined;
      this.wsConnected.set(false);
    }
  }

  ping() {
    this.sendWs({ action: 'ping' });
  }

  requestState() {
    this.sendWs({ action: 'get_state' });
  }

  sendChat(sender: string, message: string) {
    this.sendWs({ action: 'chat', sender, message });
  }

  private sendWs(payload: any) {
    try {
      this.ws$?.next(payload);
    } catch {}
  }

  private handleWsMessage(msg: any) {
    const type = msg?.type;
    if (type === 'initial_state' && msg.room) {
      this.updateGameState(msg.room as Sala);
    } else if (type === 'state_update' && msg.room) {
      this.updateGameState(msg.room as Sala);
    } else if (type === 'chat_message') {
      const item = {
        sender: msg.sender ?? 'Desconhecido',
        message: msg.message ?? '',
        timestamp: msg.timestamp ?? new Date().toISOString()
      };
      const current = this.chatMessages();
      this.chatMessages.set([...current, item]);
    } else if (type === 'game_event') {
      const sala = msg?.dados?.sala;
      if (sala) {
        this.updateGameState(sala as Sala);
      } else if (this.currentRoom()) {
        this.getRoomState(this.currentRoom() as string).subscribe({
          next: (state) => this.updateGameState(state as Sala)
        });
      }
    }
  }
}
