"""
Serializers para validação de requisições REST
"""
from rest_framework import serializers


class JoinRoomSerializer(serializers.Serializer):
    """Serializer para entrar em uma sala"""
    roomId = serializers.CharField(required=True, max_length=255)
    playerIp = serializers.IPAddressField(required=False, allow_null=True)


class MoveSerializer(serializers.Serializer):
    """Serializer para fazer uma jogada"""
    roomId = serializers.CharField(required=True, max_length=255)
    player = serializers.ChoiceField(choices=['X', 'O'], required=True)
    position = serializers.IntegerField(required=True, min_value=0, max_value=8)


class RoomStateSerializer(serializers.Serializer):
    """Serializer para consultar estado da sala"""
    roomId = serializers.CharField(required=True, max_length=255)
