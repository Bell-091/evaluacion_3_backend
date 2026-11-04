from django.contrib import admin
from .models import TipoFaena, Maquinaria, PerfilUsuario

# ------------------------------------------------------------------------------
# 1. PERSONALIZACIÓN CORPORATIVA DEL SITIO ADMINISTRATIVO
# ------------------------------------------------------------------------------
admin.site.site_header = "RentMaq Chile - Panel de Control Operativo"
admin.site.site_title = "RentMaq Admin"
admin.site.index_title = "Gestión Operativa de Recursos y Servicios de Maquinaria"


# ------------------------------------------------------------------------------
# 2. ADMINISTRADOR DE TIPOS DE FAENA
# ------------------------------------------------------------------------------
@admin.register(TipoFaena)
class TipoFaenaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'icono_bootstrap', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('fecha_creacion',)


# ------------------------------------------------------------------------------
# 3. ADMINISTRADOR AVANZADO DE MAQUINARIA
# ------------------------------------------------------------------------------
@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    # Columnas mostradas en la tabla principal
    list_display = (
        'codigo', 
        'nombre', 
        'marca', 
        'tipo_faena', 
        'tarifa_diaria', 
        'garantia', 
        'estado', 
        'activo'
    )

    # Filtros laterales interactivos
    list_filter = (
        'tipo_faena', 
        'estado', 
        'activo', 
        'fecha_ingreso'
    )

    # Campos de búsqueda textual
    search_fields = (
        'codigo', 
        'nombre', 
        'marca', 
        'modelo', 
        'descripcion'
    )

    # Edición rápida sin abrir la ficha
    list_editable = (
        'tarifa_diaria', 
        'estado', 
        'activo'
    )

    # Paginación en admin
    list_per_page = 10

    # Organización modular del formulario en secciones
    fieldsets = (
        ('Identificación y Clasificación', {
            'fields': ('codigo', 'nombre', 'marca', 'modelo', 'tipo_faena')
        }),
        ('Capacidades Técnicas y Operativas', {
            'fields': ('potencia_hp', 'unidades_disponibles', 'estado', 'descripcion')
        }),
        ('Valores Comerciales y Arancel', {
            'fields': ('tarifa_diaria', 'garantia'),
            'description': 'Tarifas en pesos chilenos (CLP) sujetas a validación de no negatividad.'
        }),
        ('Soporte Multimedia y Vigencia', {
            'fields': ('imagen', 'activo')
        }),
    )


# ------------------------------------------------------------------------------
# 4. ADMINISTRADOR DE PERFILES DE USUARIO
# ------------------------------------------------------------------------------
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'telefono', 'empresa', 'rol')
    search_fields = ('user__username', 'rut', 'empresa')
    list_filter = ('rol',)
