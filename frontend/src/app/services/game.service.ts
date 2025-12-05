import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
  espectadores?: string[];
}

export interface ChatMessage {
  jogador_nome: string;
  mensagem: string;
  tipo: 'jogador' | 'espectador';
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private readonly apiUrl = `http://${window.location.hostname}:8000`;

  currentRoom = signal<string | null>(null);
  currentPlayer = signal<string | null>(null);
  currentSymbol = signal<string | null>(null);
  gameState = signal<Sala | null>(null);
  userType = signal<'jogador' | 'espectador' | null>(null);
  chatMessages = signal<ChatMessage[]>([]);

  constructor(private http: HttpClient) { }

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

  sendChatMessage(roomId: string, playerName: string, message: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/salas/${roomId}/chat`, {
      jogador: playerName,
      mensagem: message
    });
  }

  setCurrentRoom(roomId: string) {
    this.currentRoom.set(roomId);
  }

  setCurrentPlayer(playerName: string, symbol: string, userType: 'jogador' | 'espectador' = 'jogador') {
    this.currentPlayer.set(playerName);
    this.currentSymbol.set(symbol);
    this.userType.set(userType);
  }

  updateGameState(state: Sala) {
    this.gameState.set(state);
  }

  addChatMessage(message: ChatMessage) {
    this.chatMessages.update(messages => [...messages, message]);
  }

  resetGame() {
    this.currentRoom.set(null);
    this.currentPlayer.set(null);
    this.currentSymbol.set(null);
    this.gameState.set(null);
    this.userType.set(null);
    this.chatMessages.set([]);
  }
}
