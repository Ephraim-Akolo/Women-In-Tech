import os, requests
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from uuid import uuid4

# Create your models here.


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
    

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=150, null=True, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    age = models.IntegerField(null=True, unique=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    def email_user(self, subject: str, message: str, from_email: str = ..., **kwargs):
        zep2mail = os.getenv('ZEPTOMAIL_URL')
        zep2mail_auth = os.getenv('ZEPTOMAIL_AUTH_KEY')
        kwargs = {
            'url': zep2mail,
            'authorization': f'Zoho-enczapikey {zep2mail_auth}',
            'from_email': from_email,
            'to_emails_names': [(self.email, self.username or self.get_full_name())],
            'subject': subject,
            'htmlbody': message
        }
        return self._send_mail(**kwargs)
    
    # def email_user_otp(self, token):
    #     return self.email_user(
    #         subject='Sako Support',
    #         message=htmlbody_otp.format(token=token),
    #         from_email='noreply@xnexd.io'
    #     )

    def _send_mail(self, url:str, authorization:str, from_email:str, to_emails_names:list[tuple], subject:str, htmlbody:str):
        header = {
            'Authorization': authorization,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            }
        body = {
            'from': {'address': from_email},
            'to': [
                {'email_address': {'address': _email, 'name': _name}}
                for _email, _name in to_emails_names
            ],
            'subject': subject,
            'htmlbody': htmlbody
        }
        r = requests.post(url, headers=header, json=body).json()
        if 'error' in r:
            return (False, r)
        return (True, r)
    

class RegisteredCourse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Course(models.TextChoices):
        UIUX_DESIGN = 'ui/ux design',  'ui/ux design'
        DATA_ANALYSIS = 'data analysis', 'data analysis'

    course = models.CharField(
        max_length=30,
        unique=False,
        choices=Course.choices,
        # default=Course.UIUX_DESIGN
    )

    reason = models.TextField()

    def __str__(self) -> str:
        return f'{self.course}: {self.user.email}'