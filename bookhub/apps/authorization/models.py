from django.db import models
from apps.core.models import BaseModel


class Role(BaseModel):
    """Роли пользователей в системе"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('customer', 'Покупатель'),
        ('guest', 'Гость'),
    ]

    name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        unique=True,
        verbose_name='Название роли'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание роли'
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.get_name_display()


class BusinessElement(BaseModel):
    """Бизнес-элементы системы (объекты для контроля доступа)"""
    ELEMENT_CHOICES = [
        ('user', 'Пользователь'),
        ('product', 'Товар'),
        ('category', 'Категория'),
        ('order', 'Заказ'),
        ('cart', 'Корзина'),
        ('review', 'Отзыв'),
        ('permission', 'Право доступа'),
    ]

    name = models.CharField(
        max_length=50,
        choices=ELEMENT_CHOICES,
        unique=True,
        verbose_name='Название элемента'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание элемента'
    )

    class Meta:
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'

    def __str__(self):
        return self.get_name_display()


class AccessRule(BaseModel):
    """
    Правила доступа ролей к бизнес-элементам.
    Соответствует таблице access_roles_rules из ТЗ.
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='access_rules',
        verbose_name='Роль'
    )
    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name='access_rules',
        verbose_name='Бизнес-элемент'
    )

    # Разрешения (как в ТЗ)
    read_permission = models.BooleanField(
        default=False,
        verbose_name='Чтение своих'
    )
    read_all_permission = models.BooleanField(
        default=False,
        verbose_name='Чтение всех'
    )
    create_permission = models.BooleanField(
        default=False,
        verbose_name='Создание'
    )
    update_permission = models.BooleanField(
        default=False,
        verbose_name='Редактирование своих'
    )
    update_all_permission = models.BooleanField(
        default=False,
        verbose_name='Редактирование всех'
    )
    delete_permission = models.BooleanField(
        default=False,
        verbose_name='Удаление своих'
    )
    delete_all_permission = models.BooleanField(
        default=False,
        verbose_name='Удаление всех'
    )

    class Meta:
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'
        unique_together = ['role', 'element']

    def __str__(self):
        return f'{self.role} -> {self.element}'


class UserRole(BaseModel):
    """Связь пользователей с ролями (многие-ко-многим)"""
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='Пользователь'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = ['user', 'role']

    def __str__(self):
        return f'{self.user} - {self.role}'