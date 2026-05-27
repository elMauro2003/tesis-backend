from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modelo de Usuario personalizado extendiendo AbstractUser.
    El campo email es nullable para permitir creación de usuarios sin email.
    """
    # Sobrescribir el campo email para hacerlo opcional (blank=True, null=True)
    email = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="dirección de correo electrónico",
    )

    class Meta:
        db_table = "users"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.get_full_name()} (@{self.username})"
