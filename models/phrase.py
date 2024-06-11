from tortoise import fields, models
from aiogram.utils.i18n import gettext as _


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    user = fields.ForeignKeyField('models.User', related_name='categories', null=True)


class AudioFile(models.Model):
    id = fields.IntField(pk=True)
    tg_id = fields.IntField(null=True)
    audio = fields.BinaryField()


class UserPhrase(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='user_phrases')
    recognized_text = fields.TextField()
    audio = fields.ForeignKeyField('models.AudioFile', related_name='user_phrases_audio')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return _("Пользователь {user} произнес {recognized_text}").format(user=self.user,
                                                                          recognized_text=self.recognized_text)


class PronunciationCategory(models.Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()


class PronunciationPhrase(models.Model):
    id = fields.IntField(pk=True)
    slug = fields.CharField(max_length=255, unique=True, null=True)

    category = fields.ForeignKeyField('models.PronunciationCategory', related_name='categories')
    text = fields.CharField(max_length=255, unique=True)
    translation = fields.TextField()

    audio = fields.ForeignKeyField('models.AudioFile', related_name='phrases_audio')
    comment = fields.TextField(null=True)
    plot_image = fields.BinaryField(null=True)
    image = fields.BinaryField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.text[:20]}..."


class LexisPhrase(models.Model):
    id = fields.IntField(pk=True)
    category = fields.ForeignKeyField('models.Category', related_name='lexis_phrases')
    phrase = fields.CharField(max_length=255, unique=True)
    spaced_phrase = fields.CharField(max_length=255, unique=True)
    group = fields.ForeignKeyField('models.UserGroup', related_name='lexis_phrases', null=True)
    teacher = fields.ForeignKeyField('models.Teacher', related_name='lexis_phrases', null=True)
    user = fields.ForeignKeyField('models.User', related_name='lexis_phrases', null=True)
