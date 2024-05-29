from tortoise import fields, models


class TextToSpeech(models.Model):
    id = fields.IntField(pk=True)
    voice_id = fields.CharField(max_length=255)
    user_id = fields.IntField()
    text = fields.CharField(max_length=255, unique=True)
    voice = fields.BinaryField()
    created_at = fields.DatetimeField(auto_now_add=True)
