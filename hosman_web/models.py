from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

# Create your models here.

class Dummy(models.Model):
    pass

class Patient(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    class Gender(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"
    gender = models.CharField(max_length=6, choices=Gender.choices, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.OneToOneField('Address', on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.ForeignKey(
            'GContent',
            on_delete=models.SET_NULL,
            null=True,
            blank=True
            )
    varified = models.BooleanField(default=False)
    def __str__(self):
        if self.first_name is not None:
            first = self.first_name
        else:
            first = "NULL:FirstName"
        if self.last_name is not None:
            last = self.last_name
        else:
            last = "NULL: LastName"
        return first + ' ' + last

class CUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,username, password=None):
        user = self.create_user(username=username, password=password)
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.is_manager = True
        user.save(using=self._db)
        pt = Patient.objects.create(user=user)
        pt.profile_picture = Patient.objects.get(user__username="default").profile_picture
        pt.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=200, unique=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    objects = CUserManager()
    def has_perm(self, perm, obj=None):
        return True
    def has_module_perms(self, app_label):
        return True
    def __str__(self):
        return self.username

class Address(models.Model):
    address_line_1 = models.CharField(max_length=150, null=True, blank=True)
    address_line_2 = models.CharField(max_length=150, null=True, blank=True)
    country = models.CharField(max_length=50, default="other")
    province = models.CharField(max_length=50, default='other')
    state = models.CharField(max_length=50, default='other')
    city = models.CharField(max_length=50, default='other')
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    def __str__(self):
        obj = ''
        if self.address_line_1 is not None:
                obj = obj + self.address_line_1 + ' '
        if self.address_line_2 is not None:
                obj = obj + self.address_line_2 + ' '
        obj = obj + self.city + ' '
        if self.zip_code is not None:
                obj = obj + '- ' + self.zip_code + ' '
        obj = obj + self.state + ' ' + self.province + ' ' + self.country
        return obj

class GContent(models.Model):
    content = models.FileField()
    class TypeVideo(models.IntegerChoices):
        VIDEO = 1
        IMAGE = 0
        SCRIPT = 2
    content_type = models.IntegerField(
        choices=TypeVideo.choices,
        default=TypeVideo.IMAGE
        )
    belongs_to = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE
        )