from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from arriendo.models import TipoFaena, Maquinaria, PerfilUsuario

class Command(BaseCommand):
    help = "Carga inicial de datos de prueba para la plataforma de arriendo RentMaq Chile"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Iniciando carga de datos iniciales..."))

        # 1. Crear Usuarios de Prueba (Admin y Estándar)
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser(
                username="admin", 
                email="admin@rentmaq.cl", 
                password="admin123"
            )
            admin_user.first_name = "Rodrigo"
            admin_user.last_name = "Administrador"
            admin_user.save()

            perfil_admin, _ = PerfilUsuario.objects.get_or_create(user=admin_user)
            perfil_admin.rut = "11.111.111-1"
            perfil_admin.telefono = "+56 9 8888 7777"
            perfil_admin.empresa = "RentMaq Chile SpA"
            perfil_admin.rol = "ADMINISTRADOR"
            perfil_admin.save()
            self.stdout.write(self.style.SUCCESS("[OK] Superusuario 'admin' creado exitosamente."))
        else:
            self.stdout.write("Superusuario 'admin' ya existía.")

        if not User.objects.filter(username="cliente").exists():
            cliente_user = User.objects.create_user(
                username="cliente", 
                email="cliente@constructora.cl", 
                password="cliente123"
            )
            cliente_user.first_name = "Carlos"
            cliente_user.last_name = "Contratista"
            cliente_user.save()

            perfil_cli, _ = PerfilUsuario.objects.get_or_create(user=cliente_user)
            perfil_cli.rut = "22.222.222-2"
            perfil_cli.telefono = "+56 9 7777 6666"
            perfil_cli.empresa = "Constructora Andes Ltda."
            perfil_cli.rol = "CLIENTE"
            perfil_cli.save()
            self.stdout.write(self.style.SUCCESS("[OK] Usuario estándar 'cliente' creado exitosamente."))
        else:
            self.stdout.write("Usuario estándar 'cliente' ya existía.")

        # 2. Cargar 4 Clasificadores (TipoFaena)
        faenas_data = [
            {
                "nombre": "Movimiento de Tierra y Excavación",
                "descripcion": "Maquinaria pesada para remoción, zanjado, nivelación y extracción de material rocoso.",
                "icono_bootstrap": "bi-cone-striped"
            },
            {
                "nombre": "Elevación, Montaje y Carga",
                "descripcion": "Equipos de izaje vertical y horizontal para paletizado, contenedores y estructuras.",
                "icono_bootstrap": "bi-arrows-vertical"
            },
            {
                "nombre": "Construcción y Obras Civiles",
                "descripcion": "Maquinaria versátil para edificaciones, fundaciones y transporte interno en obra.",
                "icono_bootstrap": "bi-buildings"
            },
            {
                "nombre": "Pavimentación y Compactación",
                "descripcion": "Equipamiento especializado en sellado asfáltico, rodillos vibratorios y bases estabilizadas.",
                "icono_bootstrap": "bi-bezier2"
            },
        ]

        faenas_creadas = {}
        for f in faenas_data:
            obj, created = TipoFaena.objects.get_or_create(
                nombre=f["nombre"], 
                defaults={"descripcion": f["descripcion"], "icono_bootstrap": f["icono_bootstrap"]}
            )
            faenas_creadas[f["nombre"]] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"[OK] Faena creada: {obj.nombre}"))

        # 3. Cargar al menos 8 Maquinarias Coherentes con el Giro
        maquinarias_data = [
            {
                "codigo": "RET-001",
                "nombre": "Retroexcavadora 4x4 con Brazo Extensible",
                "marca": "Caterpillar",
                "modelo": "420F2",
                "tipo_faena": faenas_creadas["Movimiento de Tierra y Excavación"],
                "potencia_hp": 93,
                "tarifa_diaria": 160000,
                "garantia": 500000,
                "unidades_disponibles": 3,
                "estado": "DISPONIBLE",
                "descripcion": "Capacidad de balde de 1.0 m3. Ideal para zanjas de tuberías, cimentaciones y carga de camiones tolva.",
                "activo": True
            },
            {
                "codigo": "EXC-002",
                "nombre": "Excavadora Hidráulica de Orugas 22 Ton",
                "marca": "Komatsu",
                "modelo": "PC200-8M0",
                "tipo_faena": faenas_creadas["Movimiento de Tierra y Excavación"],
                "potencia_hp": 148,
                "tarifa_diaria": 280000,
                "garantia": 900000,
                "unidades_disponibles": 2,
                "estado": "DISPONIBLE",
                "descripcion": "Profundidad máxima de excavación de 6.6 metros. Excelente estabilidad en terrenos irregulares.",
                "activo": True
            },
            {
                "codigo": "MIN-003",
                "nombre": "Minicargador Frontal con Cabina Cerrada",
                "marca": "Bobcat",
                "modelo": "S570",
                "tipo_faena": faenas_creadas["Construcción y Obras Civiles"],
                "potencia_hp": 61,
                "tarifa_diaria": 95000,
                "garantia": 350000,
                "unidades_disponibles": 5,
                "estado": "DISPONIBLE",
                "descripcion": "Ideal para espacios confinados en obras urbanas. Compatible con martillo hidráulico y balde barrenador.",
                "activo": True
            },
            {
                "codigo": "GRU-004",
                "nombre": "Grúa Horquilla Todo Terreno 3.5 Ton",
                "marca": "Toyota",
                "modelo": "8FG35",
                "tipo_faena": faenas_creadas["Elevación, Montaje y Carga"],
                "potencia_hp": 75,
                "tarifa_diaria": 110000,
                "garantia": 400000,
                "unidades_disponibles": 4,
                "estado": "DISPONIBLE",
                "descripcion": "Mástil triple con elevación máxima de 4.7 metros. Desplazador lateral hidráulico de horquillas.",
                "activo": True
            },
            {
                "codigo": "MAN-005",
                "nombre": "Manipulador Telescópico 17 Metros",
                "marca": "Manitou",
                "modelo": "MT 1840",
                "tipo_faena": faenas_creadas["Elevación, Montaje y Carga"],
                "potencia_hp": 100,
                "tarifa_diaria": 210000,
                "garantia": 700000,
                "unidades_disponibles": 2,
                "estado": "DISPONIBLE",
                "descripcion": "Alcance vertical de 17.5 metros con estabilizadores hidráulicos. Apto para faenas portuarias y mineras.",
                "activo": True
            },
            {
                "codigo": "ROD-006",
                "nombre": "Rodillo Compactador Vibratorio Tandem",
                "marca": "Bomag",
                "modelo": "BW 120 AD-5",
                "tipo_faena": faenas_creadas["Pavimentación y Compactación"],
                "potencia_hp": 34,
                "tarifa_diaria": 130000,
                "garantia": 450000,
                "unidades_disponibles": 3,
                "estado": "DISPONIBLE",
                "descripcion": "Doble tambor vibratorio para compactación fina de asfalto y sub-bases granulares en caminos.",
                "activo": True
            },
            {
                "codigo": "MOT-007",
                "nombre": "Motoniveladora Articulada 14 Pies",
                "marca": "Caterpillar",
                "modelo": "140K",
                "tipo_faena": faenas_creadas["Pavimentación y Compactación"],
                "potencia_hp": 190,
                "tarifa_diaria": 320000,
                "garantia": 1100000,
                "unidades_disponibles": 1,
                "estado": "DISPONIBLE",
                "descripcion": "Hoja vertedera de alta precisión para perfiles de pendientes, cunetas y mantención de caminos mineros.",
                "activo": True
            },
            {
                "codigo": "TIJ-008",
                "nombre": "Plataforma Elevadora Tipo Tijera 12 Metros",
                "marca": "Genie",
                "modelo": "GS-3246",
                "tipo_faena": faenas_creadas["Construcción y Obras Civiles"],
                "potencia_hp": 25,
                "tarifa_diaria": 85000,
                "garantia": 300000,
                "unidades_disponibles": 4,
                "estado": "DISPONIBLE",
                "descripcion": "Operación eléctrica silenciosa y libre de emisiones para trabajos en interiores, galpones e instalaciones.",
                "activo": True
            },
        ]

        for m in maquinarias_data:
            obj, created = Maquinaria.objects.get_or_create(
                codigo=m["codigo"],
                defaults=m
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"[OK] Maquinaria cargada: [{obj.codigo}] {obj.nombre}"))

        self.stdout.write(self.style.SUCCESS("\n¡Poblado de datos finalizado con éxito!"))
