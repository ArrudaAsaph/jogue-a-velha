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
  }
}
