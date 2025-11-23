"""
Utilitários e lógica do jogo da velha
"""


class TicTacToeGame:
    """Classe para lógica do jogo da velha"""

    @staticmethod
    def check_winner(board):
        """
        Verifica se há um vencedor no tabuleiro

        Args:
            board: Lista de 9 elementos representando o tabuleiro

        Returns:
            'X', 'O', 'draw' ou None
        """
        # Combinações vencedoras
        winning_combinations = [
            [0, 1, 2],  # Linha 1
            [3, 4, 5],  # Linha 2
            [6, 7, 8],  # Linha 3
            [0, 3, 6],  # Coluna 1
            [1, 4, 7],  # Coluna 2
            [2, 5, 8],  # Coluna 3
            [0, 4, 8],  # Diagonal principal
            [2, 4, 6],  # Diagonal secundária
        ]

        # Verifica vitória
        for combo in winning_combinations:
            if (board[combo[0]] == board[combo[1]] == board[combo[2]]
                and board[combo[0]] in ['X', 'O']):
                return board[combo[0]]

        # Verifica empate (tabuleiro cheio)
        if ' ' not in board:
            return 'draw'

        return None

    @staticmethod
    def is_valid_move(board, position):
        """
        Verifica se uma jogada é válida

        Args:
            board: Lista de 9 elementos representando o tabuleiro
            position: Posição da jogada (0-8)

        Returns:
            Boolean indicando se a jogada é válida
        """
        if position < 0 or position > 8:
            return False

        return board[position] == ' '

    @staticmethod
    def make_move(board, position, player):
        """
        Realiza uma jogada no tabuleiro

        Args:
            board: Lista de 9 elementos representando o tabuleiro
            position: Posição da jogada (0-8)
            player: 'X' ou 'O'

        Returns:
            Novo tabuleiro atualizado
        """
        new_board = board.copy()
        new_board[position] = player
        return new_board

    @staticmethod
    def get_next_player(current_player):
        """
        Retorna o próximo jogador

        Args:
            current_player: 'X' ou 'O'

        Returns:
            'O' se current_player é 'X', senão 'X'
        """
        return 'O' if current_player == 'X' else 'X'
