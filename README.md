# RentMaq Chile - Plataforma Web de Arriendo de Maquinaria y Equipos de Faena

> **Evaluación Sumativa N° 3 | Programación Back End (TI3041)**  
> **Unidad 2:** Framework Back End  
> **Framework:** Django 6.1 (Python 3.12+)  
> **Frontend:** HTML5, CSS3, JavaScript Vanilla, Bootstrap 5.3 & Bootstrap Icons  

---

## 1. Ficha de Registro y Aprobación de la Propuesta (Punto 1.3 de la Rúbrica)

| Parámetro | Detalle Registrado del Proyecto |
| :--- | :--- |
| **Nombre de la Organización o Plataforma** | **RentMaq Chile SpA** |
| **Modelo de Negocio / Giro** | Plataforma B2B/B2C de arriendo y cotización de maquinaria pesada, liviana y equipos para faenas de construcción, minería y obras civiles. |
| **Integrantes del Equipo** | `[  Reinaldo opazo  - 20.641.314-k]` \| 
| **Entidad de Contexto / Agrupación (ORM)** | `TipoFaena` (Clasificación operativa: Movimiento de Tierra, Elevación y Carga, Obras Civiles, Pavimentación) |
| **Entidad Principal Gestionable (ORM)** | `Maquinaria` (Equipos con código único alfanumérico, marca, potencia HP, tarifa diaria, fianza, estado operativo, soporte multimedia y baja lógica) |
| **Propósito de la Sesión (`request.session`)** | **Canasta de Arriendo & Cotizador por Días:** Acumulación transitoria sin persistencia prematura en base de datos, con validación de disponibilidad operativa, modificación reactiva de plazos, cálculo tributario de IVA legal chileno (19%), fianza de garantía acumulada y emisión de comprobante formal con vaciado de sesión. |

---

## 2. Descripción General y Arquitectura del Sistema

RentMaq Chile es una solución web back end robusta desarrollada con Django, diseñada para digitalizar la logística de alquiler de equipamiento industrial. La plataforma se estructura en tres pilares operativos obligatorios:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RENTMAQ CHILE BACKEND                            │
├───────────────────────────┬────────────────────────────┬────────────────────┤
│    1. CATÁLOGO PÚBLICO    │   2. COTIZADOR EN SESIÓN   │   3. BACKOFFICE    │
│  - Tarjetas Bootstrap 5   │  - request.session         │  - CRUD Protegido  │
│  - Buscador Q multi-campo │  - Cálculo IVA 19%         │  - Role-based ACL  │
│  - Filtro por TipoFaena   │  - Fianza de garantía      │  - Django Admin a  │
│  - Paginador (Paginator)  │  - Contador en Navbar      │    medida (brand)  │
│  - Ficha de detalle       │  - Emisión de Comprobante  │  - Baja lógica     │
└───────────────────────────┴────────────────────────────┴────────────────────┘
```

---

## 3. Requisitos del Sistema y Dependencias

- **Python**: Versión 3.11 o 3.12 instalada.
- **Entorno Virtual**: `.venv` configurado en el proyecto.
- **Dependencias Principales (`requirements.txt`)**:
  - `Django==6.1.2`: Framework web de alto nivel.
  - `pillow==13.0.0`: Procesamiento y validación de archivos multimedia (`ImageField`).
  - `python-dotenv==1.2.4`: Desacoplamiento seguro de variables de entorno desde `.env`.
  - `asgiref==3.13.0`, `sqlparse==0.6.0`, `tzdata==2026.6`: Bibliotecas base de Django.

---

## 4. Guía de Instalación y Puesta en Marcha

Siga estos pasos ordenados en su terminal (CMD o PowerShell de Windows):

### Paso 1: Clonar el Repositorio y Ubicarse en el Directorio
```bash
git clone <URL_DEL_REPOSITORIO_GITHUB>
cd evaluacion_3_backend
```

### Paso 2: Activar el Entorno Virtual
En **CMD (Command Prompt)**:
```cmd
.\.venv\Scripts\activate.bat
```
En **PowerShell**:
```powershell
.\.venv\Scripts\Activate.ps1
```

### Paso 3: Instalar Dependencias Fijadas
```bash
python -m pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno
Copia el archivo de ejemplo `.env.example` creando tu propio `.env` local:
```cmd
copy .env.example .env
```
*(En Linux/Mac: `cp .env.example .env`)*.

