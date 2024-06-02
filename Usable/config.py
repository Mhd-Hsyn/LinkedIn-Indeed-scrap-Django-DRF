from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from decouple import config


connection = get_connection(
    host=config("EMAIL_HOST"),
    port=config("EMAIL_PORT"),
    username=config("EMAIL_HOST_USER"),
    password=config("EMAIL_HOST_PASSWORD"),
    use_tls=True,
)
