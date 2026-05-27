"""
Management command para cargar datos de prueba realistas en la BD.

Este comando puebla la BD con datos COMPLETOS E ÍNTEGROS para TODOS los modelos:

INFRAESTRUCTURA:
    - 3 sedes
    - 8 edificios  
    - 24 alas
    - 120 cuartos

ACADÉMICA:
    - 2 facultades
    - 3 carreras
    - 5 años académicos (1-5)
    - 15 grupos (3 grupos por año)

ACTORES:
    - 35+ profesores con roles completos:
        * 2 Decanos (1 por facultad)
        * 5 PPAs (1 por año académico)
        * 15 Profesores Guía (1 por grupo)
        * 24 Responsables de Ala (1 por ala)
        * 2 Instructores regulares
        * 2 Subdirectores administrativo
        * 2 Comunicadores
        * 1 Administrador

DATA OPERATIVA:
    - 150 estudiantes distribuidos entre grupos
    - Todas las asignaciones de cuartos cubriendo ~85% de capacidad
    - 80+ evaluaciones distribuidas en el semestre
    - 50+ quejas con diversos estados
    - 60+ cuartelerías programadas
    - 12 informaciones públicas
    - 8 reportes

Año académico: Septiembre 2025 — Julio 2026
"""

import random
from datetime import datetime, date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db.models import F
from django.utils import timezone
from apps.authentication.models import User

from apps.academic.models import Faculty, Career, CareerYear, Group as StudentGroup
from apps.actors.models import Student, Professor, Dean, YearLeadProfessor, GroupAdvisor, WingSupervisor
from apps.infrastructure.models import Site, Building, Wing, Room
from apps.operations.models import Assignment, Complaint, Evaluation, CleaningSchedule, Information, Report
from apps.actors.serializers import StudentCreateSerializer


