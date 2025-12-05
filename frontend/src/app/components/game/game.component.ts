import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { DialogModule } from 'primeng/dialog';
import { GameService, Sala } from '../../services/game.service';
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
    DialogModule
  ],
  template: `
    <div class="min-h-screen p-4">
      <div class="max-w-4xl mx-auto">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div class="flex justify-between items-center">
            <div>
              <h1 class="text-3xl font-bold text-blue-600">Jogo da Velha</h1>
              <p class="text-gray-600 mt-1">
                Você é: <span class="font-bold">{{ gameService.currentPlayer() }}</span>
                (<span class="font-bold text-blue-600">{{ gameService.currentSymbol() }}</span>)
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

        <!-- Game Info -->
        <div class="grid md:grid-cols-2 gap-4 mb-6">
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
          <div class="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6 mt-6">
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

        <!-- Chat -->
        <div class="bg-white rounded-lg shadow-lg p-6 mt-6">
          <h3 class="text-lg font-bold mb-4">Chat da Sala</h3>
          <div class="space-y-2 max-h-60 overflow-y-auto border rounded p-3 bg-gray-50">
            @for (msg of gameService.chatMessages(); track $index) {
              <div class="text-sm">
                <span class="font-semibold">{{ msg.sender }}</span>:
                <span>{{ msg.message }}</span>
                <span class="text-gray-400 text-xs"> — {{ formatTime(msg.timestamp) }}</span>
              </div>
            }
            @if (!gameService.chatMessages().length) {
              <div class="text-gray-500 text-sm">Nenhuma mensagem ainda.</div>
            }
          </div>
          <div class="flex gap-2 mt-3">
            <input
              type="text"
              [(ngModel)]="chatInput"
              placeholder="Digite sua mensagem"
              class="flex-1 px-3 py-2 border rounded"
            />
            <button pButton label="Enviar" icon="pi pi-send" (click)="sendChat()" [disabled]="!canSendChat()"></button>
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
export class GameComponent implements OnInit, OnDestroy {
  gameState = signal<Sala | null>(null);
  errorMessage = signal<string>('');
  showError = false;
  private pollSubscription?: Subscription;
  chatInput = '';

  constructor(
    public gameService: GameService,
    private router: Router
  ) {}

  ngOnInit() {
    if (!this.gameService.currentRoom()) {
      this.router.navigate(['/']);
      return;
    }

    this.loadGameState();
    this.gameService.connectToRoom(this.gameService.currentRoom() as string);
  }

  ngOnDestroy() {
    this.stopPolling();
    this.gameService.disconnectFromRoom();
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
    if (!this.isMyTurn()) return false;
    if (this.playersCount() < 2) return false;
    return true;
  }

  isMyTurn(): boolean {
    const state = this.gameState();
    const mySymbol = this.gameService.currentSymbol();
    return state?.vez === mySymbol;
  }

  playersCount(): number {
    return this.gameState()?.jogadores.length || 0;
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

  canSendChat(): boolean {
    return !!this.chatInput.trim() && !!this.gameService.currentPlayer();
  }

  sendChat() {
    const sender = this.gameService.currentPlayer();
    if (!sender || !this.chatInput.trim()) return;
    this.gameService.sendChat(sender, this.chatInput.trim());
    this.chatInput = '';
  }

  formatTime(ts: string): string {
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString();
    } catch {
      return ts;
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
