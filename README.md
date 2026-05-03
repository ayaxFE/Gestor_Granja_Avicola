# Sistema de Control de Producción Avícola

# ESTRUCTURA

GESTOR_GRANJA_AVICOLA/
│
├── venv/               
├── __pycache__/            
│
├── config/           
│   ├── __init__.py      
│   └── config.py        
│
├── database/              
│   ├── __init__.py             
│   ├── db_local.py            
│   ├── db_cloud.py             
│   ├── sync.py                
│   └── granja_pando_local.db  
│
├── ui/               
│   ├── __init__.py          
│   └── main_window.py   
│
├── README.md             
└── run.py                 


## Descripción del Proyecto
Aplicación de escritorio desarrollada en Python orientada a la gestión operativa y analítica de granjas de pollos parrilleros. El sistema permite la trazabilidad completa del ciclo de producción, optimizando el registro de variables críticas como la mortandad y el consumo de alimento. 

Diseñado con una arquitectura *offline-first*, garantiza la continuidad operativa en zonas rurales con conectividad intermitente, utilizando una base de datos local que posteriormente se sincroniza con un entorno cloud centralizado.

El proyecto fue concebido inicialmente para cubrir los requerimientos de Granja Pando, y actualmente posee una estructura modular (Multi-Tenant) escalable para la integración de múltiples empresas, como ARGEAVE.

## Características Principales

* **Arquitectura Híbrida (Offline-First):** Operación continua sin dependencia de internet mediante SQLite, con motor de sincronización diferida hacia MySQL (Clever Cloud/Hostinger).
* **Gestión de Infraestructura:** Administración jerárquica de Dueños, Granjas y Galpones, con control de estado de ocupación y capacidad.
* **Trazabilidad Sanitaria:** Registro diario de mortandad por lote, con cálculo automatizado de tasas de supervivencia y alertas por superación de umbrales críticos (ej. > 5%).
* **Control de Consumo de Alimento:** Registro de remitos por fase de alimentación (F1 a F5) y cálculo de proyecciones basado en estándares de consumo teórico vs. población activa.
* **Control de Acceso Basado en Roles (RBAC):** Interfaces y permisos diferenciados para perfiles de 'Supervisor' (análisis y gestión) y 'Granjero' (operatividad diaria).

## Stack Tecnológico

* **Lenguaje Core:** Python 3.x
* **Interfaz Gráfica (GUI):** Tkinter
* **Base de Datos Local:** SQLite3
* **Base de Datos Cloud:** MySQL
* **Dependencias Principales:** `mysql-connector-python`

## Estructura del Código

La aplicación sigue una separación lógica de responsabilidades:

* `main.py`: Punto de entrada de la aplicación. Contiene la interfaz gráfica de usuario y la lógica de enrutamiento basada en roles.
* `db_local.py`: Módulo de persistencia local. Maneja la creación de tablas, validación de rutas en el sistema de archivos del usuario y transacciones SQLite.
* `db_cloud.py`: Módulo de conexión remota. Gestiona la autenticación y las transacciones directas contra el servidor MySQL central.
* `sync.py`: Motor de sincronización. Evalúa los registros locales pendientes (flag de sincronización) y los transmite a la nube de forma segura.
* `config.py`: Archivo de configuración central. Contiene credenciales de bases de datos, parámetros de conexión y constantes del negocio (tablas de consumo por fase, umbrales de alerta).

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone [https://github.com/moniVaz0923/SistemaDeControlDeProducci-nAvicola.git](https://github.com/moniVaz0923/SistemaDeControlDeProducci-nAvicola.git)
cd SistemaDeControlDeProducci-nAvicola

