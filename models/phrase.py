from tortoise import fields, models
from aiogram.utils.i18n import gettext as _


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()


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


class OriginalPhrase(models.Model):
    id = fields.IntField(pk=True)
    slug = fields.CharField(max_length=255, unique=True)
    audio = fields.ForeignKeyField('models.AudioFile', related_name='phrases_audio')
    category = fields.ForeignKeyField('models.Category', related_name='categories')
    text = fields.CharField(max_length=255, unique=True)
    translation = fields.TextField()
    comment = fields.TextField()
    plot_image = fields.BinaryField()
    image = fields.BinaryField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.text[:20]}..."


class LexisPhrase(models.Model):
    id = fields.IntField(pk=True)
    phrase = fields.CharField(max_length=255, unique=True)
    spaced_phrase = fields.CharField(max_length=255, unique=True)
    group = fields.ForeignKeyField('models.UserGroup', related_name='lexis_group', null=True)
    teacher = fields.ForeignKeyField('models.Teacher', related_name='lexis_teacher', null=True)
    user = fields.ForeignKeyField('models.User', related_name='lexis_user', null=True)
