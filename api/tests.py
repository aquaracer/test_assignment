from django.db.models import Q
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer
from .models import User


class AccountTests(APITestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(
            username='+79999999999',
            password='qwerty123456',
            first_name='Иван',
            middle_name='Иванович',
            last_name='Иванов',
        )

        self.user_2 = User.objects.create_user(
            username='+79999999998',
            password='qwerty1234569',
            first_name='Петр',
            middle_name='Петрович',
            last_name='Петров',
        )

        account_user_1_rur = Account.objects.create(
            user=self.user_1,
            currency=Account.CURRENCY_TYPE.rur,
            balance=10
        )
        account_user_2_rur = Account.objects.create(
            user=self.user_2,
            currency=Account.CURRENCY_TYPE.rur,
            balance=100
        )
        account_user_1_usd = Account.objects.create(
            user=self.user_1,
            currency=Account.CURRENCY_TYPE.usd,
            balance=10
        )
        account_user_2_usd = Account.objects.create(
            user=self.user_2,
            currency=Account.CURRENCY_TYPE.usd,
            balance=100
        )

        transactions = [
            Transaction(
                sender_account=account_user_1_rur,
                reciever_account=account_user_2_rur,
                currency=Account.CURRENCY_TYPE.rur,
                description='перевод средств другому пользователю',
                amount=100,
                transaction_type=Transaction.PAYMENT_TYPE.debit,
            ),
            Transaction(
                sender_account=account_user_1_rur,
                reciever_account=account_user_2_rur,
                currency=Account.CURRENCY_TYPE.rur,
                description='перевод средств другому пользователю',
                amount=10,
                transaction_type=Transaction.PAYMENT_TYPE.debit,
            ),
            Transaction(
                sender_account=account_user_1_usd,
                reciever_account=account_user_2_usd,
                currency=Account.CURRENCY_TYPE.usd,
                description='перевод средств другому пользователю',
                amount=100,
                transaction_type=Transaction.PAYMENT_TYPE.debit,
            ),
            Transaction(
                sender_account=account_user_1_usd,
                reciever_account=account_user_2_usd,
                currency=Account.CURRENCY_TYPE.usd,
                description='перевод средств другому пользователю',
                amount=10,
                transaction_type=Transaction.PAYMENT_TYPE.debit,
            ),
        ]

        Transaction.objects.bulk_create(transactions)

        self.user_1_token = Token.objects.create(user=self.user_1)
        self.user_2_token = Token.objects.create(user=self.user_2)

        Account.objects.filter(user=self.user_1, сurrency=Account.CURRENCY_TYPE.usd).update(balance=100)

    def test_user_account_list(self):
        """Список счетов пользователя"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        response = self.client.get(f'/api/v1/account/')
        serializer_data = AccountSerializer(Account.objects.filter(user=self.user_1), many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_transfer_funds_counterparty(self):
        """Перевед средств другому пользователю"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        senders_account = Account.objects.get(user=self.user_1, сurrency_id='1')
        receivers_account = Account.objects.get(user=self.user_2, сurrency_id='1')
        senders_old_balance = senders_account.balance
        receivers_old_balance = receivers_account.balance

        data = {
            "senders_account": senders_account.number,
            "amount_to_send": "100",
            "receivers_account": receivers_account.number,
        }

        response = self.client.post('/api/v1/transaction/', data, format='json')
        senders_new_balance = Account.objects.get(number=senders_account.number).balance
        receivers_new_balance = Account.objects.get(number=receivers_account.number).balance
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(senders_old_balance - 100, senders_new_balance)
        self.assertEqual(receivers_old_balance + 100, receivers_new_balance)

    def test_get_user_transactions(self):
        """Получить историю операций пользователя"""

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user_1_token))
        response = self.client.get(f'/api/v1/transaction/')
        serializer_data = TransactionSerializer(Transaction.objects.filter(
            Q(sender_account__user=self.user_1, transaction_type=Transaction.PAYMENT_TYPE.debit) |
            Q(reciever_account__user=self.user_2, transaction_type=Transaction.PAYMENT_TYPE.credit)
        ).order_by('-created')[:2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer_data)

