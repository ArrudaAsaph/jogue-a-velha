from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .room_manager import room_manager
from .serializers import JoinRoomSerializer, MoveSerializer, RoomStateSerializer
from .utils import TicTacToeGame


@swagger_auto_schema(
    method='post',
    request_body=JoinRoomSerializer,
    responses={
        200: openapi.Response(
            description="Sucesso ao entrar na sala",
            examples={
                "application/json": {
                    "message": "joined",
                    "player": "O",
                    "roomId": "192.168.0.23:5580"
                }
            }
        ),
        400: "Requisição inválida",
        404: "Sala não encontrada",
        409: "Sala já está cheia"
    }
)
@api_view(['POST'])
def join_room(request):
    """
    Endpoint para um jogador entrar em uma sala existente

    O jogador será registrado como 'O' e o status da sala mudará para 'playing'
    """
    serializer = JoinRoomSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"error": "Dados inválidos", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    room_id = serializer.validated_data['roomId']
    player_ip = serializer.validated_data.get('playerIp') or request.META.get('REMOTE_ADDR', 'unknown')

    # Busca a sala em memória
    room = room_manager.find_one({"roomId": room_id})

    if not room:
        return Response(
            {"error": "Sala não encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verifica se a sala já está cheia
    if room.get('player2') is not None:
        return Response(
            {"error": "Sala já está cheia"},
            status=status.HTTP_409_CONFLICT
        )

    # Atualiza a sala com o segundo jogador
    room_manager.update_one(
        {"roomId": room_id},
        {
            "$set": {
                "player2": {
                    "id": "O",
                    "ip": player_ip
                },
                "status": "playing"
            }
        }
    )

    return Response(
        {
            "message": "joined",
            "player": "O",
            "roomId": room_id
        },
        status=status.HTTP_200_OK
    )


@swagger_auto_schema(
    method='post',
    request_body=MoveSerializer,
    responses={
        200: openapi.Response(
            description="Jogada realizada com sucesso",
            examples={
                "application/json": {
                    "board": ["X", " ", " ", " ", "O", " ", " ", " ", " "],
                    "turn": "X",
                    "status": "playing",
                    "winner": None
                }
            }
        ),
        400: "Jogada inválida",
        404: "Sala não encontrada",
        409: "Não é seu turno"
    }
)
@api_view(['POST'])
def make_move(request):
    """
    Endpoint para realizar uma jogada

    Valida o turno, a posição e atualiza o tabuleiro
    Verifica vitória ou empate após cada jogada
    """
    serializer = MoveSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {"error": "Dados inválidos", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    room_id = serializer.validated_data['roomId']
    player = serializer.validated_data['player']
    position = serializer.validated_data['position']

    # Busca a sala em memória
    room = room_manager.find_one({"roomId": room_id})

    if not room:
        return Response(
            {"error": "Sala não encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verifica se o jogo já terminou
    if room['status'] == 'finished':
        return Response(
            {"error": "Jogo já finalizado"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verifica se é o turno do jogador
    if room['turn'] != player:
        return Response(
            {"error": f"Não é seu turno. Turno atual: {room['turn']}"},
            status=status.HTTP_409_CONFLICT
        )

    # Valida a jogada
    board = room['board']
    if not TicTacToeGame.is_valid_move(board, position):
        return Response(
            {"error": "Posição inválida ou já ocupada"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Realiza a jogada
    new_board = TicTacToeGame.make_move(board, position, player)

    # Verifica resultado
    winner = TicTacToeGame.check_winner(new_board)

    # Determina o novo status e próximo jogador
    if winner:
        new_status = 'finished'
        next_turn = room['turn']  # Mantém o turno se o jogo acabou
    else:
        new_status = 'playing'
        next_turn = TicTacToeGame.get_next_player(player)

    # Atualiza em memória
    room_manager.update_one(
        {"roomId": room_id},
        {
            "$set": {
                "board": new_board,
                "turn": next_turn,
                "status": new_status,
                "winner": winner
            }
        }
    )

    return Response(
        {
            "board": new_board,
            "turn": next_turn,
            "status": new_status,
            "winner": winner
        },
        status=status.HTTP_200_OK
    )


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'roomId',
            openapi.IN_QUERY,
            description="ID da sala",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Estado atual da sala",
            examples={
                "application/json": {
                    "roomId": "192.168.0.23:5580",
                    "board": ["X", " ", " ", " ", "O", " ", " ", " ", " "],
                    "turn": "X",
                    "status": "playing",
                    "winner": None,
                    "player1": {"id": "X", "ip": "192.168.0.23"},
                    "player2": {"id": "O", "ip": "192.168.0.50"}
                }
            }
        ),
        400: "Requisição inválida",
        404: "Sala não encontrada"
    }
)
@api_view(['GET'])
def get_room_state(request):
    """
    Endpoint para consultar o estado atual de uma sala

    Retorna tabuleiro, turno, status, vencedor e informações dos jogadores
    """
    room_id = request.query_params.get('roomId')

    if not room_id:
        return Response(
            {"error": "roomId é obrigatório"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Busca a sala em memória
    room = room_manager.find_one({"roomId": room_id})

    if not room:
        return Response(
            {"error": "Sala não encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(room, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="Status do serviço",
            examples={
                "application/json": {
                    "status": "online",
                    "service": "Jogo da Velha REST API",
                    "version": "1.0.0"
                }
            }
        )
    }
)
@api_view(['GET'])
def health_check(request):
    """
    Endpoint de health check para verificar se o serviço está funcionando
    """
    return Response(
        {
            "status": "online",
            "service": "Jogo da Velha REST API",
            "version": "1.0.0"
        },
        status=status.HTTP_200_OK
    )
