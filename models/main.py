from tortoise import fields, models


class MainPhoto(models.Model):
    id = fields.IntField(pk=True)
    tg_id = fields.CharField(max_length=255)
