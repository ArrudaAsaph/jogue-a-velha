import { Component, OnInit, OnDestroy, signal, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { DialogModule } from 'primeng/dialog';
import { InputTextModule } from 'primeng/inputtext';
import { BadgeModule } from 'primeng/badge';
import { GameService, Sala, ChatMessage } from '../../services/game.service';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-game',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    CardModule,
    MessageModule,
    DialogModule,
    InputTextModule,
    BadgeModule
  ],
  template: `
    <div class="min-h-screen p-4">
      <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-3xl font-bold text-blue-600">Jogo da Velha</h1>
              <p class="text-gray-600 mt-1">
                Você é: <span class="font-bold">{{ gameService.currentPlayer() }}</span>
                @if (gameService.userType() === 'jogador') {
                  (<span class="font-bold text-blue-600">{{ gameService.currentSymbol() }}</span>)
                } @else {
                  (<span class="font-bold text-purple-600">Espectador 👁️</span>)
                }
              </p>
            </div>
            <button
              pButton
              label="Sair"
              icon="pi pi-sign-out"
              severity="danger"
              (click)="exitGame()"
            ></button>
          </div>
        </div>

        <!-- Main Content Grid -->
        <div class="grid lg:grid-cols-3 gap-6">
          <!-- Left Column: Game Info and Board -->
          <div class="lg:col-span-2 space-y-6">
            <!-- Game Info -->
            <div class="grid md:grid-cols-2 gap-4">
              <p-card>
                <div class="space-y-2">
                  <div class="flex justify-between">
                    <span class="font-medium">ID da Sala:</span>
                    <span class="font-mono text-sm">{{ gameService.currentRoom() }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="font-medium">Jogadores:</span>
                    <span>{{ playersCount() }}/2</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="font-medium">Espectadores:</span>
                    <span pBadge [value]="spectatorsCount().toString()" severity="info"></span>
                  </div>
                  @if (gameState()) {
                    <div class="flex justify-between">
                      <span class="font-medium">Vez de:</span>
                      <span class="font-bold" [class.text-blue-600]="isMyTurn()">
                        {{ currentTurnPlayer() }}
                      </span>
                    </div>
                  }
                </div>
              </p-card>

              <p-card>
                <div class="space-y-2">
                  @if (gameState()?.vencedor) {
                    <p-message
                      severity="success"
                      [text]="'🎉 ' + getWinnerName() + ' venceu!'"
                      styleClass="w-full"
                    />
                  } @else if (gameState()?.empate) {
                    <p-message
                      severity="info"
                      text="⚖️ Empate!"
                      styleClass="w-full"
                    />
                  } @else if (gameService.userType() === 'espectador') {
                    <p-message
                      severity="info"
                      text="👁️ Você está assistindo"
                      styleClass="w-full"
                    />
                  } @else if (isMyTurn()) {
                    <p-message
                      severity="success"
                      text="✨ Sua vez de jogar!"
                      styleClass="w-full"
                    />
                  } @else if (playersCount() === 2) {
                    <p-message
                      severity="info"
                      text="⏳ Aguardando adversário..."
                      styleClass="w-full"
                    />
                  } @else {
                    <p-message
                      severity="warn"
                      text="⏳ Aguardando segundo jogador..."
                      styleClass="w-full"
                    />
                  }
                </div>
              </p-card>
            </div>

            <!-- Game Board -->
            <div class="bg-white rounded-lg shadow-lg p-8">
              <div class="grid grid-cols-3 gap-4 max-w-md mx-auto">
                @for (cell of gameState()?.tabuleiro; track $index) {
                  <button
                    class="aspect-square text-6xl font-bold rounded-lg transition-all duration-200 border-4"
                    [class.bg-blue-50]="cell === 'X'"
                    [class.border-blue-500]="cell === 'X'"
                    [class.text-blue-600]="cell === 'X'"
                    [class.bg-red-50]="cell === 'O'"
                    [class.border-red-500]="cell === 'O'"
                    [class.text-red-600]="cell === 'O'"
                    [class.bg-gray-50]="cell === ''"
                    [class.border-gray-300]="cell === ''"
                    [class.hover:bg-gray-100]="canPlay($index)"
                    [class.cursor-pointer]="canPlay($index)"
                    [class.cursor-not-allowed]="!canPlay($index)"
                    [disabled]="!canPlay($index)"
                    (click)="makeMove($index)"
                  >
                    {{ cell }}
                  </button>
                }
              </div>

              @if (gameState()?.vencedor || gameState()?.empate) {
                <div class="text-center mt-6">
                  <button
                    pButton
                    label="Jogar Novamente"
                    icon="pi pi-refresh"
                    severity="success"
                    size="large"
                    (click)="playAgain()"
                  ></button>
                </div>
              }
            </div>

            <!-- Share Room ID -->
            @if (playersCount() === 1) {
              <div class="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6">
                <h3 class="text-lg font-bold text-yellow-800 mb-3">
                  🔗 Compartilhe o ID da sala
                </h3>
                <div class="flex gap-2">
                  <input
                    type="text"
                    [value]="gameService.currentRoom()"
                    readonly
                    class="flex-1 px-4 py-2 border-2 border-yellow-300 rounded bg-white font-mono"
                  />
                  <button
                    pButton
                    label="Copiar"
                    icon="pi pi-copy"
                    (click)="copyRoomId()"
                  ></button>
                </div>
              </div>
            }
          </div>

          <!-- Right Column: Chat -->
          <div class="lg:col-span-1">
            <div class="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-xl border border-gray-200 overflow-hidden flex flex-col h-[600px]">
              <!-- Chat Header -->
              <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-4">
                <div class="flex items-center gap-3">
                  <div class="bg-white/20 backdrop-blur-sm rounded-full p-2">
                    <i class="pi pi-comments text-white text-xl"></i>
                  </div>
                  <div class="flex-1">
                    <h3 class="text-xl font-bold text-white">Chat ao Vivo</h3>
                    <p class="text-white/80 text-xs">
                      {{ gameService.chatMessages().length }} mensagens
                    </p>
                  </div>
                  <div class="bg-white/20 backdrop-blur-sm rounded-full px-3 py-1">
                    <span class="text-white text-xs font-semibold">
                      {{ playersCount() + spectatorsCount() }} online
                    </span>
                  </div>
                </div>
              </div>

              <!-- Chat Messages -->
              <div #chatContainer class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50/50">
                @if (gameService.chatMessages().length === 0) {
                  <div class="flex flex-col items-center justify-center h-full text-gray-400">
                    <div class="bg-white rounded-full p-6 shadow-lg mb-4">
                      <i class="pi pi-comments text-5xl text-gray-300"></i>
                    </div>
                    <p class="text-lg font-medium">Nenhuma mensagem ainda</p>
                    <p class="text-sm">Seja o primeiro a enviar uma mensagem!</p>
                  </div>
                }
                @for (msg of gameService.chatMessages(); track $index) {
                  <div class="flex gap-3 animate-fade-in">
                    <!-- Avatar -->
                    <div class="flex-shrink-0">
                      <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold shadow-md"
                           [class.bg-gradient-to-br]="true"
                           [class.from-blue-400]="msg.tipo === 'jogador'"
                           [class.to-blue-600]="msg.tipo === 'jogador'"
                           [class.from-purple-400]="msg.tipo === 'espectador'"
                           [class.to-purple-600]="msg.tipo === 'espectador'">
                        {{ msg.jogador_nome.charAt(0).toUpperCase() }}
                      </div>
                    </div>

                    <!-- Message Content -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-1">
                        <span class="font-bold text-sm"
                              [class.text-blue-700]="msg.tipo === 'jogador'"
                              [class.text-purple-700]="msg.tipo === 'espectador'">
                          {{ msg.jogador_nome }}
                        </span>
                        @if (msg.tipo === 'espectador') {
                          <span class="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded-full font-medium flex items-center gap-1">
                            <i class="pi pi-eye text-xs"></i>
                            Espectador
                          </span>
                        } @else {
                          <span class="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full font-medium flex items-center gap-1">
                            <i class="pi pi-user text-xs"></i>
                            Jogador
                          </span>
                        }
                        <span class="text-xs text-gray-400 ml-auto">
                          {{ formatTime(msg.timestamp) }}
                        </span>
                      </div>
                      <div class="bg-white rounded-lg shadow-sm px-3 py-2 border"
                           [class.border-blue-200]="msg.tipo === 'jogador'"
                           [class.border-purple-200]="msg.tipo === 'espectador'">
                        <p class="text-gray-800 text-sm leading-relaxed break-words">
                          {{ msg.mensagem }}
                        </p>
                      </div>
                    </div>
                  </div>
                }
              </div>

              <!-- Chat Input -->
              <div class="p-4 bg-white border-t border-gray-200">
                <div class="flex gap-2">
                  <div class="flex-1 relative">
                    <input
                      pInputText
                      [(ngModel)]="chatMessage"
                      (keyup.enter)="sendMessage()"
                      placeholder="Digite sua mensagem..."
                      class="w-full pr-12 rounded-lg border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                      maxlength="500"
                    />
                    <span class="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
                      {{ chatMessage.length }}/500
                    </span>
                  </div>
                  <button
                    pButton
                    icon="pi pi-send"
                    (click)="sendMessage()"
                    [disabled]="!chatMessage.trim()"
                    class="px-4"
                    [class.opacity-50]="!chatMessage.trim()"
                    severity="info"
                    [rounded]="true"
                  ></button>
                </div>
                <p class="text-xs text-gray-500 mt-2 flex items-center gap-1">
                  <i class="pi pi-info-circle"></i>
                  Pressione Enter para enviar
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Dialog -->
    <p-dialog
      [(visible)]="showError"
      header="Erro"
      [modal]="true"
      [closable]="true"
    >
      <p>{{ errorMessage() }}</p>
    </p-dialog>
  `
})
export class GameComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('chatContainer') private chatContainer?: ElementRef;

  gameState = signal<Sala | null>(null);
  errorMessage = signal<string>('');
  showError = false;
  chatMessage = '';
  private pollSubscription?: Subscription;
  private ws?: WebSocket;
  private shouldScrollChat = false;

  constructor(
    public gameService: GameService,
    private router: Router
  ) { }

  ngAfterViewChecked() {
    if (this.shouldScrollChat) {
      this.scrollChatToBottom();
      this.shouldScrollChat = false;
    }
  }

  ngOnInit() {
    if (!this.gameService.currentRoom()) {
      this.router.navigate(['/']);
      return;
    }

    this.loadGameState();
    this.startPolling();
    this.connectWebSocket();
  }

  ngOnDestroy() {
    this.stopPolling();
    this.disconnectWebSocket();
  }

  connectWebSocket() {
    const roomId = this.gameService.currentRoom();
    if (!roomId) return;

    const wsUrl = `ws://${window.location.hostname}:8002/ws/${roomId}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket conectado');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket recebeu:', data);

        // Mensagem vinda do Redis pub/sub (game_event)
        if (data.type === 'game_event' && data.evento === 'chat_mensagem' && data.dados) {
          const chatMsg: ChatMessage = {
            jogador_nome: data.dados.jogador_nome,
            mensagem: data.dados.mensagem,
            tipo: data.dados.tipo,
            timestamp: data.dados.timestamp
          };
          this.gameService.addChatMessage(chatMsg);
          this.shouldScrollChat = true;
        }
        // Mensagem de chat direta (fallback)
        else if (data.type === 'chat_message') {
          const chatMsg: ChatMessage = {
            jogador_nome: data.sender,
            mensagem: data.message,
            tipo: 'jogador',
            timestamp: Date.now()
          };
          this.gameService.addChatMessage(chatMsg);
          this.shouldScrollChat = true;
        }
        // Atualizar estado do jogo
        else if (data.type === 'state_update' || data.type === 'initial_state') {
          this.gameState.set(data.room);
          this.gameService.updateGameState(data.room);
        }
        // Outros eventos do jogo
        else if (data.type === 'game_event') {
          console.log('Evento do jogo:', data.evento, data.dados);
          // Recarregar estado após jogadas, vitórias, etc.
          if (['jogada_realizada', 'jogo_vitoria', 'jogo_empate', 'jogo_reiniciado'].includes(data.evento)) {
            this.loadGameState();
          }
        }
      } catch (e) {
        console.error('Erro ao processar mensagem WebSocket:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error('Erro WebSocket:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket desconectado');
    };
  }

  disconnectWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = undefined;
    }
  }

  loadGameState() {
    const roomId = this.gameService.currentRoom();
    if (!roomId) return;

    this.gameService.getRoomState(roomId).subscribe({
      next: (state) => {
        this.gameState.set(state);
        this.gameService.updateGameState(state);
      },
      error: (error) => {
        this.showErrorDialog('Erro ao carregar estado do jogo');
      }
    });
  }

  startPolling() {
    // Poll every 1 second
    this.pollSubscription = interval(1000).subscribe(() => {
      this.loadGameState();
    });
  }

  stopPolling() {
    if (this.pollSubscription) {
      this.pollSubscription.unsubscribe();
    }
  }

  makeMove(position: number) {
    const roomId = this.gameService.currentRoom();
    const playerName = this.gameService.currentPlayer();

    if (!roomId || !playerName) return;

    this.gameService.makeMove(roomId, playerName, position).subscribe({
      next: (response) => {
        this.gameState.set(response.sala);
        this.gameService.updateGameState(response.sala);
      },
      error: (error) => {
        const errorMsg = error.error?.erro || 'Erro ao fazer jogada';
        this.showErrorDialog(errorMsg);
      }
    });
  }

  canPlay(position: number): boolean {
    const state = this.gameState();
    if (!state) return false;
    if (state.vencedor || state.empate) return false;
    if (state.tabuleiro[position] !== '') return false;
    if (this.gameService.userType() === 'espectador') return false;
    if (!this.isMyTurn()) return false;
    if (this.playersCount() < 2) return false;
    return true;
  }

  isMyTurn(): boolean {
    if (this.gameService.userType() === 'espectador') return false;
    const state = this.gameState();
    const mySymbol = this.gameService.currentSymbol();
    return state?.vez === mySymbol;
  }

  playersCount(): number {
    return this.gameState()?.jogadores.length || 0;
  }

  spectatorsCount(): number {
    return this.gameState()?.espectadores?.length || 0;
  }

  sendMessage() {
    const message = this.chatMessage.trim();
    if (!message) return;

    const roomId = this.gameService.currentRoom();
    const playerName = this.gameService.currentPlayer();

    if (!roomId || !playerName) {
      console.error('Room ID ou Player Name não definidos', { roomId, playerName });
      return;
    }

    console.log('Enviando mensagem de chat:', { roomId, playerName, message });

    this.gameService.sendChatMessage(roomId, playerName, message).subscribe({
      next: (response) => {
        console.log('Mensagem enviada com sucesso:', response);
        this.chatMessage = '';
        this.shouldScrollChat = true;
      },
      error: (error) => {
        console.error('Erro ao enviar mensagem:', error);
        this.showErrorDialog('Erro ao enviar mensagem no chat');
      }
    });
  }

  scrollChatToBottom() {
    try {
      if (this.chatContainer) {
        this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
      }
    } catch (err) {
      console.error('Erro ao fazer scroll do chat:', err);
    }
  }

  formatTime(timestamp: number): string {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  }

  currentTurnPlayer(): string {
    const state = this.gameState();
    if (!state) return '';
    return state.nomes?.[state.vez] || state.vez;
  }

  getWinnerName(): string {
    const state = this.gameState();
    if (!state?.vencedor) return '';
    return state.nomes?.[state.vencedor] || state.vencedor;
  }

  copyRoomId() {
    const roomId = this.gameService.currentRoom();
    if (roomId) {
      navigator.clipboard.writeText(roomId);
    }
  }

  playAgain() {
    const roomId = this.gameService.currentRoom();
    if (!roomId) return;

    this.gameService.restartGame(roomId).subscribe({
      next: (response) => {
        this.gameState.set(response.sala);
        this.gameService.updateGameState(response.sala);
      },
      error: (error) => {
        this.showErrorDialog('Erro ao reiniciar jogo');
      }
    });
  }

  exitGame() {
    this.gameService.resetGame();
    this.router.navigate(['/']);
  }

  showErrorDialog(message: string) {
    this.errorMessage.set(message);
    this.showError = true;
  }
}
