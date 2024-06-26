from tortoise import fields, models


class Payments(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='payments')
    created_at = fields.DatetimeField(auto_now_add=True)