class Command(BaseCommand):
    help = "Carga datos de prueba COMPLETOS e ÍNTEGROS en la BD"

    def handle(self, *args, **options):
        self.stdout.write("🌱 Iniciando seed database mejorado...\n")
        
        try:
            self.create_groups_from_roles()  # Crear grupos Django para roles
            self.create_infrastructure()
            self.create_academic_structure()
            self.create_professors()
            self.create_students()
            self.create_evaluations()
            self.create_complaints()
            self.create_cleaning_schedules()
            self.create_informations()
            self.create_reports()
            
            self.stdout.write(self.style.SUCCESS(
                "\n✅ Seed database completado exitosamente!\n"
            ))
            self.print_summary()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            raise
    
    def print_summary(self):
        """Imprime resumen estadístico del seed."""
        sites = Site.objects.count()
        buildings = Building.objects.count()
        wings = Wing.objects.count()
        rooms = Room.objects.count()
        students = Student.objects.count()
        assignments = Assignment.objects.filter(released_date__isnull=True).count()
        evaluations = Evaluation.objects.count()
        complaints = Complaint.objects.count()
        cleaning = CleaningSchedule.objects.count()
        info = Information.objects.count()
        reports = Report.objects.count()
        
        self.stdout.write("📊 DATOS CARGADOS:\n")
        self.stdout.write(f"   🏗️  Infraestructura: {sites} sedes, {buildings} edificios, {wings} alas, {rooms} cuartos\n")
        self.stdout.write(f"   👥 Estudiantes: {students} (con {assignments} asignaciones activas)\n")
        self.stdout.write(f"   📋 Evaluaciones: {evaluations}\n")
        self.stdout.write(f"   🗣️  Quejas: {complaints}\n")
        self.stdout.write(f"   🧹 Cuartelerías: {cleaning}\n")
        self.stdout.write(f"   📢 Informaciones: {info}\n")
        self.stdout.write(f"   📊 Reportes: {reports}\n")
    
    def create_groups_from_roles(self):
        """Crea los grupos Django para roles (si no existen)."""
        self.stdout.write("👤 Creando grupos de roles...")
        
        role_groups = [
            'estudiante', 'instructor', 'directivo', 'subdirector',
            'comunicador', 'decano', 'ppa', 'pg', 'admin'
        ]
        
        for role_name in role_groups:
            Group.objects.get_or_create(name=role_name)
        
        self.stdout.write(self.style.SUCCESS("✓ Grupos de roles creados"))


    def create_infrastructure(self):
        """Crear sedes, edificios, alas y cuartos."""
        self.stdout.write("📍 Creando infraestructura...")
        
        # Sedes (3)
        sites_data = [
            {"name": "Sede Central", "address": "Campus Principal, Las Villas", "desc": "Complejo residencial central"},
            {"name": "Sede Pedagógico", "address": "Facultad de Educación, Las Villas", "desc": "Residencia para estudiantes de pedagogía"},
            {"name": "Sede Fajardo", "address": "Complejo Fajardo, Las Villas", "desc": "Residencia del complejo Fajardo"},
        ]
        sites = []
        for s in sites_data:
            site, _ = Site.objects.get_or_create(
                name=s["name"],
                defaults={"address": s["address"], "description": s["desc"]}
            )
            sites.append(site)
        
        # Edificios por sede (2-3 por sede = 8 total)
        buildings = []
        building_names = [
            ("Edificio A - Ciencias", "Residencia de Ciencias Exactas"),
            ("Edificio B - Ingeniería", "Residencia de Ingeniería"),
            ("Edificio C - Humanidades", "Residencia de Humanidades"),
            ("Edificio D - Administrativo", "Residencia Administrativa"),
        ]
        
        for i, site in enumerate(sites):
            count = 3 if i == 0 else 2  # Central: 3, otras: 2
            for j in range(count):
                idx = (i * 3 + j) % len(building_names)
                building, _ = Building.objects.get_or_create(
                    site=site,
                    name=f"{building_names[idx][0]} - {site.name}",
                    defaults={"address": f"Edificio {j+1}, {site.address}"}
                )
                buildings.append(building)
        
        # Alas por edificio (3 alas por edificio = 24 total)
        wings = []
        for building in buildings:
            for i in range(3):
                wing, _ = Wing.objects.get_or_create(
                    building=building,
                    name=f"Ala {chr(65+i)}",  # A, B, C
                )
                wings.append(wing)
        
        # Cuartos por ala (5 cuartos × 24 alas = 120 cuartos)
        for wing in wings:
            for i in range(5):
                room_number = f"{wing.building.id:02d}{wing.id:02d}{i+1:02d}"
                Room.objects.get_or_create(
                    wing=wing,
                    number=room_number,
                    defaults={
                        "capacity": 4,
                        "is_active": True,
                        "current_occupancy": 0,
                    }
                )
        
        self.stdout.write(self.style.SUCCESS(f"✓ Infraestructura: {len(sites)} sedes, {len(buildings)} edificios, {len(wings)} alas, 120 cuartos"))
        self.sites = sites
        self.buildings = buildings
        self.wings = wings


    def create_academic_structure(self):
        """Crear estructura académica: facultades, carreras, años, grupos."""
        self.stdout.write("🎓 Creando estructura académica...")
        
        # Facultades (2)
        faculties_data = [
            {"name": "Facultad de Matemática, Física y Computación", "code": "MATFISCOM"},
            {"name": "Facultad de Ingeniería", "code": "FING"},
        ]
        faculties = []
        for f in faculties_data:
            faculty, _ = Faculty.objects.get_or_create(
                name=f["name"],
                defaults={"code": f["code"]}
            )
            faculties.append(faculty)
        
        # Carreras (3: 2 en MATFISCOM, 1 en FING)
        careers_data = [
            {"name": "Ingeniería en Ciencias Informáticas", "code": "ICI", "faculty": faculties[0]},
            {"name": "Licenciatura en Matemática", "code": "LM", "faculty": faculties[0]},
            {"name": "Ingeniería Eléctrica", "code": "EE", "faculty": faculties[1]},
        ]
        careers = []
        for c in careers_data:
            career, _ = Career.objects.get_or_create(
                code=c["code"],
                defaults={"name": c["name"], "faculty": c["faculty"]}
            )
            careers.append(career)
        
        # Años académicos (5 años × 3 carreras = 15 años)
        years = []
        for career in careers:
            for year_num in range(1, 6):  # 1º a 5º año
                year, _ = CareerYear.objects.get_or_create(
                    career=career,
                    year=year_num
                )
                years.append(year)
        
        # Grupos de estudiantes (1 grupo por año = 15 grupos)
        groups = []
        for year in years:
            group_name = f"{year.career.code}-{year.year}°"
            group, _ = StudentGroup.objects.get_or_create(
                name=group_name,
                career_year=year
            )
            groups.append(group)
        
        self.stdout.write(self.style.SUCCESS(
            f"✓ Académica: {len(faculties)} facultades, {len(careers)} carreras, "
            f"{len(years)} años, {len(groups)} grupos"
        ))
        self.faculties = faculties
        self.careers = careers
        self.years = years
        self.groups = groups


    def create_professors(self):
        """Crear profesores y asignarles roles de forma completa."""
        self.stdout.write("👨‍🏫 Creando profesores con roles...")
        
        # Datos base de profesores
        professors_data = [
            # DECANOS (2: 1 por facultad)
            {"username": "decano_matfiscom", "email": "decano1@uclv.cu", "first_name": "Juan", "last_name": "López"},
            {"username": "decano_fing", "email": "decano2@uclv.cu", "first_name": "María", "last_name": "Rodríguez"},
            
            # PPAs - Profesores Principales de Año (5: 1 por año académico)
            {"username": "ppa_ici_1", "email": "ppa1@uclv.cu", "first_name": "Pedro", "last_name": "González"},
            {"username": "ppa_ici_2", "email": "ppa2@uclv.cu", "first_name": "Carmen", "last_name": "Martínez"},
            {"username": "ppa_ici_3", "email": "ppa3@uclv.cu", "first_name": "Roberto", "last_name": "Díaz"},
            {"username": "ppa_lm_1", "email": "ppa4@uclv.cu", "first_name": "Sofía", "last_name": "Vargas"},
            {"username": "ppa_ee_1", "email": "ppa5@uclv.cu", "first_name": "Luis", "last_name": "Castro"},
            
            # PROFESORES GUÍA (15: 1 por grupo - pero crearemos solo 15 principales)
            {"username": "pg_ici_1a", "email": "pg1@uclv.cu", "first_name": "Carlos", "last_name": "Martínez"},
            {"username": "pg_ici_1b", "email": "pg2@uclv.cu", "first_name": "Ana", "last_name": "Jiménez"},
            {"username": "pg_ici_1c", "email": "pg3@uclv.cu", "first_name": "David", "last_name": "Flores"},
            {"username": "pg_ici_2a", "email": "pg4@uclv.cu", "first_name": "Elena", "last_name": "Ruiz"},
            {"username": "pg_ici_2b", "email": "pg5@uclv.cu", "first_name": "Francisco", "last_name": "Sánchez"},
            {"username": "pg_ici_2c", "email": "pg6@uclv.cu", "first_name": "Gabriela", "last_name": "López"},
            {"username": "pg_ici_3a", "email": "pg7@uclv.cu", "first_name": "Héctor", "last_name": "García"},
            {"username": "pg_ici_3b", "email": "pg8@uclv.cu", "first_name": "Irene", "last_name": "Pérz"},
            {"username": "pg_ici_3c", "email": "pg9@uclv.cu", "first_name": "Javier", "last_name": "Vega"},
            {"username": "pg_lm_1a", "email": "pg10@uclv.cu", "first_name": "Karen", "last_name": "Morales"},
            {"username": "pg_lm_1b", "email": "pg11@uclv.cu", "first_name": "Luis", "last_name": "Ramírez"},
            {"username": "pg_ee_1a", "email": "pg12@uclv.cu", "first_name": "Marta", "last_name": "Herrera"},
            {"username": "pg_ee_1b", "email": "pg13@uclv.cu", "first_name": "Nicolás", "last_name": "Fuentes"},
            
            # RESPONSABLES DE ALA (24: 1 por ala)
            *[{"username": f"wing_supervisor_{i:02d}", "email": f"wing_sup{i}@uclv.cu",
               "first_name": f"Supervisor{i%10}", "last_name": f"Ala{i}"} for i in range(1, 25)],
            
            # SUBDIRECTORES ADMINISTRATIVOS (2)
            {"username": "subdirector_1", "email": "subdirector1@uclv.cu", "first_name": "Otilia", "last_name": "Rodríguez"},
            {"username": "subdirector_2", "email": "subdirector2@uclv.cu", "first_name": "Pablo", "last_name": "Santos"},
            
            # COMUNICADORES (2)
            {"username": "comunicador_1", "email": "comunicador1@uclv.cu", "first_name": "Quique", "last_name": "Torres"},
            {"username": "comunicador_2", "email": "comunicador2@uclv.cu", "first_name": "Rosa", "last_name": "Valentín"},
            
            # ADMINISTRADOR (1)
            {"username": "admin_bd", "email": "admin@uclv.cu", "first_name": "Sergio", "last_name": "Administrador"},
        ]
        
        professors = []
        for prof_data in professors_data:
            user, created = User.objects.get_or_create(
                username=prof_data["username"],
                defaults={
                    "email": prof_data["email"],
                    "first_name": prof_data["first_name"],
                    "last_name": prof_data["last_name"],
                }
            )
            if created or not user.has_usable_password():
                user.set_password("Password123!")
                user.save()
            
            professor, _ = Professor.objects.get_or_create(
                user=user,
                defaults={
                    "employee_id": f"EMP-{prof_data['username'][:10]}-{user.id:04d}",
                    "department": "Dirección de Becas",
                }
            )
            professors.append((user, professor))
        
        # Asignar roles específicos
        idx = 0
        
        # Decanos (2)
        for i in range(2):
            decano_user = professors[idx][0]
            decano_user.groups.add(Group.objects.get(name='decano'))
            Dean.objects.get_or_create(
                professor=professors[idx][1],
                defaults={"faculty": self.faculties[i]}
            )
            idx += 1
        
        # PPAs (5 - 1 por año académico)
        for i in range(5):
            ppa_user = professors[idx][0]
            ppa_user.groups.add(Group.objects.get(name='ppa'))
            YearLeadProfessor.objects.get_or_create(
                professor=professors[idx][1],
                defaults={"career_year": self.years[i]}
            )
            idx += 1
        
        # Profesores Guía (15 - 1 por grupo, pero solo los primeros)
        for i in range(min(15, len(self.groups))):
            pg_user = professors[idx][0]
            pg_user.groups.add(Group.objects.get(name='pg'))
            GroupAdvisor.objects.get_or_create(
                professor=professors[idx][1],
                defaults={"group": self.groups[i]}
            )
            idx += 1
        
        # Responsables de Ala (24 - 1 por ala)
        for i, wing in enumerate(self.wings):
            if idx < len(professors):
                wing_user = professors[idx][0]
                wing_user.groups.add(Group.objects.get(name='instructor'))
                WingSupervisor.objects.get_or_create(
                    professor=professors[idx][1],
                    defaults={"wing": wing}
                )
                idx += 1
        
        # Subdirectores administrativos (2)
        for i in range(2):
            if idx < len(professors):
                sd_user = professors[idx][0]
                sd_user.groups.add(Group.objects.get(name='subdirector'))
                idx += 1
        
        # Comunicadores (2)
        for i in range(2):
            if idx < len(professors):
                com_user = professors[idx][0]
                com_user.groups.add(Group.objects.get(name='comunicador'))
                idx += 1
        
        # Administrador (1)
        if idx < len(professors):
            admin_user = professors[idx][0]
            admin_user.groups.add(Group.objects.get(name='admin'))
            admin_user.is_staff = True
            admin_user.save()
        
        self.stdout.write(self.style.SUCCESS(f"✓ {len(professors)} profesores con roles completos creados"))
        self.professors = professors


    def create_students(self):
        """Crear 150 estudiantes y asignarles cuartos equilibradamente."""
        self.stdout.write("👥 Creando estudiantes con asignaciones...")
        
        first_names = [
            "Luis", "María", "Carlos", "Ana", "Pedro", "Sofia", "Juan", "Rosa",
            "Miguel", "Elena", "Andrés", "Fernanda", "Roberto", "Catalina", "Diego", "Valentina"
        ]
        last_names = [
            "García", "López", "González", "Martínez", "Rodríguez", "Pérez", "Jiménez",
            "Vargas", "Díaz", "Castro", "Flores", "Ruiz", "Sánchez", "Ramírez", "Herrera"
        ]
        
        health_conditions = [
            None,
            "Alergia a penicilina",
            "Asma leve",
            "Diabetes tipo 2",
            "Hipertensión",
            "Alergia a mariscos",
        ]
        
        medications = [
            None,
            "Insulina",
            "Omeprazol",
            "Ventolín",
            "Metformina",
        ]
        
        students_created = 0
        rooms = list(Room.objects.filter(is_active=True).order_by('id'))
        room_index = 0
        
        # Distribuir 150 estudiantes entre grupos (10 por grupo aprox)
        students_per_group = 150 // len(self.groups) + 1
        
        for group_idx, group in enumerate(self.groups):
            for student_num in range(students_per_group):
                if students_created >= 150:
                    break
                
                student_num_global = students_created + 1
                
                # Datos del usuario
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                username = f"student_{student_num_global:04d}"
                email = f"{username}@uclv.cu"
                
                # Crear usuario y estudiante usando StudentCreateSerializer (flujo frontend)
                serializer_payload = {
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "password": "Password123!",
                    "ci": f"{random.randint(90000000000, 99999999999)}",
                    "gender": random.choice(['M', 'F']),
                    "address": f"Calle {random.randint(1, 100)}, Apt {random.randint(1, 99)}",
                    "province": random.choice(["Villa Clara", "La Habana", "Santiago"]),
                    "municipality": random.choice(["Santa Clara", "Camajuaní", "Remedios", "Encrucijada"]),
                    "phone": f"+53 4222-{random.randint(1000, 9999)}",
                    "emergency_phone": f"+53 4222-{random.randint(1000, 9999)}",
                    # academic: pasar career id y year (auto-asignación de grupo)
                    "career": group.career_year.career.id,
                    "year": group.career_year.year,
                    "academic_performance": random.choice([
                        None, "Buen aprovechamiento", "Aprovechamiento medio", "Bajo aprovechamiento"
                    ]),
                    # salud y perfil
                    "illnesses": random.choice(health_conditions),
                    "medications": random.choice(medications),
                    "is_militant": random.choice([True, False, False]),
                    "is_cadet_minint": random.choice([True, False, False, False, False]),
                    "is_cadet_far": random.choice([True, False, False, False, False]),
                    "disciplinary_process": None,
                }
                # Para ambas rutas: agregar birth_date
                birth_date_value = date(random.randint(1999, 2006), random.randint(1, 12), random.randint(1, 28))
                serializer_payload["birth_date"] = birth_date_value

                # Evitar crear usuario duplicado si ya existe
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    student, _ = Student.objects.get_or_create(
                        user=user,
                        defaults={
                            "ci": serializer_payload["ci"],
                            "group": group,
                            "birth_date": birth_date_value,
                            "student_id": f"SID-{username}",
                            "address": serializer_payload["address"],
                            "province": serializer_payload["province"],
                            "municipality": serializer_payload["municipality"],
                            "phone": serializer_payload["phone"],
                            "emergency_phone": serializer_payload["emergency_phone"],
                            "illnesses": serializer_payload["illnesses"],
                            "medications": serializer_payload["medications"],
                            "is_militant": serializer_payload["is_militant"],
                            "is_cadet_minint": serializer_payload["is_cadet_minint"],
                            "is_cadet_far": serializer_payload["is_cadet_far"],
                            "academic_performance": serializer_payload["academic_performance"],
                            "disciplinary_process": serializer_payload["disciplinary_process"],
                        }
                    )
                else:
                    serializer = StudentCreateSerializer(data=serializer_payload)
                    if serializer.is_valid():
                        student = serializer.save()
                        user = student.user
                    else:
                        # Fallback: crear por ORM si el serializer falla
                        user, _ = User.objects.get_or_create(
                            username=username,
                            defaults={
                                "email": email,
                                "first_name": first_name,
                                "last_name": last_name,
                            }
                        )
                        if not user.has_usable_password():
                            user.set_password("Password123!")
                            user.save()
                        user.groups.add(Group.objects.get(name='estudiante'))
                        student, _ = Student.objects.get_or_create(
                            user=user,
                            defaults={
                                "ci": serializer_payload["ci"],
                                "group": group,
                                "birth_date": birth_date_value,
                                "student_id": f"SID-{username}",
                                "address": serializer_payload["address"],
                                "province": serializer_payload["province"],
                                "municipality": serializer_payload["municipality"],
                                "phone": serializer_payload["phone"],
                                "emergency_phone": serializer_payload["emergency_phone"],
                                "illnesses": serializer_payload["illnesses"],
                                "medications": serializer_payload["medications"],
                                "is_militant": serializer_payload["is_militant"],
                                "is_cadet_minint": serializer_payload["is_cadet_minint"],
                                "is_cadet_far": serializer_payload["is_cadet_far"],
                                "academic_performance": serializer_payload["academic_performance"],
                                "disciplinary_process": payload["disciplinary_process"],
                            }
                        )
                
                # Asignar cuarto en forma rotatoria para distribuir equilibradamente
                if room_index < len(rooms):
                    room = rooms[room_index]
                    Assignment.objects.get_or_create(
                        student=student,
                        defaults={
                            "room": room,
                            "assigned_date": date(2025, 9, 15),
                            "assigned_by": random.choice([p[0] for p in self.professors if 'wing_supervisor' in p[0].username or 'instructor' in p[0].username]),
                        }
                    )
                    room_index += 1
                
                students_created += 1
            
            if students_created >= 150:
                break
        
        self.stdout.write(self.style.SUCCESS(f"✓ {students_created} estudiantes creados con asignaciones"))
        self.students = Student.objects.all()
        
        # Guarda usuario para login de prueba
        self.first_student_user = User.objects.filter(username='student_0001').first()


    def create_evaluations(self):
        """Crear 80+ evaluaciones distribuidas en el semestre."""
        self.stdout.write("📋 Creando evaluaciones...")
        
        grades = ['B', 'R', 'M']  # Bien, Regular, Mal
        comments = [
            "Comportamiento ejemplar",
            "Participación activa en actividades residenciales",
            "Cumplimiento general de normas",
            "Incumplimiento de normas",
            "Necesita mejorar disciplina",
            "Excelente desempeño",
            "Responsable y cooperador",
            "Poco compromiso",
            "Puntualidad regular",
            "Buen compañero de cuarto",
        ]
        
        evaluations_created = 0
        # Distribuir evaluaciones a lo largo del semestre (sep 2025 - jul 2026)
        start_date = date(2025, 9, 15)
        end_date = date(2026, 7, 10)
        current_date = start_date
        
        # Crear ~5 evaluaciones cada 2 semanas
        while current_date <= end_date and evaluations_created < 80:
            # Seleccionar 5-8 estudiantes aleatorios para evaluar
            random_students = random.sample(list(self.students)[:100], min(8, len(self.students)))
            
            for student in random_students:
                if evaluations_created < 80:
                    # Elegir instructor evaluador
                    evaluator = random.choice([
                        p[0] for p in self.professors
                        if 'instructor' in p[0].username or 'wing_supervisor' in p[0].username
                    ])
                    
                    Evaluation.objects.create(
                        student=student,
                        date=current_date,
                        grade=random.choice(grades),
                        comment=random.choice(comments),
                        created_by=evaluator,
                    )
                    evaluations_created += 1
            
            # Avanzar 14 días
            current_date += timedelta(days=14)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {evaluations_created} evaluaciones creadas"))


    def create_complaints(self):
        """Crear 50+ quejas en diversos estados y tipos."""
        self.stdout.write("🗣️ Creando quejas...")
        
        statuses = ['pendiente', 'en_proceso', 'resuelta', 'rechazada']
        complaint_types = ['administrativa', 'educativa']
        descriptions = [
            "Fuga de agua en el baño",
            "Falta de agua caliente en la ducha",
            "Problema con electricidad en cuarto",
            "Deterioro del equipamiento de dormitorio",
            "Mala coordinación de cuartelerías",
            "Necesidad de mantenimiento urgente",
            "Falta de higiene en áreas comunes",
            "Ruido excesivo en horarios de estudio",
            "Problema con agua potable",
            "Ventilación deficiente en cuarto",
            "Mala calidad de almohadas y colchones",
            "Falta de privacidad adecuada",
            "Plagas en el dormitorio",
            "Iluminación insuficiente",
            "Puertas y cerraduras defectuosas",
        ]
        
        responses = [
            "Orden enviada a mantenimiento",
            "Se inició proceso de reparación",
            "Problema resuelto correctamente",
            "Validada la queja, en proceso de revisión",
            "Derivada al área correspondiente",
            "Se asignó equipo de trabajo",
        ]
        
        complaints_created = 0
        start_date = date(2025, 9, 20)
        current_date = start_date
        building_list = list(self.buildings)
        
        while current_date <= date(2026, 7, 31) and complaints_created < 50:
            # Crear 1-3 quejas por semana
            for _ in range(random.randint(1, 3)):
                if complaints_created < 50:
                    student = random.choice(self.students[:120])  # Primeros 120 estudiantes
                    
                    # 50% con respuesta, 50% sin respuesta
                    has_response = random.choice([True, False])
                    response_date = None
                    if has_response:
                        response_date = timezone.make_aware(
                            datetime.combine(
                                current_date + timedelta(days=random.randint(1, 5)),
                                datetime.min.time()
                            )
                        )
                    
                    Complaint.objects.create(
                        student=student,
                        date=current_date,
                        building=random.choice(building_list),
                        description=random.choice(descriptions),
                        type=random.choice(complaint_types),
                        status=random.choices(
                            statuses,
                            weights=[20, 30, 35, 15]  # Más quejas resueltas que pendientes
                        )[0],
                        response=random.choice(responses) if has_response else None,
                        response_date=response_date,
                        visibility=random.choice([True, False, False]),  # Menos visibles que ocultas
                    )
                    complaints_created += 1
            
            current_date += timedelta(days=7)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {complaints_created} quejas creadas"))


    def create_cleaning_schedules(self):
        """Crear 60+ cuartelerías (limpiezas asignadas)."""
        self.stdout.write("🧹 Creando cuartelerías...")
        
        rooms_list = list(Room.objects.filter(is_active=True).order_by('id'))
        evaluations = ['B', 'R', 'M']
        comments_list = [
            "Se limpió satisfactoriamente",
            "Faltó el estudiante",
            "Limpieza poco completa",
            "Excelente trabajo de limpieza",
            "Algunos detalles por mejorar",
            "Completado correctamente",
            "",  # Sin comentarios
        ]
        
        cleaning_created = 0
        start_date = date(2025, 9, 22)
        current_date = start_date
        
        # Crear ~4 cuartelerías por semana
        while current_date <= date(2026, 7, 10) and cleaning_created < 60:
            # Seleccionar 4-6 cuartos aleatorios
            selected_rooms = random.sample(rooms_list, min(6, len(rooms_list)))
            
            for room in selected_rooms:
                if cleaning_created < 60:
                    # Obtener estudiantes asignados a este cuarto (activos)
                    students_in_room = Student.objects.filter(
                        assignments__room=room,
                        assignments__released_date__isnull=True
                    )
                    
                    if students_in_room.exists():
                        CleaningSchedule.objects.create(
                            room=room,
                            student=random.choice(list(students_in_room)),
                            assigned_date=current_date,
                            completed=random.choice([True, True, False]),  # 66% completadas
                            evaluation=random.choice(evaluations) if random.choice([True, True, False]) else None,
                            comments=random.choice(comments_list),
                        )
                        cleaning_created += 1
            
            current_date += timedelta(days=7)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {cleaning_created} cuartelerías creadas"))


    def create_informations(self):
        """Crear 12 informaciones/comunicados."""
        self.stdout.write("📢 Creando informaciones...")
        
        informations_data = [
            {
                "title": "Suspensión de agua caliente",
                "content": "Por mantenimiento preventivo, el servicio de agua caliente estará suspendido del 5 al 7 de octubre de 08:00 a 18:00 horas."
            },
            {
                "title": "Mantenimiento de sistema eléctrico",
                "content": "Se realizarán trabajos de mantenimiento en el sistema eléctrico principal. Se recomienda usar linternas y mantener áreas despejadas."
            },
            {
                "title": "Reunión de representantes estudiantiles",
                "content": "Los estudiantes están invitados a la reunión mensual de comunicación con la dirección. Será el próximo jueves a las 18:00 en el salón de actos."
            },
            {
                "title": "Programa de actividades culturales",
                "content": "Se han programado actividades deportivas, culturales y recreativas para octubre. Consulte el cronograma en la cartelera principal."
            },
            {
                "title": "Cierre de áreas por reparación",
                "content": "Las áreas del ala norte estarán cerradas por trabajos de reparación estructural. Use rutas alternas."
            },
            {
                "title": "Orientación sobre normas de convivencia",
                "content": "Se llevará a cabo charla informativa sobre normas de convivencia residencial. Asistencia obligatoria para nuevos estudiantes."
            },
            {
                "title": "Apertura de comedor reforzado",
                "content": "El comedor hará servicio ampliado durante período de exámenes. Horario especial comunicado previamente."
            },
            {
                "title": "Control sanitario y fumigación",
                "content": "Se realizará control de plagas y fumigación preventiva. Mantenga cerradas puertas y ventanas según indicaciones."
            },
            {
                "title": "Carga de fichas médicas",
                "content": "Recordamos la obligatoriedad de completar fichas médicas ante enfermería. Plazo límite 15 de septiembre."
            },
            {
                "title": "Beneficiarios de beca especial",
                "content": "Se publican los beneficiarios de beca especial por bajo desempeño. Consulte listado en la dirección."
            },
            {
                "title": "Clausura del año académico",
                "content": "Ceremonia de clausura del año académico 2025-2026. Participación obligatoria de estudiantes residentes."
            },
            {
                "title": "Normas para período de receso",
                "content": "Durante el receso, solo permanecerán en residencia estudiantes autorizados. Consulte requisitos de permanencia."
            },
        ]
        
        comunicadores = [p[0] for p in self.professors if 'comunicador' in p[0].username]
        if not comunicadores:
            # Fallback: usar primer profesor
            comunicadores = [self.professors[0][0]]
        
        start_date = date(2025, 9, 1)
        current_date = start_date
        
        for i, info_data in enumerate(informations_data):
            Information.objects.create(
                title=info_data["title"],
                content=info_data["content"],
                published_date=current_date,
                expires_date=current_date + timedelta(days=30),
                is_public=True,
                created_by=random.choice(comunicadores),
            )
            current_date += timedelta(days=7)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {len(informations_data)} informaciones creadas"))


    def create_reports(self):
        """Crear 8 reportes variados."""
        self.stdout.write("📊 Creando reportes...")
        
        directivos = [p[0] for p in self.professors if 'directivo' in p[0].username or p[0].is_staff]
        if not directivos:
            directivos = [self.professors[0][0]]
        
        reports_data = [
            {
                "name": "Ocupancia por Ala - Septiembre 2025",
                "type": "occupancy",
                "params": {"building_id": self.buildings[0].id if self.buildings else 1, "month": "2025-09"}
            },
            {
                "name": "Evaluaciones del Semestre 2025-2026",
                "type": "evaluations",
                "params": {"semester": "2025-2026", "grade": "all"}
            },
            {
                "name": "Resumen de Quejas - Q1",
                "type": "complaints",
                "params": {"quarter": "Q1", "year": 2025}
            },
            {
                "name": "Estado de Cuartelerías - Octubre",
                "type": "cleaning",
                "params": {"month": "2025-10", "status": "all"}
            },
            {
                "name": "Distribución de Estudiantes por Carrera",
                "type": "students",
                "params": {"filter": "career", "semester": "2025-2026"}
            },
            {
                "name": "Reporte de Asignaciones Activas",
                "type": "assignments",
                "params": {"status": "active", "date": "2025-10-01"}
            },
            {
                "name": "Análisis de Disciplina Residencial",
                "type": "discipline",
                "params": {"period": "2025-2026", "include_recommendations": True}
            },
            {
                "name": "Estadísticas de Ocupación Mensual",
                "type": "statistics",
                "params": {"metric": "occupancy", "months": 3}
            },
        ]
        
        for i, report_data in enumerate(reports_data):
            Report.objects.create(
                name=report_data["name"],
                type=report_data["type"],
                parameters=report_data["params"],
                generated_date=timezone.now() - timedelta(days=i*7),
                generated_by=random.choice(directivos),
                file_url=f"/media/reports/{report_data['type']}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            )
        
        self.stdout.write(self.style.SUCCESS(f"✓ {len(reports_data)} reportes creados"))
