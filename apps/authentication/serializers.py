from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


# ─── JWT Personalizado ─────────────────────────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Claims personalizados dentro del JWT
        token["roles"]     = list(user.groups.values_list("name", flat=True))
        token["full_name"] = user.get_full_name()
        token["email"]     = user.email

        # Determinar tipo de usuario para que el frontend pueda redirigir
        if hasattr(user, "student"):
            token["user_type"] = "student"
        elif hasattr(user, "professor"):
            token["user_type"] = "professor"
        else:
            token["user_type"] = "staff"

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Añadir info útil en el body de la respuesta (además del token)
        data["user"] = {
            "id":        self.user.id,
            "username":  self.user.username,
            "full_name": self.user.get_full_name(),
            "email":     self.user.email,
            "roles":     list(self.user.groups.values_list("name", flat=True)),
        }
        return data


# ─── Cambio de Contraseña ──────────────────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True, required=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        write_only=True, required=True,
        style={"input_type": "password"},
    )
    confirm_new_password = serializers.CharField(
        write_only=True, required=True,
        style={"input_type": "password"},
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual no es correcta.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError(
                {"confirm_new_password": "Las contraseñas nuevas no coinciden."}
            )
        # Aplica los validadores de contraseña de Django (longitud, comunes, etc.)
        validate_password(attrs["new_password"], self.context["request"].user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


# ─── Usuario ───────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "is_active", "is_staff", "date_joined", "last_login",
            "roles", "user_type",
        ]
        read_only_fields = ["date_joined", "last_login"]

    def get_roles(self, obj) -> list:
        return list(obj.groups.values_list("name", flat=True))

    def get_user_type(self, obj) -> str:
        if hasattr(obj, "student"):
            return "student"
        if hasattr(obj, "professor"):
            return "professor"
        return "staff"


class UserCreateSerializer(serializers.ModelSerializer):
    """Crea un nuevo usuario con contraseña hasheada correctamente."""
    password = serializers.CharField(
        write_only=True, required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model  = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        # Usar create_user para hashear la contraseña correctamente
        return User.objects.create_user(**validated_data)


# ─── Roles ─────────────────────────────────────────────────────────────────────

class RoleSerializer(serializers.ModelSerializer):
    """Serializer para los Groups de Django ( roles del RBAC)."""
    user_count = serializers.SerializerMethodField()

    class Meta:
        model  = Group
        fields = ["id", "name", "user_count"]

    def get_user_count(self, obj) -> int:
        return obj.user_set.count()


class UserRoleAssignSerializer(serializers.Serializer):
    role_name = serializers.CharField(required=True)

    def validate_role_name(self, value):
        VALID_ROLES = [
            "estudiante", "instructor", "directivo", "subdirector",
            "comunicador", "decano", "ppa", "pg", "admin",
        ]
        if value not in VALID_ROLES:
            raise serializers.ValidationError(
                f"Rol inválido. Opciones válidas: {', '.join(VALID_ROLES)}"
            )
        if not Group.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                f"El rol '{value}' no existe en la BD. "
                f"Ejecuta: python manage.py create_roles"
            )
        return value


class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)


class UserPermissionsResponseSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)
    roles = serializers.ListField(child=serializers.CharField(), read_only=True)
    permissions = serializers.ListField(child=serializers.CharField(), read_only=True)
