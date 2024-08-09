from tortoise import fields, models


class TypeSubscription(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    price = fields.IntField(null=True)
    months = fields.IntField(null=True)
    description = fields.TextField(null=True)
    payload = fields.CharField(max_length=250, null=True)

    def __str__(self):
        return f"{self.name}"


class Subscription(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='subscription')
    type_subscription = fields.ForeignKeyField('models.TypeSubscription', related_name='subscription')
    payment_token = fields.CharField(max_length=255, null=True)
    date_start = fields.DateField()
    date_end = fields.DateField(null=True)

    def __str__(self):
        return f"{self.type_subscription}"
