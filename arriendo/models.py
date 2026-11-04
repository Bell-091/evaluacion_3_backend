from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ------------------------------------------------------------------------------
# 1. ENTIDAD DE CONTEXTO / AGRUPACIÓN: TipoFaena
# Representa la clasificación temática de las faenas operativas
# ------------------------------------------------------------------------------
class TipoFaena(models.Model):
    nombre = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Nombre de la Faena"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Descripción operativa"
    )
    icono_bootstrap = models.CharField(
        max_length=50, 
        default="bi-tools", 
        verbose_name="Ícono Bootstrap"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Registro"
    )

    class Meta:
        verbose_name = "Tipo de Faena"
        verbose_name_plural = "Tipos de Faenas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# ------------------------------------------------------------------------------
# 2. ENTIDAD PRINCIPAL GESTIONABLE: Maquinaria
# Representa cada equipo o máquina disponible para arriendo
# ------------------------------------------------------------------------------
class Maquinaria(models.Model):
    # Opciones cerradas de estado operativo (choices)
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible para Arriendo'),
        ('EN_FAENA', 'En Faena / Arrendada'),
        ('MANTENIMIENTO', 'En Mantenimiento Preventivo'),
        ('FUERA_SERVICIO', 'Fuera de Servicio'),
    ]

    # Identificación única alfanumérica
    codigo = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Código de Inventario"
    )
    nombre = models.CharField(
        max_length=150, 
        verbose_name="Nombre del Equipo"
    )
    marca = models.CharField(
        max_length=80, 
        verbose_name="Marca"
    )
    modelo = models.CharField(
        max_length=80, 
        verbose_name="Modelo"
    )

    # Relación referencial protegida (on_delete=models.PROTECT)
    tipo_faena = models.ForeignKey(
        TipoFaena, 
        on_delete=models.PROTECT, 
        related_name="maquinarias", 
        verbose_name="Tipo de Faena / Clasificación"
    )

    # Atributos cuantitativos con validadores anti-negativos
    potencia_hp = models.IntegerField(
        validators=[MinValueValidator(1, message="La potencia debe ser de al menos 1 HP")],
        verbose_name="Potencia (HP)"
    )
    tarifa_diaria = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        validators=[MinValueValidator(0, message="La tarifa diaria no puede ser negativa")],
        verbose_name="Tarifa Diaria (CLP)"
    )
    garantia = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        validators=[MinValueValidator(0, message="La fianza de garantía no puede ser negativa")],
        verbose_name="Fianza de Garantía (CLP)"
    )
    unidades_disponibles = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0, message="Las unidades no pueden ser negativas")],
        verbose_name="Unidades Disponibles en Parque"
    )

    # Estado con choices
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='DISPONIBLE', 
        verbose_name="Condición Operativa"
    )

    # Soporte multimedia
    imagen = models.ImageField(
        upload_to='maquinarias/', 
        blank=True, 
        null=True, 
        verbose_name="Fotografía del Equipo"
    )

    # Atributos descriptivos
    descripcion = models.TextField(
        verbose_name="Especificaciones y Descripción Técnica"
    )

    # Control de vigencia / baja lógica
    activo = models.BooleanField(
        default=True, 
        verbose_name="Vigente / Habilitado"
    )
    fecha_ingreso = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Fecha de Alta en Sistema"
    )

    class Meta:
        verbose_name = "Maquinaria"
        verbose_name_plural = "Maquinarias"
        ordering = ['-fecha_ingreso']

    def __str__(self):
        return f"[{self.codigo}] {self.nombre} - {self.marca}"


# ------------------------------------------------------------------------------
# 3. ENTIDAD DE PERFIL COMPLEMENTARIO: PerfilUsuario
# Extiende django.contrib.auth.models.User con datos específicos de la empresa
# ------------------------------------------------------------------------------
class PerfilUsuario(models.Model):
    ROLES_CHOICES = [
        ('ADMINISTRADOR', 'Administrador de Flota'),
        ('OPERADOR', 'Operador de Logística'),
        ('CLIENTE', 'Cliente Corporativo'),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="perfil", 
        verbose_name="Usuario"
    )
    rut = models.CharField(
        max_length=12, 
        unique=True, 
        verbose_name="RUT / DNI"
    )
    telefono = models.CharField(
        max_length=20, 
        verbose_name="Teléfono de Contacto"
    )
    empresa = models.CharField(
        max_length=120, 
        blank=True, 
        null=True, 
        verbose_name="Razón Social / Empresa"
    )
    rol = models.CharField(
        max_length=20, 
        choices=ROLES_CHOICES, 
        default='CLIENTE', 
        verbose_name="Rol en Plataforma"
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()}) - RUT: {self.rut}"


# Signal para crear o actualizar el perfil automáticamente cuando se crea un User
@receiver(post_save, sender=User)
def crear_o_guardar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.get_or_create(user=instance, defaults={'rut': f'TEMP-{instance.id}'})
    else:
        if hasattr(instance, 'perfil'):
            instance.perfil.save()
