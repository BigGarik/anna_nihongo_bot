from tortoise import fields, models


class Payment(models.Model):
    id = fields.UUIDField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='payment')
    type_subscription = fields.ForeignKeyField('models.TypeSubscription', related_name='payment')

    payload = fields.CharField(max_length=250, null=True)
    status = fields.CharField(max_length=50, null=True)
    amount_value = fields.DecimalField(max_digits=10, decimal_places=2)
    amount_currency = fields.CharField(max_length=3)
    income_amount_value = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    income_amount_currency = fields.CharField(max_length=3, null=True)
    payment_method_id = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "payments"
