from tortoise import fields, models
from aiogram.utils.i18n import gettext as _


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()


class UserPhrase(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='phrases')
    recognized_text = fields.TextField()
    audio = fields.BinaryField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return _("Пользователь {user} произнес {recognized_text}").format(user=self.user,
                                                                          recognized_text=self.recognized_text)


class OriginalPhrase(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    category = fields.ForeignKeyField('models.Category', related_name='categories')
    text = fields.TextField()
    translation = fields.TextField()
    comment = fields.TextField()
    plot_image = fields.BinaryField()
    image = fields.BinaryField()
    audio = fields.BinaryField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.text[:20]}..."
