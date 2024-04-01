import uuid
from model_utils import Choices
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MinLengthValidator, RegexValidator
from django.db import models


class AbstarctBaseModel(models.Model):

    created = models.DateTimeField(auto_now_add=True, editable=True)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class User(AbstractUser):
    """Пользователь"""

    username = models.CharField( # в качестве логина используем номер телефона
        verbose_name='Телефон', max_length=16,
        validators=[MinLengthValidator(12),
                    RegexValidator(regex=r'^\+?1?\d{11}$',
                                   message='Телефон должен быть в формате: +7999999999')],
        unique=True
    )
    middle_name = models.CharField(verbose_name='Отчество', max_length=150, blank=True, null=True)

    def __str__(self):
        return f'{self.id} {self.last_name} {self.first_name} {self.middle_name}'


class Account(AbstarctBaseModel):
    """Счет (кошелек)"""

    CURRENCY_TYPE = Choices(
        (1, 'usd', 'Доллар США'),
        (2, 'rur', 'Российский Рубль'),
    )

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.SET_NULL, null=True)
    currency = models.IntegerField(verbose_name='Тип валюты', choices=CURRENCY_TYPE, default=CURRENCY_TYPE.usd)
    number = models.UUIDField(verbose_name='Номер счета', default=uuid.uuid4)
    balance = models.DecimalField(
        verbose_name='Баланс',
        max_digits=11,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = 'Счет'
        verbose_name_plural = 'Счета'

    def __str__(self):
        return f'{self.id} {self.number}'


class Transaction(AbstarctBaseModel):
    """Транзакция"""

    PAYMENT_TYPE = Choices(
        (1, 'debit', 'Списание'),
        (2, 'credit', 'Пополнение'),
    )

    sender_account = models.ForeignKey(
        Account,
        verbose_name='Счет отправителя',
        on_delete=models.SET_NULL, null=True,
        related_name='sender_account',
    )
    reciever_account = models.ForeignKey(
        Account,
        verbose_name='Счет получателя',
        on_delete=models.SET_NULL,
        null=True,
        related_name='receiver_account',
    )

    currency = models.IntegerField(verbose_name='Тип валюты', choices=Account.CURRENCY_TYPE,
                                   default=Account.CURRENCY_TYPE.usd)
    description = models.CharField(verbose_name='Назначение платежа', max_length=300)
    amount = models.DecimalField(
        verbose_name='Сумма',
        max_digits=11,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    transaction_type = models.IntegerField(verbose_name='Тип платежа', choices=PAYMENT_TYPE)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f'{self.id}'
