from django.contrib import admin
from .models import User, Account, Transaction


class AccountInline(admin.TabularInline):
    model = Account
    extra = 0
    readonly_fields = ('number', 'balance', 'currency')
    show_change_link = True


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('sender_account', 'reciever_account', 'description', 'amount', 'transaction_type', 'currency')
    fk_name = 'sender_account'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [AccountInline]


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    inlines = [TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
