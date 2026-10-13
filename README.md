# AnalytiX

### Inteligencia artificial aplicada al análisis de datos.

**AnalytiX** es un asistente de Business Intelligence (BI) impulsado por inteligencia artificial, diseñado para convertir preguntas en lenguaje natural en consultas SQL y facilitar el acceso a la información almacenada en bases de datos.

Utiliza modelos de lenguaje locales mediante Ollama y Qwen para interpretar preguntas, generar consultas SQL, recuperar información y presentar resultados de forma clara, rápida y comprensible.

El objetivo es acercar el análisis de datos a cualquier usuario, reduciendo la necesidad de conocimientos avanzados en SQL.

---

## Vista previa

![Interfaz de AnalytiX](https://github.com/user-attachments/assets/59756aaf-3cc4-46f6-b4c3-6b54b593481f)

---

## Características principales

* **Consultas en lenguaje natural:** transforma preguntas del usuario en consultas SQL.
* **Inteligencia artificial local:** integración con Qwen mediante Ollama.
* **Administración de conexiones:** permite registrar y gestionar conexiones a bases de datos PostgreSQL.
* **Exploración del esquema:** identifica tablas, columnas y tipos de datos de las bases de datos conectadas.
* **Generación de SQL:** construye consultas adaptadas a la estructura de la base de datos.
* **Validación de consultas:** incorpora controles para restringir la ejecución a consultas de lectura.
* **Procesamiento de resultados:** organiza los datos obtenidos para facilitar su interpretación.
* **Respuestas optimizadas:** ajusta las instrucciones y los parámetros del modelo para reducir tiempos de generación.
* **Interfaz web:** permite interactuar con el agente desde una interfaz centralizada.

## ¿Cómo funciona?

AnalytiX integra la pregunta del usuario, el esquema de la base de datos y un modelo de inteligencia artificial en un flujo de procesamiento.

1. **Conexión:** el usuario configura una conexión a la base de datos.
2. **Exploración:** el sistema obtiene la estructura de tablas y columnas disponibles.
3. **Interpretación:** el agente analiza la pregunta y genera una consulta SQL.
4. **Validación:** la consulta pasa por controles de seguridad antes de su ejecución.
5. **Ejecución:** el sistema consulta la base de datos y obtiene los resultados.
6. **Respuesta:** los datos se organizan y se presentan al usuario de forma clara.

## Arquitectura tecnológica

| Componente              | Tecnología              |
| ----------------------- | ----------------------- |
| Backend                 | Python · Django         |
| API                     | Django REST Framework   |
| Inteligencia artificial | Qwen · Ollama           |
| Base de datos de origen | PostgreSQL              |
| Acceso a datos          | Psycopg                 |
| Frontend                | HTML · CSS · JavaScript |

## Estructura del proyecto

El proyecto está organizado en aplicaciones y servicios independientes para facilitar su mantenimiento y evolución.

```text
AnalytiX/
├── analytix/
│   ├── ai_agent/
│   │   └── services/
│   │       ├── bi_agent.py
│   │       ├── db_service.py
│   │       └── llm_service.py
│   └── modeler/
├── templates/
├── static/
├── manage.py
└── README.md
```

*La estructura es ilustrativa y puede ajustarse a la organización actual del repositorio.*

### Aplicación `ai_agent`

Gestiona el flujo de interacción con la inteligencia artificial, la generación de consultas SQL, su ejecución y el procesamiento de los resultados.

### Aplicación `modeler`

Centraliza la administración de conexiones a bases de datos y la exploración de sus esquemas, incluyendo tablas y columnas.

## Requisitos

Antes de ejecutar el proyecto, necesitas:

* Python instalado.
* PostgreSQL accesible desde el entorno de ejecución.
* Ollama instalado y en funcionamiento.
* Un modelo Qwen descargado en Ollama.
* Las dependencias de Python del proyecto.

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Analytix
```

### 2. Crear un entorno virtual

En Windows:

```bash
python -m venv env
env\Scripts\activate
```

### 3. Instalar las dependencias

Si el proyecto cuenta con un archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Instalar y ejecutar Ollama

Descarga Ollama desde [ollama.com](https://ollama.com/).

Descarga el modelo Qwen utilizado por el proyecto. Por ejemplo, si trabajas con la variante de 8 mil millones de parámetros:

```bash
ollama pull qwen3:8b
```

Comprueba que el modelo esté disponible:

```bash
ollama list
```

### 5. Ejecutar Django

```bash
python manage.py migrate
python manage.py runserver
```

Abre la dirección local que muestra Django en la terminal para acceder a la aplicación.

> **Nota:** los nombres del modelo, las variables de entorno y la configuración de la conexión deben coincidir con los definidos en tu proyecto. No publiques credenciales ni contraseñas en el repositorio.

## Seguridad

AnalytiX está diseñado para priorizar las consultas de lectura y reducir el riesgo de operaciones no autorizadas.

Las medidas recomendadas incluyen:

* Validar las consultas SQL antes de ejecutarlas.
* Restringir las operaciones permitidas a consultas de solo lectura.
* Utilizar credenciales con permisos mínimos en las bases de datos.
* Proteger las credenciales de conexión mediante variables de entorno o un sistema seguro de configuración.
* Evitar que los datos obtenidos de la base de datos se interpreten como instrucciones para el modelo.
* Limitar el acceso a información sensible según los permisos del usuario.

La generación de SQL mediante inteligencia artificial no garantiza por sí sola que una consulta sea segura. La validación debe realizarse independientemente del modelo.

## Objetivos del proyecto

AnalytiX busca evolucionar hacia una plataforma de análisis de datos asistida por inteligencia artificial, capaz de facilitar la exploración de información empresarial sin exigir que el usuario escriba SQL manualmente.

### Próximas mejoras

* Ampliar el soporte para otros motores de bases de datos.
* Mejorar la visualización de resultados mediante tablas dinámicas e indicadores.
* Incorporar análisis de tendencias y métricas de negocio.
* Optimizar la latencia de los agentes y el procesamiento de consultas.
* Fortalecer los mecanismos de validación y control de acceso.
* Incorporar herramientas de visualización de datos.

## Filosofía

La inteligencia artificial debe simplificar el acceso al conocimiento, potenciar las capacidades humanas y convertir los datos en información útil para tomar mejores decisiones.

**AnalytiX — Tus datos, tus preguntas, nuevas perspectivas.**

---

Desarrollado con Python, Django, PostgreSQL y modelos de inteligencia artificial locales.

