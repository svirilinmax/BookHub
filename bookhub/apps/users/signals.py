from apps.authorization.models import Role, UserRole
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def assign_customer_role(sender, instance, created, **kwargs):
    """
    Автоматически назначаем роль 'customer' новым пользователям
    """

    if created and not instance.is_staff:
        try:
            customer_role = Role.objects.get(name="customer")
            UserRole.objects.get_or_create(user=instance, role=customer_role)
            print(f"Автоматически назначена роль 'customer' для {instance.email}")
        except Role.DoesNotExist:
            print("Роль 'customer' не найдена в базе данных")
