from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings


User=get_user_model()

@shared_task( bind=True,max_retries=3,default_retry_delay=10)


def send_welcome_email(self,user_pk):
    try:
        user = User.objects.get(pk=user_pk)

        send_mail(
            subject="Welcome to ArkaMarket",
            message=f"""
    Hello {user.username},

    Welcome to ArkaMarket.

    Thank you for creating an account.

    Enjoy shopping!
    """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        print(f"Welcome email sent to {user.email}")

    except Exception as exc:
        print(f"Failed to send email to {user.email}")
        raise self.retry(exc=exc)


