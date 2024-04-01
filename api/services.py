import logging

from django.db import DatabaseError, transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.serializers import Serializer

from .models import Account, Transaction

logger = logging.getLogger('__name__')


@transaction.atomic
def send_funds(serializer: Serializer, request: Request) -> None:
    """Перевод средств"""

    senders_account = serializer.validated_data.get('senders_account')
    amount = serializer.validated_data.get('amount_to_send')
    receivers_account = serializer.validated_data.get('receivers_account')

    if not Account.objects.filter(user=request.user, number=senders_account).exists():
        raise ValidationError(
            'Счет списания средств не принадлежит данному пользователю. Проверьте правильность счета и повторите попытку'
        )

    if not Account.objects.filter(number=receivers_account).exists():
        raise ValidationError(
            'Счет для получения средств не найден в системе. Проверьте правильность счета и повторите попытку'
        )

    sender = Account.objects.get(number=senders_account)
    receiver = Account.objects.get(number=receivers_account)

    if sender.currency != receiver.currency:
        raise ValidationError(
            'Валюта счета получателя должна соответствовать валюте счета отправителя'
        )

    if not Account.objects.filter(number=senders_account, balance__gte=amount).exists():
        raise ValidationError('На счете недостаточно средств')

    try:
        Account.objects.filter(number=senders_account).update(balance=F('balance') - amount)
    except DatabaseError as error:
        logger.error(msg={'Ошибка при обновлении баланса отправителя': error})
        raise DatabaseError('Ошибка при обновлении баланса отправителя', error)

    try:
        Account.objects.filter(number=receivers_account).update(balance=F('balance') + amount)
    except DatabaseError as error:
        logger.error(msg={'Ошибка при обновлении баланса получателя': error})
        raise DatabaseError('Ошибка при обновлении баланса получателя', error)

    try:
        batch = [
            Transaction(
                sender_account=sender,
                reciever_account=receiver,
                description='перевод средств другому пользователю',
                amount=amount,
                transaction_type=Transaction.PAYMENT_TYPE.debit,
            ),
            Transaction(
                sender_account=sender,
                reciever_account=receiver,
                description='зачисление средств от другого пользователя',
                amount=amount,
                transaction_type=Transaction.PAYMENT_TYPE.credit,
            ),
        ]
        Transaction.objects.bulk_create(batch)
    except DatabaseError as error:
        logger.error(msg={'Ошибка при создании операций': error})
        raise DatabaseError('Ошибка при создании операций', error)
