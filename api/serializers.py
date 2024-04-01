from rest_framework import serializers

from api.models import Account, Transaction


class AccountCreateSerializer(serializers.ModelSerializer):
    """Создание кошелька"""

    class Meta:
        model = Account
        exclude = ('number',)


class AccountSerializer(serializers.ModelSerializer):
    """Кошелек"""

    class Meta:
        model = Account
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    """Операция"""

    class Meta:
        model = Transaction
        fields = '__all__'


class CreateTransactionSerializer(serializers.Serializer):
    """Совершение операции"""

    senders_account = serializers.UUIDField(required=True)
    amount_to_send = serializers.DecimalField(required=True, min_value=0.01, max_digits=11, decimal_places=2)
    receivers_account = serializers.UUIDField(required=True)


