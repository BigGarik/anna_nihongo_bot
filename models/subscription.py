from tortoise import fields, models


class TypeSubscription(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    price = fields.FloatField(null=True)
    day = fields.IntField(null=True)

    def __str__(self):
        return f"{self.name}"


class Subscription(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='subscription')
    type_subscription = fields.ForeignKeyField('models.TypeSubscription', related_name='subscription')
    date_start = fields.DateField()
    date_end = fields.DateField(null=True)

    def __str__(self):
        return f"{self.type_subscription}"
