from apps.core.models import BaseModel
from django.db import models
from django.utils.text import slugify


class Category(BaseModel):
    """
    Категории книг
    """

    name = models.CharField(max_length=255, verbose_name="Название категории")
    slug = models.SlugField(
        max_length=255, unique=True, verbose_name="URL-идентификатор"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(BaseModel):
    """
    Книги/товары
    """

    title = models.CharField(max_length=255, verbose_name="Название книги")
    author = models.CharField(max_length=255, verbose_name="Автор")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name="Категория",
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name="Владелец (кто добавил)",
    )
    is_available = models.BooleanField(default=True, verbose_name="Доступен для заказа")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.author}"
