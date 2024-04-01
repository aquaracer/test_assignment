from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Account, Transaction
from api.serializers import AccountSerializer, TransactionSerializer, CreateTransactionSerializer, \
    AccountCreateSerializer
from api.services import send_funds


class AccountViewSet(ModelViewSet):
    """CRUD кошелька"""

    permission_classes = [IsAuthenticated, ]
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AccountCreateSerializer
        else:
            return AccountSerializer


class TransactionViewSet(ModelViewSet):
    """CRUD операции"""

    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Transaction.objects.filter(
            Q(sender_account__user=self.request.user, transaction_type=Transaction.PAYMENT_TYPE.debit) |
            Q(reciever_account__user=self.request.user, transaction_type=Transaction.PAYMENT_TYPE.credit)
        ).prefetch_related('sender_account', 'reciever_account').order_by('-created')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransactionSerializer
        else:
            return TransactionSerializer

    def create(self, request, *args, **kwargs):
        """Создание операции"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_funds(serializer, request)
        return Response()
