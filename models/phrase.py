from tortoise import fields, models


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    user = fields.ForeignKeyField('models.User', related_name='categories', null=True)
    public = fields.BooleanField(default=False)


class AudioFile(models.Model):
    id = fields.IntField(pk=True)
    tg_id = fields.CharField(max_length=255, null=True)
    audio = fields.BinaryField()


class UserAnswer(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='user_answers')
    phrase = fields.ForeignKeyField('models.Phrase', related_name='user_answers')

    answer_text = fields.CharField(max_length=255, null=True)
    audio_id = fields.CharField(max_length=255, null=True)
    result = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)


class Phrase(models.Model):
    id = fields.IntField(pk=True)

    text_phrase = fields.CharField(max_length=255, unique=True)
    spaced_phrase = fields.CharField(max_length=255, unique=True)
    translation = fields.CharField(max_length=255, null=True)

    category = fields.ForeignKeyField('models.Category', related_name='phrases')
    audio_id = fields.CharField(max_length=255, null=True)
    user = fields.ForeignKeyField('models.User', related_name='phrases', null=True)
    group = fields.ForeignKeyField('models.UserGroup', related_name='phrases', null=True)
    teacher = fields.ForeignKeyField('models.Teacher', related_name='phrases', null=True)

    plot_image = fields.BinaryField(null=True)
    image_id = fields.CharField(max_length=255, null=True)
    comment = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text_phrase[:200]}..."
