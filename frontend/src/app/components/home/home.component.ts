import { Component, signal } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { CardModule } from 'primeng/card';
import { MessageModule } from 'primeng/message';
import { GameService } from '../../services/game.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    InputTextModule,
    CardModule,
    MessageModule
  ],
  template: `
    <div class="min-h-screen flex items-center justify-center p-4">
      <div class="max-w-2xl w-full">
        <div class="text-center mb-8">
          <h1 class="text-5xl font-bold text-blue-600 mb-2">Jogo da Velha</h1>
          <p class="text-gray-600">Escolha uma opção para começar</p>
        </div>

        <div class="grid md:grid-cols-2 gap-6">
          <!-- Criar Sala -->
          <p-card styleClass="h-full">
            <ng-template pTemplate="header">
              <div class="p-4 bg-blue-50">
                <h2 class="text-2xl font-bold text-blue-700">Criar Nova Sala</h2>
              </div>
            </ng-template>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium mb-2">Seu Nome</label>
                <input
                  type="text"
                  pInputText
                  [(ngModel)]="createName"
                  placeholder="Digite seu nome"
                  class="w-full"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">Porta (opcional)</label>
                <input
                  type="text"
                  pInputText
                  [(ngModel)]="porta"
                  placeholder="Ex: 8080"
                  class="w-full"
                />
              </div>
              @if (createError()) {
                <p-message severity="error" [text]="createError()!" styleClass="w-full" />
              }
              <button
                pButton
                label="Criar Sala"
                icon="pi pi-plus"
                [loading]="isCreating()"
                (click)="createRoom()"
                class="w-full"
                [disabled]="!createName.trim()"
              ></button>
            </div>
          </p-card>

          <!-- Entrar em Sala -->
          <p-card styleClass="h-full">
            <ng-template pTemplate="header">
              <div class="p-4 bg-green-50">
                <h2 class="text-2xl font-bold text-green-700">Entrar em Sala</h2>
              </div>
            </ng-template>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium mb-2">Seu Nome</label>
                <input
                  type="text"
                  pInputText
                  [(ngModel)]="joinName"
                  placeholder="Digite seu nome"
                  class="w-full"
                />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">ID da Sala</label>
                <input
                  type="text"
                  pInputText
                  [(ngModel)]="roomId"
                  placeholder="Cole o ID da sala"
                  class="w-full"
                />
              </div>
              @if (joinError()) {
                <p-message severity="error" [text]="joinError()!" styleClass="w-full" />
              }
              <button
                pButton
                label="Entrar"
                icon="pi pi-sign-in"
                [loading]="isJoining()"
                (click)="joinRoom()"
                class="w-full"
                [disabled]="!joinName.trim() || !roomId.trim()"
              ></button>
            </div>
          </p-card>
        </div>
      </div>
    </div>
  `
})
export class HomeComponent {
  createName = '';
  porta = '8080';
  joinName = '';
  roomId = '';

  isCreating = signal(false);
  isJoining = signal(false);
  createError = signal<string | null>(null);
  joinError = signal<string | null>(null);

  constructor(
    private gameService: GameService,
    private router: Router
  ) { }

  createRoom() {
    this.createError.set(null);
    this.isCreating.set(true);

    this.gameService.createRoom(this.porta || '8080').subscribe({
      next: (response) => {
        const roomId = response.room_id;
        this.gameService.setCurrentRoom(roomId);

        // Join the room automatically
        this.gameService.joinRoom(roomId, this.createName).subscribe({
          next: (joinResponse) => {
            const userType = joinResponse.tipo || 'jogador';
            const symbol = joinResponse.seu_simbolo || joinResponse.sala.jogadores[0];
            this.gameService.setCurrentPlayer(this.createName, symbol, userType);
            this.gameService.updateGameState(joinResponse.sala);
            this.isCreating.set(false);
            this.router.navigate(['/game']);
          },
          error: (error) => {
            this.isCreating.set(false);
            this.createError.set('Erro ao entrar na sala criada');
          }
        });
      },
      error: (error) => {
        this.isCreating.set(false);
        this.createError.set('Erro ao criar sala. Verifique se o servidor está rodando.');
      }
    });
  }

  joinRoom() {
    this.joinError.set(null);
    this.isJoining.set(true);

    this.gameService.joinRoom(this.roomId, this.joinName).subscribe({
      next: (response) => {
        const userType = response.tipo || 'jogador';
        const symbol = response.seu_simbolo || (response.tipo === 'espectador' ? '' : response.sala.jogadores[response.sala.jogadores.length - 1]);
        this.gameService.setCurrentRoom(this.roomId);
        this.gameService.setCurrentPlayer(this.joinName, symbol, userType);
        this.gameService.updateGameState(response.sala);
        this.isJoining.set(false);
        this.router.navigate(['/game']);
      },
      error: (error) => {
        this.isJoining.set(false);
        const errorMsg = error.error?.erro || 'Erro ao entrar na sala';
        this.joinError.set(errorMsg);
      }
    });
  }
}