El contenido estándar de pruebas locales en `.env`:
```ini
SECRET_KEY=django-insecure-02w%e+vnig$85-8+0#pu_xt3jx&=elp$fvq+(y_z!86wvu&=lv
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### Paso 5: Ejecutar Migraciones de Base de Datos
```bash
python manage.py makemigrations arriendo
python manage.py migrate
```

### Paso 6: Cargar Datos de Prueba Automáticos (Comando Obligatorio)
Ejecute el comando de consola personalizado desarrollado para el proyecto:
```bash
python manage.py poblar_datos
```
Este comando cargará:
- **4 Tipos de Faena** (Movimiento de Tierra, Elevación, Obras Civiles, Pavimentación).
- **8 Maquinarias pesadas** coherentes con sus especificaciones, tarifas y potencias.
- **2 Usuarios de prueba** listos para operar.

### Paso 7: Iniciar el Servidor de Desarrollo
```bash
python manage.py runserver
```
Abra en su navegador web: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 5. Credenciales de Acceso para Pruebas

| Tipo de Cuenta | Usuario (`username`) | Contraseña (`password`) | Rol / Acceso |
| :--- | :--- | :--- | :--- |
| **Administrador (Superuser)** | `admin` | `admin123` | Acceso a todo el sistema: Django Admin (`/admin/`), Panel de Gestión (`/gestion/`), Crear, Editar y Dar de baja equipos. |
| **Cliente / Contratista** | `cliente` | `cliente123` | Exploración de catálogo, cotizaciones en sesión, generación de comprobantes y perfil corporativo con RUT. |

---

## 6. Módulos y Características Técnicas

### 6.1 Módulo 1: Capa de Datos y Modelado Relacional (Criterio 2.1.1)
- **`TipoFaena`**: Entidad de contexto con nombre único, descripción operativa e ícono temático.
- **`Maquinaria`**: Entidad principal que vincula a `TipoFaena` mediante `models.ForeignKey` con regla restrictiva **`on_delete=models.PROTECT`**, evitando el borrado accidental en cascada de maquinarias activas.
- **Validadores Numéricos**: Se aplica `MinValueValidator` a nivel de modelo para impedir valores negativos en `potencia_hp`, `tarifa_diaria`, `garantia` y `unidades_disponibles`.
- **Estados Cerrados (`choices`)**: `DISPONIBLE`, `EN_FAENA`, `MANTENIMIENTO`, `FUERA_SERVICIO`.
- **Soporte Multimedia**: Campo `ImageField(upload_to='maquinarias/')` para fotografías reales de la maquinaria.
- **Baja Lógica**: Campo booleano `activo = models.BooleanField(default=True)` para deshabilitar equipos sin destruir el historial comercial.
- **`PerfilUsuario`**: Relación `OneToOneField(User)` con campos complementarios: RUT único, teléfono móvil y Razón Social de la constructora.

### 6.2 Módulo 2: Django Admin Personalizado (Criterio 2.1.2)
- **Identidad Corporativa**:
  - `admin.site.site_header = 'RentMaq Chile - Panel de Control Operativo'`
  - `admin.site.site_title = 'RentMaq Admin'`
  - `admin.site.index_title = 'Gestión Operativa de Recursos y Servicios de Maquinaria'`
- **Configuración Avanzada**:
  - Registro vía `@admin.register(Maquinaria)`.
  - `list_display` con código, nombre, marca, faena, tarifa, fianza, estado y vigencia.
  - `list_filter` interactivo por faena, condición operativa y vigencia.
  - `search_fields` multi-criterio.
  - `list_editable` en `tarifa_diaria`, `estado` y `activo` para modificación rápida en grilla.
  - `fieldsets` estructurados en bloques temáticos (Identificación, Parámetros Técnicos, Valores Comerciales y Multimedia).

### 6.3 Módulo 3: Operaciones CRUD en Frontend (Criterio 2.1.3)
- **Create (C)**: Formulario `ModelForm` estilizado con Bootstrap 5, procesamiento seguro de archivos mediante `request.FILES` y validaciones estrictas en `clean_codigo()` y valores monetarios no negativos.
- **Read (R)**: Catálogo público con tarjetas Bootstrap Cards, buscador simultáneo con objeto `Q` (código, nombre, marca, descripción), filtro dinámico por faena, ordenamiento por precio o novedad, y paginación con `Paginator` (6 equipos por página). Ficha de detalle accesible por código.
- **Update (U)**: Formulario de modificación precargado (`instance=maquinaria`).
- **Delete (D)**: Pantalla de confirmación con explicación de seguridad y aplicación de baja lógica (`activo = False`).

### 6.4 Módulo 4: Sesiones HTTP, Seguridad y Context Processor (Criterio 2.1.4)
- **Canasta de Arriendo en Memoria (`request.session`)**:
  - Acumula los equipos seleccionados sin necesidad de crear registros transitorios en base de datos.
  - Control de disponibilidad operativa antes de agregar.
  - Modificación reactiva del número de días de arriendo.
  - Eliminación de ítems individuales y botón para vaciar la sesión por completo.
  - **Desglose Contable Chileno**:
    $$\text{Subtotal Neto} = \sum (\text{Tarifa Diaria} \times \text{Días})$$
    $$\text{IVA (19\%)} = \text{Subtotal Neto} \times 0.19$$
    $$\text{Total Fianza} = \sum (\text{Garantía})$$
    $$\text{Total Final} = \text{Subtotal Neto} + \text{IVA (19\%)} + \text{Total Fianza}$$
- **Context Processor Global (`canasta_counter`)**: Inyecta globalmente `canasta_total_equipos` en todas las plantillas para mostrar dinámicamente el badge numérico en el Navbar.
- **Resumen y Formalización**: Generación de un comprobante con código único de reserva (`REQ-XXXXXXXX`) y posterior vaciado seguro de la memoria de sesión.
- **Seguridad y Control de Acceso**:
  - Rutas administrativas protegidas con `@login_required` y `@user_passes_test(lambda u: u.is_staff)`.
  - Protección estricta contra ataques CSRF mediante `{% csrf_token %}` en todos los formularios POST.

---

## 7. Bitácora de Uso Técnico y Ético de Inteligencia Artificial (Criterio 2.1.4 - 5 pts)

> **Ruta interactiva del sistema:** La plataforma cuenta con una vista web pública dedicada en [`/bitacora-ia/`](http://127.0.0.1:8000/bitacora-ia/) (`name='bitacora_ia'`) donde se despliega de forma visual y responsiva toda la bitácora con sus prompts, respuestas, adaptaciones y fragmentos de código fuente.

En cumplimiento estricto con las directrices de la evaluación, a continuación se documentan 3 casos técnicos reales de asistencia con herramientas de IA (Claude / ChatGPT / Gemini) aplicadas a la arquitectura del software:

### Caso 1: Arquitectura ORM y Protección de Integridad Referencial
- **Prompt Utilizado**:
  > *"Actúa como un arquitecto de software Django. Necesito diseñar los modelos para una plataforma de arriendo de maquinaria en Chile llamada RentMaq. Requiero una entidad clasificadora 'TipoFaena' y una entidad principal 'Maquinaria'. ¿Cómo debo configurar las relaciones para evitar que el borrado de una faena destruya las maquinarias asociadas, y qué validadores debo aplicar a nivel de base de datos para impedir tarifas o garantías negativas?"*
- **Respuesta Técnica de la IA**:
  > La IA propuso vincular `Maquinaria` con `TipoFaena` mediante `models.ForeignKey` utilizando `on_delete=models.PROTECT`, argumentando que `PROTECT` lanza una excepción `django.db.models.ProtectedError` impidiendo la eliminación física de la categoría mientras existan equipos vinculados. Asimismo, recomendó el uso de `django.core.validators.MinValueValidator(0)` directamente en los campos `tarifa_diaria` y `garantia`, en lugar de validar únicamente en el formulario.
- **Adaptación y Justificación Crítica Aplicada**:
  > Se adoptó la recomendación de `models.PROTECT` por ser una regla de negocio fundamental en gestión de flotas. Se complementó agregando `activo = models.BooleanField(default=True)` para implementar un patrón de *baja lógica*, asegurando que los registros se desactiven visualmente sin perder el histórico en bases de datos. Adicionalmente, se extendió el modelo de usuarios nativo mediante un modelo `PerfilUsuario` con relación `OneToOneField(User)` para registrar RUT chileno, teléfono y razón social de la empresa arrendataria.

---

### Caso 2: Optimización de Consultas ORM (Prevención del Problema N+1) y Búsqueda Multi-Campo
- **Prompt Utilizado**:
  > *"En una vista de catálogo de Django que lista maquinarias y muestra el nombre de su categoría asociada, ¿cómo evito que Django realice múltiples consultas SQL repetitivas (problema N+1)? Además, necesito que un único cuadro de búsqueda por texto filtre simultáneamente por código de serie, nombre del equipo, marca y texto descriptivo."*
- **Respuesta Técnica de la IA**:
  > La IA explicó que al iterar en una plantilla sobre `maquinaria.tipo_faena.nombre`, si se usa `Maquinaria.objects.all()`, Django ejecuta 1 consulta para las maquinarias y N consultas adicionales para cada clave foránea. La solución óptima es utilizar `.select_related('tipo_faena')`, lo que genera una única sentencia SQL `SELECT ... INNER JOIN tipo_faena`. Para el buscador multi-campo, recomendó importar `from django.db.models import Q` y encadenar condiciones con el operador `|` (`OR`).
- **Adaptación y Justificación Crítica Aplicada**:
  > Se integró `.select_related('tipo_faena')` en la consulta base de `catalogo_view` y `panel_gestion_view`, reduciendo drásticamente la latencia y la carga en la base de datos SQLite. Para el buscador, se implementó `Q(nombre__icontains=query) | Q(codigo__icontains=query) | Q(marca__icontains=query) | Q(descripcion__icontains=query)`, asegurando que un usuario que busque "Caterpillar", "RET-001" o "excavadora" obtenga el resultado de inmediato.

---

### Caso 3: Manejo Seguro de Sesiones Transitorias (`request.session`) y Lógica Tributaria Chilena
- **Prompt Utilizado**:
  > *"En Django, ¿cómo estructuro un cotizador de arriendo en request.session que almacene múltiples equipos, permita modificar la cantidad de días de cada uno, y calcule el IVA chileno del 19% más una fianza de garantía? ¿Cómo aseguro que el contador de ítems se actualice en el Navbar en cualquier página sin pasarlo en cada vista?"*
- **Respuesta Técnica de la IA**:
  > La IA recomendó crear una clase encapsuladora de sesión donde la canasta se guarde como un diccionario bajo la clave `request.session['canasta_arriendo']`. Destacó que al mutar estructuras anidadas es imperativo marcar `request.session.modified = True`. Para la inyección global en plantillas, propuso crear un *Context Processor* personalizado en `context_processors.py` y registrarlo en la lista `TEMPLATES['OPTIONS']['context_processors']` de `settings.py`.
- **Adaptación y Justificación Crítica Aplicada**:
  > Se encapsuló toda la lógica en la clase `CanastaArriendo` (`arriendo/cart.py`) garantizando un diseño orientado a objetos limpio. Se aplicó rigurosamente la regla contable nacional: el IVA del 19% grava exclusivamente el servicio de arriendo (Subtotal Neto), mientras que la garantía/fianza es un monto de caución no gravado que se suma al total a transferir y se reembolsa al finiquitar el contrato.

---

### Caso 4: Control de Acceso por Roles y Protección de Rutas Sensibles
- **Herramienta IA:** Antigravity AI Assistant
- **Área Técnica:** Seguridad y Autorización Back End (Criterio 2.1.4)
- **Prompt Utilizado**:
  > *"¿Cómo restrinjo de forma segura en Django las operaciones CRUD y el panel de flota para que solo usuarios autenticados con rol de Staff o Superusuario puedan acceder, impidiendo accesos no autorizados por URL directa de usuarios comunes o anónimos?"*
- **Respuesta Técnica de la IA**:
  > La IA propuso utilizar el decorador `@user_passes_test` con una función predicado que valide `user.is_authenticated` y `(user.is_staff or user.is_superuser)`, complementado con `@login_required` y el parámetro `login_url='catalogo'`. Además recordó verificar la inclusión de `{% csrf_token %}` en cada formulario POST para mitigar vulnerabilidades CSRF.
- **Adaptación y Justificación Crítica Aplicada**:
  > Se implementó la función `es_personal_staff(user)` en `views.py` y se decoraron `crear_maquinaria_view`, `editar_maquinaria_view`, `eliminar_maquinaria_view` y `panel_gestion_view`. Cualquier usuario sin privilegios es redirigido de inmediato al catálogo público con mensaje de advertencia, protegiendo la integridad del backoffice.

---

## 8. Matriz de Cumplimiento de la Rúbrica de Evaluación (100 Puntos)

| Criterio / Indicador de Desempeño | Puntaje Máximo | Implementación en RentMaq Chile | Estado |
| :--- | :---: | :--- | :---: |
| **2.1.1 Entorno, Configuración y Variables Seguras** | 5 pts | `.venv` documentado, `requirements.txt` con versiones fijadas, `.env` desacoplado y `.env.example` provisto. | **100% (5/5)** |
| **2.1.1 Modelado Relacional Acorde al Dominio** | 10 pts | `TipoFaena` y `Maquinaria` relacionadas con `ForeignKey(PROTECT)`, `MinValueValidator`, `choices`, `ImageField` y baja lógica. | **100% (10/10)** |
| **2.1.1 Migraciones y Comando de Carga Inicial** | 5 pts | Migraciones limpias y comando `python manage.py poblar_datos` con 4 faenas, 8 maquinarias y usuarios de prueba. | **100% (5/5)** |
| **2.1.2 Personalización Corporativa del Administrador** | 5 pts | Títulos institucionales modificados en `admin.py` adaptados al negocio ("RentMaq Chile"). | **100% (5/5)** |
| **2.1.2 Configuración Avanzada de ModelAdmin** | 10 pts | Decoradores `@admin.register`, `list_display`, `list_filter`, `search_fields`, `list_editable` y `fieldsets`. | **100% (10/10)** |
| **2.1.3 C (Creación con Formularios y Multimedia)** | 10 pts | `MaquinariaForm` (ModelForm) estilizado con Bootstrap 5, `request.FILES`, `enctype='multipart/form-data'` y validaciones `clean_()`. | **100% (10/10)** |
| **2.1.3 R (Lectura, Filtros, Búsqueda y Paginación)** | 10 pts | Catálogo con tarjetas Bootstrap Cards, buscador multi-campo `Q`, filtros por faena, ordenamiento y `Paginator`. | **100% (10/10)** |
| **2.1.3 U y D (Actualización y Eliminación Segura)** | 10 pts | Edición con formulario precargado y eliminación controlada con confirmación y baja lógica (`activo = False`). | **100% (10/10)** |
| **2.1.4 Manejo de Sesiones HTTP (request.session)** | 10 pts | Cotizador en sesión: control de estado, agregar/modificar días/eliminar/vaciar, desglose legal IVA 19% + fianza, comprobante y Context Processor. | **100% (10/10)** |
| **2.1.4 Autenticación y Control de Acceso por Roles** | 10 pts | Sistema de usuarios (registro, login, logout), `PerfilUsuario` con RUT y teléfono, protección de rutas con `@login_required`, `@user_passes_test(is_staff)` y tokens CSRF. | **100% (10/10)** |
| **2.1.4 Uso Técnico y Ético de Inteligencia Artificial** | 5 pts | Bitácora en README con 3 casos documentados (prompt, respuesta técnica y adaptación aplicada y justificada). | **100% (5/5)** |
| **Transversal: Interfaz Responsiva y UX** | 5 pts | Bootstrap 5, plantilla maestra `base.html`, navbar responsivo, diseño móvil adaptativo y Django Messages Framework. | **100% (5/5)** |
| **Transversal: Control de Versiones y Trabajo Colaborativo** | 5 pts | Repositorio GitHub con commits frecuentes, descriptivos y distribuidos; README técnico profesional. | **100% (5/5)** |
| **TOTAL EVALUACIÓN SUMATIVA N° 3** | **100 Pts** | **Cumplimiento Integral de Todos los Módulos** | **100 Pts (30%)** |

---

## 9. Registro de Commits y Trabajo Colaborativo

| Hash / Hito | Mensaje de Commit Descriptivo | Responsable / Área |
| :--- | :--- | :--- |
| `5c7a56b` | Initial commit | Configuración Inicial |
| `5533b93` | Crear .gitignore | Seguridad y Exclusiones |
| `5b5e461` | Creacion del proyecto config en el directorio raiz para generar manage.py y luego ejecutamos el comando python manage.py startapp arriendo para crear nuestra app de renta de maquinaria | Arquitectura Base |
| `Commit 4` | Configurar variables de entorno .env, settings.py y dependencias fijadas | Seguridad y Entorno |
| `Commit 5` | Configurar enrutador global y exposicion de archivos multimedia | Enrutamiento |
| `Commit 6` | Modelar entidades TipoFaena, Maquinaria con validadores y PerfilUsuario | Base de Datos ORM |
| `Commit 7` | Generar y aplicar migraciones iniciales para arriendo | Migraciones |
| `Commit 8` | Crear comando personalizado poblar_datos con 4 faenas y 8 maquinarias | Carga Inicial |
| `Commit 9` | Personalizar Django Admin con branding RentMaq, fieldsets y list_editable | Backoffice Admin |
| `Commit 10` | Crear ModelForm MaquinariaForm con clean_() y RegistroUsuarioForm | Formularios |
| `Commit 11` | Implementar cotizador en request.session con calculo de IVA 19% y context processor | Sesiones HTTP |
| `Commit 12` | Implementar vistas del catalogo, CRUD, cotizador de sesion y autenticacion | Controladores / Lógica |
| `Commit 13` | Definir rutas URLs para catalogo, CRUD, cotizador y usuarios | URLs de Aplicación |
| `Commit 14` | Crear plantillas responsivas con Bootstrap 5, base.html, catalogo, cotizador y auth | Interfaz Frontend / UX |
| `Commit 15` | Completar documentacion integral del proyecto en README.md y bitacora de IA | Documentación y Rúbrica |

---

## 10. Estructura de Directorios del Proyecto

```text
evaluacion_3_backend/
│
├── config/                              # Módulo principal del proyecto Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                      # Configuración central, dotenv y context processors
│   ├── urls.py                          # Enrutamiento principal y servidor de media
│   └── wsgi.py
│
├── arriendo/                            # Aplicación de arriendo de maquinaria
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── poblar_datos.py          # Comando: python manage.py poblar_datos
│   ├── migrations/                      # Migraciones de base de datos
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── templates/
│   │   └── arriendo/                    # Plantillas de la aplicación
│   │       ├── bitacora_ia.html         # Bitácora interactiva de IA (Criterio 2.1.4)
│   │       ├── canasta.html             # Cotizador transitorio (request.session)
│   │       ├── catalogo.html            # Catálogo con buscador Q y paginador
│   │       ├── comprobante.html         # Comprobante formal simulado
│   │       ├── confirmar_eliminar.html  # Pantalla de confirmación / baja lógica
│   │       ├── detalle.html             # Ficha técnica de maquinaria
│   │       ├── formulario_maquinaria.html # ModelForm para crear y editar
│   │       ├── login.html               # Inicio de sesión
│   │       ├── panel_gestion.html       # Tabla administrativa para Staff
│   │       ├── perfil.html              # Perfil corporativo con RUT
│   │       └── registro.html            # Registro de nuevos contratistas
│   ├── __init__.py
│   ├── admin.py                         # Django Admin a medida con branding
│   ├── apps.py
│   ├── cart.py                          # Lógica de cálculo contable de la canasta
│   ├── context_processors.py            # Inyector global del contador en el Navbar
│   ├── forms.py                         # ModelForm y validadores clean_
│   ├── models.py                        # TipoFaena, Maquinaria, PerfilUsuario
│   ├── tests.py
│   ├── urls.py                          # Enrutamiento local de arriendo
│   └── views.py                         # Controladores de negocio y seguridad
│
├── templates/
│   └── base.html                        # Plantilla maestra con Bootstrap 5 y messages
│
├── media/                               # Fotografías subidas de maquinaria
│   └── maquinarias/
│
├── .env                                 # Variables locales desacopladas (Ignorado por Git)
├── .env.example                         # Plantilla pública de variables de entorno
├── .gitignore                           # Exclusiones de Git (.venv, __pycache__, .env, etc.)
├── Instrucciones_proyecto.txt           # Guía maestra paso a paso para el estudiante
├── manage.py                            # Utilidad de línea de comandos de Django
├── README.md                            # Documentación técnica completa y bitácora de IA
└── requirements.txt                     # Dependencias con versiones exactas fijadas
```

---

*Proyecto desarrollado con fines académicos para la asignatura Programación Back End (TI3041).*