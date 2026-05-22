import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_tokens_for_user(user):
    """Genera par de tokens JWT para un usuario (sin llamar al endpoint)."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }


def authenticated_client(user) -> APIClient:
    """Devuelve un APIClient con el header Authorization ya configurado."""
    client = APIClient()
    tokens = get_tokens_for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return client


# ─── Roles (se crean una sola vez por sesión de tests) ────────────────────────

@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Crea los 9 roles del sistema al inicio de la sesión de tests.
    scope="session" → solo se ejecuta una vez para todos los tests.
    """
    with django_db_blocker.unblock():
        ROLES = [
            "estudiante", "instructor", "directivo", "subdirector",
            "comunicador", "decano", "ppa", "pg", "admin",
        ]
        for role in ROLES:
            Group.objects.get_or_create(name=role)


# ─── Usuarios base ────────────────────────────────────────────────────────────

@pytest.fixture
def user_admin(db):
    user = User.objects.create_user(
        username="admin_test", password="AdminPass123!",
        first_name="Admin", last_name="Test",
        email="admin@test.cu", is_staff=True,
    )
    group, _ = Group.objects.get_or_create(name="admin")
    user.groups.add(group)
    return user


@pytest.fixture
def user_instructor(db):
    user = User.objects.create_user(
        username="instructor_test", password="InstrPass123!",
        first_name="Carlos", last_name="Instructor",
        email="instructor@test.cu",
    )
    group, _ = Group.objects.get_or_create(name="instructor")
    user.groups.add(group)
    return user


@pytest.fixture
def user_directivo(db):
    user = User.objects.create_user(
        username="directivo_test", password="DirPass123!",
        first_name="María", last_name="Directiva",
        email="directivo@test.cu",
    )
    group, _ = Group.objects.get_or_create(name="directivo")
    user.groups.add(group)
    return user


@pytest.fixture
def user_subdirector(db):
    user = User.objects.create_user(
        username="subdirector_test", password="SubPass123!",
        first_name="Pedro", last_name="Subdirector",
        email="subdirector@test.cu",
    )
    group, _ = Group.objects.get_or_create(name="subdirector")
    user.groups.add(group)
    return user


@pytest.fixture
def user_comunicador(db):
    user = User.objects.create_user(
        username="comunicador_test", password="ComPass123!",
        first_name="Ana", last_name="Comunicadora",
        email="comunicador@test.cu",
    )
    group, _ = Group.objects.get_or_create(name="comunicador")
    user.groups.add(group)
    return user


@pytest.fixture
def user_estudiante(db):
    """Usuario base con rol estudiante (sin Student asociado aún)."""
    user = User.objects.create_user(
        username="estudiante_test", password="EstPass123!",
        first_name="Luis", last_name="Estudiante",
        email="estudiante@test.cu",
    )
    group, _ = Group.objects.get_or_create(name="estudiante")
    user.groups.add(group)
    return user


@pytest.fixture
def user_no_role(db):
    """Usuario autenticado sin ningún rol — para probar denegaciones."""
    return User.objects.create_user(
        username="norole_test", password="NoRole123!",
        email="norole@test.cu",
    )


# ─── API Clients autenticados ─────────────────────────────────────────────────

@pytest.fixture
def client_admin(user_admin):
    return authenticated_client(user_admin)

@pytest.fixture
def client_instructor(user_instructor):
    return authenticated_client(user_instructor)

@pytest.fixture
def client_directivo(user_directivo):
    return authenticated_client(user_directivo)

@pytest.fixture
def client_subdirector(user_subdirector):
    return authenticated_client(user_subdirector)

@pytest.fixture
def client_comunicador(user_comunicador):
    return authenticated_client(user_comunicador)

@pytest.fixture
def client_no_auth():
    """Cliente sin autenticación."""
    return APIClient()


# ─── Infraestructura base ─────────────────────────────────────────────────────

@pytest.fixture
def site(db):
    from apps.infrastructure.models import Site
    return Site.objects.create(name="Sede Central", address="UCLV Campus")


@pytest.fixture
def building(site):
    from apps.infrastructure.models import Building
    return Building.objects.create(site=site, name="Edificio 1")


@pytest.fixture
def wing(building):
    from apps.infrastructure.models import Wing
    return Wing.objects.create(building=building, name="A")


@pytest.fixture
def room(wing):
    from apps.infrastructure.models import Room
    return Room.objects.create(wing=wing, number="101", capacity=4)


@pytest.fixture
def room_full(wing):
    """Cuarto con ocupación al máximo para tests de validación."""
    from apps.infrastructure.models import Room
    r = Room.objects.create(wing=wing, number="199", capacity=2)
    # Simular ocupación directa (bypass de señales para el fixture)
    Room.objects.filter(pk=r.pk).update(current_occupancy=2)
    r.refresh_from_db()
    return r


# ─── Estructura académica ─────────────────────────────────────────────────────

@pytest.fixture
def faculty(db):
    from apps.academic.models import Faculty
    return Faculty.objects.create(name="Facultad de Matemática, Física y Computación", code="MATFISCOM")


@pytest.fixture
def career(faculty):
    from apps.academic.models import Career
    return Career.objects.create(name="Ingeniería en Ciencias Informáticas", code="ICI", faculty=faculty)


@pytest.fixture
def career_year(career):
    from apps.academic.models import CareerYear
    return CareerYear.objects.create(career=career, year=3)


@pytest.fixture
def group(career_year):
    from apps.academic.models import Group
    return Group.objects.create(name="C-311", career_year=career_year)


# ─── Student completo ─────────────────────────────────────────────────────────

@pytest.fixture
def student(user_estudiante, group):
    """Student con User asociado y grupo académico."""
    from apps.actors.models import Student
    return Student.objects.create(
        user=user_estudiante,
        ci="90010112345",
        student_id="ICI-2020-001",
        birth_date="2001-01-01",
        gender="M",
        group=group,
    )


@pytest.fixture
def client_estudiante(student):
    """APIClient autenticado como el estudiante del fixture student."""
    return authenticated_client(student.user)


# ─── Professor + sub-rol WingSupervisor ───────────────────────────────────────

@pytest.fixture
def professor(user_instructor):
    from apps.actors.models import Professor
    return Professor.objects.create(
        user=user_instructor,
        employee_id="EMP-001",
        department="Dirección de Becas",
    )


@pytest.fixture
def wing_supervisor(professor, wing):
    from apps.actors.models import WingSupervisor
    return WingSupervisor.objects.create(professor=professor, wing=wing)
