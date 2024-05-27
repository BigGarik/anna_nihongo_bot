from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100, unique=True)
    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name}"
