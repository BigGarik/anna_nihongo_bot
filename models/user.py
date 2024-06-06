from tortoise import fields, models


class UserGroup(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, unique=True)


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=100, unique=True)
    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name}"


class Teacher(User):
    id = fields.CharField(max_length=100, pk=True)


class Student(User):
    id = fields.IntField(pk=True)
    group = fields.ManyToManyField('models.UserGroup', related_name='user_group', null=True)
    teacher = fields.ManyToManyField('models.Teacher', related_name='teacher', null=True)
