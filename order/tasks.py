from celery import shared_task
from .models import Order, OrderStatus
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db import transaction


@shared_task(bind=True,max_retries=3,default_retry_delay=10)
def send_order_email(self,order_id):
    try:
        order=Order.objects.get(id=order_id)
        products = "\n".join(
            f"- {item.product.name} × {item.quantity} = ${item.total_price}"
            for item in order.items.all()
        )
        total_price = sum(item.total_price for item in order.items.all())

        send_mail(
            subject="Order Confirmation",
            message=f"""
        Hello {order.user.username}
        Thank you for your purchase.
        Order Number:#{order.id}
        Products:
        {products}
        Total Price:${total_price}
        Status :{order.get_status_display()}
        We will notify you when your order is shipped.
        """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )
        print(f"Order confirmation email sent to {order.user.email}")

    except Exception as exc:

        print(f"Failed to send order confirmation for order {order_id}")

        raise self.retry(exc=exc)



@shared_task
def cancel_expired_orders():
    with transaction.atomic():
        limit_time=timezone.now()-timedelta(hours=24)
        orders=(
            Order.objects.filter(
            status=OrderStatus.PENDING,
            created_at__lt=limit_time
        )
            .prefetch_related("items__product")
    )
        canceled_count = orders.count()

        for order in orders:
            for item in order.items.all():
                item.product.stock_quantity+=item.quantity
                item.product.save(update_fields=["stock_quantity"])
            order.status = OrderStatus.CANCELED
            order.save(update_fields=["status"])
        return f"{canceled_count} orders canceled"