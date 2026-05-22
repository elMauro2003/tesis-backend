"""
Management command para cargar datos de prueba realistas en la BD.

Este comando puebla la BD con:
- 3 sedes, 8 edificios, 24 alas, 120 cuartos
- 2 facultades, 3 carreras, 5 años académicos, 15 grupos
- 9 profesores con roles asignados
- 60 estudiantes con asignaciones a cuartos
- 30 evaluaciones distribuidas en el semestre
- 20 quejas en varios estados
- 10 cuartelerías
- Informaciones y reportes

Año académico: Septiembre 2025 — Julio 2026
"""

import random
from datetime import datetime, date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db.models import F
from django.utils import timezone

from apps.academic.models import Faculty, Career, CareerYear, Group as StudentGroup
from apps.actors.models import Student, Professor, Dean, YearLeadProfessor, GroupAdvisor, WingSupervisor
from apps.infrastructure.models import Site, Building, Wing, Room
from apps.operations.models import Assignment, Complaint, Evaluation, CleaningSchedule, Information, Report


class Command(BaseCommand):
    help = "Carga datos de prueba completos en la BD"

    def handle(self, *args, **options):
        self.stdout.write("🌱 Iniciando seed database...")
        
        try:
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
            self.stdout.write(
                "📊 Totales:\n"
                "   3 sedes\n"
                "   8 edificios\n"
                "   24 alas\n"
                "   120 cuartos\n"
                "   2 facultades\n"
                "   3 carreras\n"
                "   5 años académicos\n"
                "   15 grupos\n"
                "   9 profesores\n"
                "   60 estudiantes\n"
                "   30 evaluaciones\n"
                "   20 quejas\n"
                "   10 cuartelerías\n"
                "   5 informaciones\n"
                "   2 reportes\n"
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            raise

    def create_infrastructure(self):
        """Crear sedes, edificios, alas y cuartos."""
        self.stdout.write("📍 Creando infraestructura...")
        
        # Sedes
        sites_data = [
            {"name": "Sede Central", "address": "Campus Principal, Las Villas"},
            {"name": "Sede Pedagógico", "address": "Facultad de Educación, Las Villas"},
            {"name": "Sede Fajardo", "address": "Complejo Fajardo, Las Villas"},
        ]
        sites = [Site.objects.get_or_create(name=s["name"], defaults={"address": s["address"]})[0] for s in sites_data]
        
        # Edificios
        buildings_per_site = 2 if len(sites) == 3 else 3
        buildings = []
        for site in sites:
            for i in range(buildings_per_site):
                building, _ = Building.objects.get_or_create(
                    name=f"Edificio {chr(65+i)} - {site.name}",
                    site=site
                )
                buildings.append(building)
        
        # Alas por edificio
        wings_per_building = 3
        wings = []
        for building in buildings:
            for i in range(wings_per_building):
                wing, _ = Wing.objects.get_or_create(
                    name=f"Ala {chr(65+i)}",
                    building=building
                )
                wings.append(wing)
        
        # Cuartos por ala (5 cuartos * 24 alas = 120 cuartos)
        rooms_per_wing = 5
        for wing in wings:
            for i in range(rooms_per_wing):
                room_number = f"{wing.building.id:02d}{wing.id:02d}{i+1:02d}"
                Room.objects.get_or_create(
                    number=room_number,
                    wing=wing,
                    defaults={
                        "capacity": 4,
                        "is_active": True,
                        "current_occupancy": 0,
                    }
                )
        
        self.stdout.write(self.style.SUCCESS("✓ Infraestructura creada"))

    def create_academic_structure(self):
        """Crear estructura académica: facultades, carreras, años, grupos."""
        self.stdout.write("🎓 Creando estructura académica...")
        
        # Facultades
        faculties_data = [
            {"name": "Facultad de Matemática, Física y Computación", "code": "MATFISCOM"},
            {"name": "Facultad de Ingeniería", "code": "ING"},
        ]
        faculties = [
            Faculty.objects.get_or_create(name=f["name"], defaults={"code": f["code"]})[0]
            for f in faculties_data
        ]
        
        # Carreras
        careers_data = [
            {"name": "Ingeniería en Ciencias Informáticas", "code": "ICI", "faculty": 0},
            {"name": "Ingeniería Eléctrica", "code": "EE", "faculty": 1},
            {"name": "Ingeniería Civil", "code": "EC", "faculty": 1},
        ]
        careers = []
        for c in careers_data:
            career, _ = Career.objects.get_or_create(
                code=c["code"],
                defaults={"name": c["name"], "faculty": faculties[c["faculty"]]}
            )
            careers.append(career)
        
        # Años académicos
        years = []
        for career in careers:
            for year_num in range(1, 6):  # 1º a 5º año
                year, _ = CareerYear.objects.get_or_create(
                    career=career,
                    year=year_num
                )
                years.append(year)
        
        # Grupos de estudiantes
        groups = []
        for year in years:
            for group_letter in ["A", "B", "C"]:
                group_name = f"{year.career.code}-{year.year}-{group_letter}"
                group, _ = StudentGroup.objects.get_or_create(
                    name=group_name,
                    career_year=year
                )
                groups.append(group)
        
        self.stdout.write(self.style.SUCCESS("✓ Estructura académica creada"))
        self.groups = groups  # Guardamos para usar en students

    def create_professors(self):
        """Crear profesores y asignarles roles."""
        self.stdout.write("👨‍🏫 Creando profesores con roles...")
        
        # Usuarios base
        professors_data = [
            {"username": "profesor_decano", "email": "prof_decano@uclv.cu", "first_name": "Juan", "last_name": "López"},
            {"username": "profesor_ppa_1", "email": "prof_ppa1@uclv.cu", "first_name": "María", "last_name": "Rodríguez"},
            {"username": "profesor_ppa_2", "email": "prof_ppa2@uclv.cu", "first_name": "Pedro", "last_name": "González"},
            {"username": "profesor_pg_1", "email": "prof_pg1@uclv.cu", "first_name": "Carmen", "last_name": "Martínez"},
            {"username": "profesor_pg_2", "email": "prof_pg2@uclv.cu", "first_name": "Roberto", "last_name": "Díaz"},
            {"username": "profesor_ala_1", "email": "prof_ala1@uclv.cu", "first_name": "Sofía", "last_name": "Vargas"},
            {"username": "profesor_ala_2", "email": "prof_ala2@uclv.cu", "first_name": "Luis", "last_name": "Castro"},
            {"username": "instructor_1", "email": "instructor1@uclv.cu", "first_name": "Carlos", "last_name": "Martínez"},
            {"username": "instructor_2", "email": "instructor2@uclv.cu", "first_name": "Ana", "last_name": "Jiménez"},
        ]
        
        professors = []
        for prof_data in professors_data:
            user, _ = User.objects.get_or_create(
                username=prof_data["username"],
                defaults={
                    "email": prof_data["email"],
                    "first_name": prof_data["first_name"],
                    "last_name": prof_data["last_name"],
                }
            )
            if not user.has_usable_password():
                user.set_password("Password123!")
                user.save()
            
            professor, _ = Professor.objects.get_or_create(
                user=user,
                defaults={
                    "employee_id": f"EMP-{user.id:05d}",
                    "department": "Dirección de Becas",
                }
            )
            professors.append((user, professor))
            
            # Asignar rol 'profesor'
            prof_group, _ = Group.objects.get_or_create(name='professor')
            user.groups.add(prof_group)
        
        # Asignar sub-roles específicos
        # Decano
        dean_user = professors[0][0]
        dean_user.groups.add(Group.objects.get(name='decano'))
        faculty = Faculty.objects.first()
        Dean.objects.get_or_create(
            professor=professors[0][1],
            defaults={"faculty": faculty}
        )
        
        # PPAs (2)
        for i in range(1, 3):
            ppa_user = professors[i][0]
            ppa_user.groups.add(Group.objects.get(name='ppa'))
            year = CareerYear.objects.all()[i-1]
            YearLeadProfessor.objects.get_or_create(
                professor=professors[i][1],
                defaults={"career_year": year}
            )
        
        # Profesores Guía (2)
        for i in range(3, 5):
            pg_user = professors[i][0]
            pg_user.groups.add(Group.objects.get(name='pg'))
            group = self.groups[i-3]
            GroupAdvisor.objects.get_or_create(
                professor=professors[i][1],
                defaults={"group": group}
            )
        
        # Responsables de Alas (2)
        wings = Wing.objects.all()[:2]
        for i, wing in enumerate(wings):
            ala_user = professors[5+i][0]
            ala_user.groups.add(Group.objects.get(name='instructor'))
            WingSupervisor.objects.get_or_create(
                professor=professors[5+i][1],
                defaults={"wing": wing}
            )
        
        # Instructores regulares (2)
        for i in range(7, 9):
            instr_user = professors[i][0]
            instr_user.groups.add(Group.objects.get(name='instructor'))
        
        self.stdout.write(self.style.SUCCESS("✓ Profesores creados"))
        self.professors = professors

    def create_students(self):
        """Crear estudiantes y asignarles cuartos."""
        self.stdout.write("👥 Creando estudiantes y asignaciones...")
        
        # Datos de ejemplo
        first_names = ["Luis", "María", "Carlos", "Ana", "Pedro", "Sofia", "Juan", "Rosa", "Miguel", "Elena"]
        last_names = ["García", "López", "González", "Martínez", "Rodríguez", "Pérez", "Jiménez", "Vargas", "Díaz", "Castro"]
        
        students_created = 0
        rooms = Room.objects.all().order_by('id')
        
        for group_idx, group in enumerate(self.groups[:15]):  # 15 grupos
            for student_num in range(4):  # 4 estudiantes por grupo
                student_num_global = group_idx * 4 + student_num + 1
                
                # Datos del usuario
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                username = f"student_{student_num_global:03d}"
                email = f"{username}@uclv.cu"
                
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
                
                # Asignar rol estudiante
                user.groups.add(Group.objects.get(name='estudiante'))
                
                # Crear estudiante
                student, _ = Student.objects.get_or_create(
                    user=user,
                    defaults={
                        "ci": f"{random.randint(90000000000, 99999999999)}",
                        "student_id": f"{group.career_year.career.code}-2025-{student_num_global:03d}",
                        "birth_date": date(random.randint(1999, 2005), random.randint(1, 12), random.randint(1, 28)),
                        "gender": random.choice(['M', 'F']),
                        "group": group,
                        "address": f"Calle {random.randint(1, 100)}, Apt {random.randint(1, 99)}",
                        "province": "Villa Clara",
                        "municipality": "Santa Clara",
                        "phone": f"+53 4222-{random.randint(1000, 9999)}",
                        "is_militant": random.choice([True, False]),
                    }
                )
                
                # Asignar cuarto en el primer cuarto activo con plazas disponibles
                room = Room.objects.filter(
                    is_active=True,
                    current_occupancy__lt=F("capacity"),
                ).order_by("id").first()

                if room is not None:
                    Assignment.objects.get_or_create(
                        student=student,
                        defaults={
                            "room": room,
                            "assigned_date": date(2025, 9, 15),
                            "assigned_by": self.professors[-1][0],  # Instructor
                        }
                    )
                
                students_created += 1
        
        self.stdout.write(self.style.SUCCESS(f"✓ {students_created} estudiantes creados"))
        self.students = Student.objects.all()
        self.first_user = User.objects.get(username="student_001")  # Para login de prueba

    def create_evaluations(self):
        """Crear evaluaciones distribuidas en el semestre."""
        self.stdout.write("📋 Creando evaluaciones...")
        
        evaluations_created = 0
        grades = ['B', 'R', 'M']
        comments = [
            "Comportamiento ejemplar",
            "Participación activa",
            "Incumplimiento de normas",
            "Necesita mejorar",
            "Excelente desempeño",
        ]
        
        # Distribuir evaluaciones a lo largo del semestre (sep 2025 - jul 2026)
        start_date = date(2025, 9, 15)
        end_date = date(2026, 7, 31)
        current_date = start_date
        
        while current_date < end_date and evaluations_created < 30:
            for student in self.students[:random.randint(5, 15)]:
                if evaluations_created < 30:
                    Evaluation.objects.create(
                        student=student,
                        date=current_date,
                        grade=random.choice(grades),
                        comment=random.choice(comments),
                        created_by=random.choice([p[0] for p in self.professors]),
                    )
                    evaluations_created += 1
            
            # Avanzar 4 semanas
            current_date += timedelta(days=28)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {evaluations_created} evaluaciones creadas"))

    def create_complaints(self):
        """Crear quejas en varios estados."""
        self.stdout.write("🗣️ Creando quejas...")
        
        statuses = ['pendiente', 'en_proceso', 'resuelta']
        complaint_types = ['administrativa', 'educativa']
        descriptions = [
            "Fuga de agua en el baño","Falta de agua caliente",
            "Problema con electricidad",
            "Deterioro del equipamiento",
            "Mala coordinación de cuartelerías",
            "Necesidad de mantenimiento urgente",
            "Falta de higiene en áreas comunes",
        ]
        
        buildings = Building.objects.all()
        complaints_created = 0
        
        start_date = date(2025, 9, 20)
        current_date = start_date
        
        while current_date < date(2026, 7, 31) and complaints_created < 20:
            for _ in range(random.randint(1, 3)):
                if complaints_created < 20:
                    Complaint.objects.create(
                        student=random.choice(self.students),
                        date=current_date,
                        building=random.choice(buildings),
                        description=random.choice(descriptions),
                        type=random.choice(complaint_types),
                        status=random.choice(statuses),
                        response="Orden enviada a mantenimiento" if random.choice([True, False]) else None,
                        response_date=timezone.make_aware(datetime.combine(current_date + timedelta(days=2), datetime.min.time())) if complaints_created % 2 == 0 else None,
                        visibility=random.choice([True, False]),
                    )
                    complaints_created += 1
            
            current_date += timedelta(days=7)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {complaints_created} quejas creadas"))

    def create_cleaning_schedules(self):
        """Crear cuartelerías."""
        self.stdout.write("🧹 Creando cuartelerías...")
        
        rooms = Room.objects.all()
        evaluations = ['B', 'R', 'M']
        cleaning_created = 0
        
        start_date = date(2025, 9, 22)
        current_date = start_date
        
        while current_date < date(2026, 7, 31) and cleaning_created < 10:
            for room in rooms[:random.randint(10, 20)]:
                if cleaning_created < 10:
                    students = Student.objects.filter(assignments__room=room, assignments__released_date__isnull=True)
                    if students.exists():
                        CleaningSchedule.objects.create(
                            room=room,
                            student=random.choice(students),
                            assigned_date=current_date,
                            completed=random.choice([True, False]),
                            evaluation=random.choice(evaluations) if random.choice([True, False]) else None,
                            comments="Se limpió satisfactoriamente" if random.choice([True, False]) else "",
                        )
                        cleaning_created += 1
            
            current_date += timedelta(days=7)
        
        self.stdout.write(self.style.SUCCESS(f"✓ {cleaning_created} cuartelerías creadas"))

    def create_informations(self):
        """Crear informaciones/noticias."""
        self.stdout.write("📢 Creando informaciones...")
        
        titles = [
            "Suspensión de agua caliente",
            "Mantenimiento de electricidad",
            "Reunión de estudiantes",
            "Programa de actividades especiales",
            "Cierre de áreas por reparación",
        ]
        
        contents = [
            "Por mantenimiento, el agua caliente estará suspendida hasta las 18:00 horas.",
            "Se realizarán trabajos de mantenimiento en el sistema eléctrico.",
            "Los estudiantes están invitados a la reunión mensual.",
            "Se han programado actividades deportivas y culturales.",
            "Algunas áreas estarán cerradas por trabajos de reparación.",
        ]
        
        start_date = date(2025, 10, 1)
        current_date = start_date
        
        for i in range(5):
            Information.objects.create(
                title=titles[i],
                content=contents[i],
                published_date=current_date,
                expires_date=current_date + timedelta(days=7),
                is_public=True,
                created_by=random.choice([p[0] for p in self.professors]),
            )
            current_date += timedelta(days=14)
        
        self.stdout.write(self.style.SUCCESS("✓ 5 informaciones creadas"))

    def create_reports(self):
        """Crear reportes."""
        self.stdout.write("📊 Creando reportes...")
        
        Report.objects.create(
            name="Ocupancia por Ala - Octubre 2025",
            type="occupancy",
            parameters={
                "building_id": Building.objects.first().id,
                "month": "2025-10"
            },
            generated_date=timezone.now(),
            generated_by=self.professors[0][0],
            file_url="/media/reports/occupancy_20251001.pdf",
        )
        
        Report.objects.create(
            name="Evaluaciones - Semestre 2025-2026",
            type="evaluations",
            parameters={
                "semester": "2025-2026"
            },
            generated_date=timezone.now(),
            generated_by=self.professors[0][0],
            file_url="/media/reports/evaluations_20250950.pdf",
        )
        
        self.stdout.write(self.style.SUCCESS("✓ 2 reportes creados"))
