import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Maquinaria, TipoFaena, PerfilUsuario
from .forms import MaquinariaForm, RegistroUsuarioForm
from .cart import CanastaArriendo

# Función de verificación para acceso Staff / Administrador
def es_personal_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ------------------------------------------------------------------------------
# 1. CATÁLOGO PÚBLICO (Read - Catálogo, Buscador Q, Filtros, Paginación)
# ------------------------------------------------------------------------------
def catalogo_view(request):
    faena_id = request.GET.get('faena')
    query = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', 'reciente')

    # Consulta base optimizada con select_related para evitar problema N+1
    maquinarias = Maquinaria.objects.filter(activo=True).select_related('tipo_faena')

    # Filtro por tipo de faena
    if faena_id:
        maquinarias = maquinarias.filter(tipo_faena_id=faena_id)

    # Buscador multi-campo con Q (nombre, código, marca, descripción)
    if query:
        maquinarias = maquinarias.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(marca__icontains=query) |
            Q(descripcion__icontains=query)
        )

    # Ordenamiento
    if orden == 'precio_asc':
        maquinarias = maquinarias.order_by('tarifa_diaria')
    elif orden == 'precio_desc':
        maquinarias = maquinarias.order_by('-tarifa_diaria')
    elif orden == 'nombre':
        maquinarias = maquinarias.order_by('nombre')
    else:
        maquinarias = maquinarias.order_by('-fecha_ingreso')

    # Paginación (6 equipos por página)
    paginator = Paginator(maquinarias, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    faenas = TipoFaena.objects.all()

    context = {
        'page_obj': page_obj,
        'faenas': faenas,
        'faena_seleccionada': faena_id,
        'query': query,
        'orden': orden,
    }
    return render(request, 'arriendo/catalogo.html', context)


# ------------------------------------------------------------------------------
# 2. FICHA DE DETALLE (Read)
# ------------------------------------------------------------------------------
def detalle_maquinaria_view(request, codigo):
    maquinaria = get_object_or_404(Maquinaria.objects.select_related('tipo_faena'), codigo=codigo, activo=True)
    return render(request, 'arriendo/detalle.html', {'maquinaria': maquinaria})


# ------------------------------------------------------------------------------
# 3. CREAR MAQUINARIA (Create - Protegido Staff)
# ------------------------------------------------------------------------------
@login_required
@user_passes_test(es_personal_staff, login_url='catalogo')
def crear_maquinaria_view(request):
    if request.method == 'POST':
        form = MaquinariaForm(request.POST, request.FILES)
        if form.is_valid():
            maquinaria = form.save()
            messages.success(request, f"¡Equipo '{maquinaria.nombre}' registrado exitosamente con código {maquinaria.codigo}!")
            return redirect('panel_gestion')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = MaquinariaForm()

    return render(request, 'arriendo/formulario_maquinaria.html', {
        'form': form, 
        'titulo': 'Alta de Nueva Maquinaria'
    })


# ------------------------------------------------------------------------------
# 4. EDITAR MAQUINARIA (Update - Protegido Staff)
# ------------------------------------------------------------------------------
@login_required
@user_passes_test(es_personal_staff, login_url='catalogo')
def editar_maquinaria_view(request, codigo):
    maquinaria = get_object_or_404(Maquinaria, codigo=codigo)
    if request.method == 'POST':
        form = MaquinariaForm(request.POST, request.FILES, instance=maquinaria)
        if form.is_valid():
            form.save()
            messages.success(request, f"Equipo '{maquinaria.nombre}' actualizado correctamente.")
            return redirect('panel_gestion')
        else:
            messages.error(request, "Ocurrió un error al intentar actualizar la información.")
    else:
        form = MaquinariaForm(instance=maquinaria)

    return render(request, 'arriendo/formulario_maquinaria.html', {
        'form': form, 
        'titulo': f'Modificación de Equipo: {maquinaria.codigo}',
        'maquinaria': maquinaria
    })


# ------------------------------------------------------------------------------
# 5. ELIMINAR / BAJA LÓGICA (Delete - Protegido Staff)
# ------------------------------------------------------------------------------
@login_required
@user_passes_test(es_personal_staff, login_url='catalogo')
def eliminar_maquinaria_view(request, codigo):
    maquinaria = get_object_or_404(Maquinaria, codigo=codigo)

    if request.method == 'POST':
        # Aplicamos baja lógica para mantener trazabilidad histórica
        maquinaria.activo = False
        maquinaria.save()
        messages.warning(request, f"El equipo '{maquinaria.nombre}' ha sido desactivado del catálogo operativo (Baja lógica).")
        return redirect('panel_gestion')

    return render(request, 'arriendo/confirmar_eliminar.html', {'maquinaria': maquinaria})


# ------------------------------------------------------------------------------
# 6. PANEL DE GESTIÓN BACKOFFICE (Protegido Staff)
# ------------------------------------------------------------------------------
@login_required
@user_passes_test(es_personal_staff, login_url='catalogo')
def panel_gestion_view(request):
    maquinarias = Maquinaria.objects.all().select_related('tipo_faena').order_by('-fecha_ingreso')
    return render(request, 'arriendo/panel_gestion.html', {'maquinarias': maquinarias})


# ------------------------------------------------------------------------------
# 7. VISTAS DEL COTIZADOR Y CANASTA DE ARRIENDO (request.session)
# ------------------------------------------------------------------------------
def agregar_canasta_view(request, maquinaria_id):
    maquinaria = get_object_or_404(Maquinaria, id=maquinaria_id, activo=True)
    if maquinaria.estado != 'DISPONIBLE':
        messages.error(request, f"El equipo {maquinaria.nombre} no se encuentra disponible para arriendo.")
        return redirect('detalle_maquinaria', codigo=maquinaria.codigo)

    dias = int(request.POST.get('dias', 1))
    if dias < 1:
        dias = 1

    canasta = CanastaArriendo(request)
    canasta.agregar(maquinaria=maquinaria, dias=dias)
    messages.success(request, f"'{maquinaria.nombre}' fue añadido a tu cotizador por {dias} día(s).")
    return redirect('ver_canasta')


def ver_canasta_view(request):
    canasta = CanastaArriendo(request)
    resumen = canasta.obtener_resumen()
    return render(request, 'arriendo/canasta.html', {'resumen': resumen})


def actualizar_canasta_view(request, maquinaria_id):
    if request.method == 'POST':
        dias = int(request.POST.get('dias', 1))
        canasta = CanastaArriendo(request)
        canasta.actualizar_dias(maquinaria_id, dias)
        messages.info(request, "Plazo de arriendo actualizado correctamente.")
    return redirect('ver_canasta')


def eliminar_de_canasta_view(request, maquinaria_id):
    canasta = CanastaArriendo(request)
    canasta.eliminar(maquinaria_id)
    messages.warning(request, "Equipo removido del cotizador.")
    return redirect('ver_canasta')


def vaciar_canasta_view(request):
    canasta = CanastaArriendo(request)
    canasta.vaciar()
    messages.info(request, "El cotizador ha sido vaciado por completo.")
    return redirect('catalogo')


def confirmar_cotizacion_view(request):
    """
    Genera el comprobante final de solicitud y vacía la sesión
    """
    canasta = CanastaArriendo(request)
    resumen = canasta.obtener_resumen()

    if not resumen['items']:
        messages.error(request, "Tu cotizador está vacío.")
        return redirect('catalogo')

    codigo_solicitud = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    datos_comprobante = {
        'codigo_solicitud': codigo_solicitud,
        'resumen': resumen,
    }

    # Vaciar la sesión tras generar el comprobante
    canasta.vaciar()
    messages.success(request, f"¡Solicitud de arriendo #{codigo_solicitud} formalizada con éxito!")
    return render(request, 'arriendo/comprobante.html', datos_comprobante)


# ------------------------------------------------------------------------------
# 8. AUTENTICACIÓN Y REGISTRO DE USUARIOS
# ------------------------------------------------------------------------------
def registro_view(request):
    if request.user.is_authenticated:
        return redirect('catalogo')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Guardar datos del Perfil
            perfil = user.perfil
            perfil.rut = form.cleaned_data['rut']
            perfil.telefono = form.cleaned_data['telefono']
            perfil.empresa = form.cleaned_data['empresa']
            perfil.rol = 'CLIENTE'
            perfil.save()

            login(request, user)
            messages.success(request, f"¡Bienvenido a RentMaq, {user.first_name or user.username}!")
            return redirect('catalogo')
        else:
            messages.error(request, "Revise los campos señalados.")
    else:
        form = RegistroUsuarioForm()

    return render(request, 'arriendo/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalogo')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Sesión iniciada correctamente. Hola, {user.username}.")
            return redirect(request.GET.get('next', 'catalogo'))
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()

    return render(request, 'arriendo/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado tu sesión de forma segura.")
    return redirect('catalogo')


@login_required
def perfil_view(request):
    return render(request, 'arriendo/perfil.html', {'user': request.user})


# ------------------------------------------------------------------------------
# 9. BITÁCORA DE USO TÉCNICO Y ÉTICO DE IA (Criterio 2.1.4)
# ------------------------------------------------------------------------------
def bitacora_ia_view(request):
    """
    Ruta interactiva que expone la Bitácora de Inteligencia Artificial
    con los prompts técnicos, respuestas obtenidas y adaptaciones críticas aplicadas.
    """
    casos_ia = [
        {
            'numero': 1,
            'titulo': 'Arquitectura ORM y Protección de Integridad Relacional',
            'herramienta': 'Claude 3.5 Sonnet / Antigravity',
            'area': 'Modelado Relacional y Validaciones',
            'criterio': 'Criterio 2.1.1 (ORM y Conexión BD)',
            'icono': 'bi-database-fill-lock',
            'prompt': (
                "Actúa como un arquitecto de software Django sénior. Para una plataforma de arriendo de "
                "maquinaria en Chile ('RentMaq Chile'), necesito modelar las entidades TipoFaena y Maquinaria. "
                "¿Cómo debo configurar las relaciones para evitar que el borrado de una categoría borre "
                "accidentalmente las máquinas en cascada, y qué validadores debo colocar a nivel de ORM para "
                "impedir tarifas diarias o fianzas negativas?"
            ),
            'respuesta_ia': (
                "La IA propuso vincular Maquinaria con TipoFaena mediante models.ForeignKey utilizando "
                "on_delete=models.PROTECT, explicando que ante un intento de borrado Django eleva una excepción "
                "ProtectedError impidiendo la eliminación física de la categoría mientras existan equipos vinculados. "
                "Asimismo, recomendó MinValueValidator(0) directamente en los campos cuantitativos para forzar "
                "la restricción a nivel de ORM y base de datos, no solo en formularios HTML."
            ),
            'adaptacion_critica': (
                "Se acogió la recomendación de models.PROTECT. Se decidió además no eliminar registros físicamente "
                "sino implementar un mecanismo de baja lógica mediante activo = models.BooleanField(default=True), "
                "protegiendo la trazabilidad histórica de cotizaciones pasadas. Adicionalmente, se extendió el modelo "
                "User nativo con PerfilUsuario (OneToOneField y señal post_save) para registrar RUT chileno, "
                "teléfono de contacto y razón social de la empresa contratista."
            ),
            'codigo_destacado': (
                "tipo_faena = models.ForeignKey(TipoFaena, on_delete=models.PROTECT, related_name='maquinarias')\n"
                "tarifa_diaria = models.DecimalField(..., validators=[MinValueValidator(0)])\n"
                "activo = models.BooleanField(default=True)  # Baja lógica"
            )
        },
        {
            'numero': 2,
            'titulo': 'Optimización de Consultas ORM (Problema N+1) y Búsqueda Multi-Campo',
            'herramienta': 'Gemini 1.5 Pro / Antigravity',
            'area': 'Rendimiento y Filtros Q',
            'criterio': 'Criterio 2.1.3 (Lectura y Búsqueda)',
            'icono': 'bi-lightning-charge-fill',
            'prompt': (
                "En la vista de catálogo público de Django necesito listar maquinarias mostrando el nombre de su "
                "TipoFaena asociada. ¿Cómo evito que Django realice consultas SQL repetitivas por cada máquina "
                "(problema N+1)? Además, ¿cómo implemento un buscador con un solo campo de texto que busque "
                "simultáneamente por código de serie, nombre del equipo, marca o especificaciones?"
            ),
            'respuesta_ia': (
                "La IA explicó que al acceder a maquinaria.tipo_faena.nombre en el template, Django por defecto "
                "hace 1 consulta para las máquinas y N consultas adicionales para sus categorías. Sugirió emplear "
                "Maquinaria.objects.filter(activo=True).select_related('tipo_faena'), lo cual genera un INNER JOIN "
                "en una única sentencia SQL. Para la búsqueda multi-campo, recomendó el objeto Q de django.db.models "
                "combinando condiciones con el operador pipe (| OR)."
            ),
            'adaptacion_critica': (
                "Se aplicó select_related('tipo_faena') en catalogo_view y panel_gestion_view, eliminando 100% "
                "las consultas redundantes sobre SQLite. El buscador Q se combinó con filtros dinámicos por ID de faena, "
                "ordenamiento configurable (precio asc/desc, nombre A-Z) y paginación con Paginator (6 equipos por página)."
            ),
            'codigo_destacado': (
                "maquinarias = Maquinaria.objects.filter(activo=True).select_related('tipo_faena')\n"
                "if query:\n"
                "    maquinarias = maquinarias.filter(\n"
                "        Q(nombre__icontains=query) | Q(codigo__icontains=query) |\n"
                "        Q(marca__icontains=query) | Q(descripcion__icontains=query)\n"
                "    )"
            )
        },
        {
            'numero': 3,
            'titulo': 'Manejo Seguro de Sesiones HTTP (request.session) y Cálculo de IVA 19%',
            'herramienta': 'ChatGPT (GPT-4o) / Antigravity',
            'area': 'Sesiones HTTP y Lógica Tributaria',
            'criterio': 'Criterio 2.1.4 (Sesiones y Cotizador)',
            'icono': 'bi-cart-check-fill',
            'prompt': (
                "¿Cómo programo un cotizador de arriendo en Django usando request.session para que el cliente "
                "acumule equipos temporalmente, modifique los días de cada uno, y calcule el IVA chileno del 19% "
                "más fianza de garantía? ¿Cómo logro que el contador de ítems se muestre en el Navbar en todas "
                "las páginas sin pasarlo manualmente en cada vista?"
            ),
            'respuesta_ia': (
                "La IA recomendó encapsular la lógica en una clase de servicio CanastaArriendo que guarde un diccionario "
                "en request.session['canasta_arriendo']. Enfatizó que al mutar estructuras anidadas es obligatorio "
                "ejecutar request.session.modified = True para que Django persista los cambios en la cookie. "
                "Para la disponibilidad global en plantillas, indicó crear un Context Processor en context_processors.py "
                "y registrarlo en TEMPLATES['OPTIONS']['context_processors']."
            ),
            'adaptacion_critica': (
                "Se implementó arriendo/cart.py (CanastaArriendo) y arriendo/context_processors.py (canasta_counter). "
                "Se aplicó la legislación tributaria chilena: el IVA del 19% grava estrictamente el Subtotal Neto "
                "del servicio de arriendo, mientras que la fianza de garantía se suma aparte sin IVA por ser un monto "
                "de caución reembolsable. Al confirmar la solicitud, se genera un código formalizado (REQ-XXXXXXXX) "
                "y se vacía la sesión."
            ),
            'codigo_destacado': (
                "subtotal_neto = sum(tarifa * dias for item in canasta)\n"
                "iva_19 = subtotal_neto * Decimal('0.19')\n"
                "total_final = subtotal_neto + iva_19 + total_garantias\n"
                "self.session.modified = True"
            )
        },
        {
            'numero': 4,
            'titulo': 'Control de Acceso por Roles y Protección de Rutas Sensibles',
            'herramienta': 'Antigravity AI Assistant',
            'area': 'Seguridad y Control de Acceso',
            'criterio': 'Criterio 2.1.4 (Seguridad y Roles)',
            'icono': 'bi-shield-shaded',
            'prompt': (
                "¿Cómo restrinjo de forma segura en Django las operaciones CRUD y el panel de flota para que solo "
                "usuarios autenticados con rol de Staff o Superusuario puedan acceder, impidiendo accesos no "
                "autorizados por URL directa de usuarios comunes o anónimos?"
            ),
            'respuesta_ia': (
                "La IA propuso utilizar el decorador @user_passes_test con una función predicado que valide "
                "user.is_authenticated y (user.is_staff or user.is_superuser), complementado con @login_required "
                "y el parámetro login_url='catalogo'. Además recordó verificar la inclusión de {% csrf_token %} "
                "en cada formulario POST para mitigar vulnerabilidades CSRF."
            ),
            'adaptacion_critica': (
                "Se implementó la función es_personal_staff(user) en views.py y se decoraron crear_maquinaria_view, "
                "editar_maquinaria_view, eliminar_maquinaria_view y panel_gestion_view. Cualquier usuario sin "
                "privilegios es redirigido de inmediato al catálogo público con mensaje de advertencia, protegiendo "
                "la integridad del backoffice."
            ),
            'codigo_destacado': (
                "@login_required\n"
                "@user_passes_test(es_personal_staff, login_url='catalogo')\n"
                "def panel_gestion_view(request):\n"
                "    ..."
            )
        }
    ]

    return render(request, 'arriendo/bitacora_ia.html', {'casos_ia': casos_ia})

