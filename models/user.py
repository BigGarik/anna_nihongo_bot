from tortoise import fields, models


class UserGroup(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, unique=True)


class User(models.Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=100, null=True)
    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=100, null=True)
    payment_method = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    language = fields.CharField(max_length=10, default='en')
    notifications = fields.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name}"


class Teacher(User):
    code = fields.CharField(max_length=100)
    group = fields.ManyToManyField('models.UserGroup', related_name='teachers', null=True)


class Student(User):
    teacher = fields.ManyToManyField('models.Teacher', related_name='students', null=True)
    group = fields.ManyToManyField('models.UserGroup', related_name='students', null=True)
