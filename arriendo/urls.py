from django.urls import path
from . import views

urlpatterns = [
    # Catálogo público y Detalle
    path('', views.catalogo_view, name='catalogo'),
    path('maquinaria/<str:codigo>/', views.detalle_maquinaria_view, name='detalle_maquinaria'),

    # Backoffice / CRUD protegido
    path('gestion/', views.panel_gestion_view, name='panel_gestion'),
    path('gestion/crear/', views.crear_maquinaria_view, name='crear_maquinaria'),
    path('gestion/editar/<str:codigo>/', views.editar_maquinaria_view, name='editar_maquinaria'),
    path('gestion/eliminar/<str:codigo>/', views.eliminar_maquinaria_view, name='eliminar_maquinaria'),

    # Canasta de Arriendo y Cotizador (request.session)
    path('canasta/', views.ver_canasta_view, name='ver_canasta'),
    path('canasta/agregar/<int:maquinaria_id>/', views.agregar_canasta_view, name='agregar_canasta'),
    path('canasta/actualizar/<int:maquinaria_id>/', views.actualizar_canasta_view, name='actualizar_canasta'),
    path('canasta/eliminar/<int:maquinaria_id>/', views.eliminar_de_canasta_view, name='eliminar_de_canasta'),
    path('canasta/vaciar/', views.vaciar_canasta_view, name='vaciar_canasta'),
    path('canasta/confirmar/', views.confirmar_cotizacion_view, name='confirmar_cotizacion'),

    # Autenticación y Perfil
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),

    # Bitácora de Inteligencia Artificial (Criterio 2.1.4)
    path('bitacora-ia/', views.bitacora_ia_view, name='bitacora_ia'),
]
