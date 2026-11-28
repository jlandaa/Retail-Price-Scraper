# 🛒 Retail Price Scraper: Automated ETL & BI Pipeline

[![ETL Frávega](https://github.com/jlandaa/Retail-Price-Scraper/actions/workflows/etl_fravega.yml/badge.svg?branch=main)](https://github.com/jlandaa/Retail-Price-Scraper/actions/workflows/etl_fravega.yml)
[![CI Quality](https://github.com/jlandaa/Retail-Price-Scraper/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/jlandaa/Retail-Price-Scraper/actions/workflows/ci.yml)

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)](https://www.databricks.com/)
[![Apache Spark](https://img.shields.io/badge/PySpark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Ruff](https://img.shields.io/badge/Ruff-261230?style=for-the-badge&logo=ruff&logoColor=D7FF64)](https://docs.astral.sh/ruff/)

## 📌 Visión General del Proyecto

Este proyecto es una solución integral de Business Intelligence y Data Engineering diseñada para monitorear la competitividad periódica en el sector retail. A través de un pipeline 100% automatizado, se extraen precios, stock, financiación y descuentos del e-commerce de **Frávega** en múltiples categorías estratégicas (tecnología, electrodomésticos, hogar, entretenimiento y bebés). Los datos atraviesan controles de calidad, se procesan mediante computación distribuida y se disponibilizan en un modelo semántico para análisis estratégico.

🔗 **[Ver Dashboard Interactivo (Publicado en Power BI)](https://app.powerbi.com/view?r=eyJrIjoiYzFhNWJmMzQtNTllYS00ODNkLTlkOTYtMDQyNmMzNzRiYjQ4IiwidCI6IjZjYmMyOTllLWIxZDUtNDJjZi1hMWRjLTgwNjZmMTdiN2QwNyIsImMiOjR9)**

## 💼 Impacto de Negocio

En la industria del retail, la agilidad para ajustar precios frente a la competencia define la cuota de mercado. Esta arquitectura permite a los equipos de Pricing y Comercial:

- **Analizar la agresividad de descuentos** por categoría de producto (Audio, Climatización, Smartphones, etc.).
- **Monitorear el posicionamiento de marcas** (ej. Samsung, Motorola, LG) frente a rebajas de competidores.
- **Detectar oportunidades de margen** mediante el análisis de dispersión entre el precio regular y el precio de oferta.

## 🏗️ Arquitectura de Datos (End-to-End)

El flujo de datos sigue las mejores prácticas de automatización, calidad de datos, orquestación por APIs y escalabilidad en la nube:

1. **Orquestación (CI/CD):** **GitHub Actions** separa la operación en dos workflows independientes: un pipeline **ETL bi-semanal** (`etl_fravega.yml`) mediante *Cron Jobs*, eliminando la intervención manual y coordinando todo el ecosistema, y un flujo de **CI de calidad** (`ci.yml`) que ejecuta `Ruff` y `Pytest` en cada `push` o Pull Request.
2. **Ingesta Resiliente y Data Quality Gate (Web Scraping):** Scraper modular en Python con `requests.Session()`, `ScraperAPI` sobre HTTPS, manejo de excepciones, reintentos automáticos (*retries*), rotación de proxies, *logging* estructurado y zona horaria explícita de Argentina (`America/Argentina/Buenos_Aires`). Antes de exportar el CSV, un **Data Quality Gate** valida volumen mínimo, cobertura de categorías e integridad de precios; los archivos crudos aprobados se suben directamente al Volumen de Databricks mediante su Files API REST.
3. **Procesamiento Distribuido (ETL):** GitHub Actions invoca la API de Jobs de **Databricks** con reintentos inteligentes y monitorea activamente el ciclo de vida de la ejecución (*polling* del `run_id`) hasta confirmar su finalización exitosa, aplicando degradación controlada ante límites transitorios de la API. PySpark gestiona la limpieza de strings, casteo estricto de tipos de datos y aplicación de lógica de negocio.
4. **Almacenamiento (Delta Lake):** Modelado dimensional optimizado bajo un **Esquema Estrella**, generando Claves Subrogadas (*Surrogate Keys*) numéricas (`id_producto`) para máxima performance.
5. **Capa Semántica y Actualización Automática (BI):** Una vez completado el Job en Databricks, el pipeline se autentica mediante **Azure AD (Service Principal)** e invoca la API REST de **Power BI Service** para refrescar el modelo semántico en modo *Import*, garantizando alta disponibilidad 24/7 y consultas instantáneas sin depender del cómputo activo del clúster.

## ⚙️ Características Técnicas Destacadas

- **CI de Calidad y Pruebas Unitarias:** Workflow dedicado con **Ruff** (linting y formateo) y **Pytest** (13 tests unitarios en memoria) que validan parseo de precios argentinos, desambiguación de marcas por regex (`LG`, `BLACK+DECKER`, `GA.MA`), generación determinística de SKUs (MD5), *Data Quality Gate* y retención sin depender de red ni gastar créditos de API.
- **Integración CI/CD y Orquestación por APIs:** Flujo 100% automatizado conectando GitHub Actions, Databricks y Power BI en un solo circuito continuo con degradación controlada.
- **Performance Optimizada:** Implementación de un modelo de datos en estrella (*Star Schema*) en Databricks, reemplazando cadenas de texto largas por identificadores numéricos únicos (`id_producto`) para cruzar hechos y dimensiones con máxima velocidad.
- **Código Limpio y Modular:** Lógica de extracción organizada por categorías estratégicas y diccionarios de marcas, con separación estricta entre funciones puras de parseo/validación y la capa de orquestación HTTP para facilitar el mantenimiento y el testing.
- **Manejo de Historial:** Política de retención de datos con rutinas automáticas de limpieza para archivos en crudo mayores a 30 días, sumado a la partición de tablas temporales en Delta Lake para análisis evolutivo.
- **Data Storytelling:** Diseño de dashboard en Power BI optimizado para lectura rápida de KPIs, análisis de dispersión de precios y detección de outliers.

## 📂 Estructura del Repositorio

```text
📦 Retail-Price-Scraper
 ┣ 📂 .github/workflows/       # Orquestación CI/CD (GitHub Actions)
 ┃ ┣ 📜 ci.yml                 # CI de calidad (Ruff + Pytest) en cada push/PR
 ┃ ┗ 📜 etl_fravega.yml        # Pipeline automatizado End-to-End
 ┣ 📂 data/                    # Almacenamiento histórico local (ventana móvil de 30 días)
 ┣ 📂 scraper/                 # Módulo de ingesta en Python
 ┃ ┗ 📜 Fravega_Completo.py    # Scraper modular con Data Quality Gate
 ┣ 📂 tests/                   # Pruebas unitarias en memoria
 ┃ ┗ 📜 test_scraper.py        # Suite de tests (parseo, marcas, calidad y retención)
 ┣ 📂 notebooks/               # Procesamiento distribuido
 ┃ ┗ 📜 Scraping_Retail.ipynb  # Transformaciones ETL en PySpark / SQL
 ┣ 📂 dashboard/               # Capa de visualización
 ┃ ┗ 📜 Scraping_retail.pbix   # Modelo semántico y reporte en Power BI
 ┣ 📜 pyproject.toml           # Configuración de Ruff y Pytest
 ┣ 📜 requirements.txt         # Dependencias del entorno de ingesta
 ┣ 📜 .gitignore               # Exclusión de cachés y entornos locales
 ┣ 📜 LICENSE                  # Licencia MIT
 ┗ 📜 README.md                # Documentación técnica
```

## 🚀 Despliegue y Ejecución

### Opción A: Pipeline Automatizado (Producción)

El proyecto está desplegado en producción. El flujo de trabajo `.github/workflows/etl_fravega.yml` se ejecuta automáticamente mediante un *cron schedule* bi-semanal, mientras que `.github/workflows/ci.yml` audita la calidad del código en cada cambio sobre `main`. Los logs de ingesta y orquestación pueden auditarse directamente en la pestaña `Actions` del repositorio.

### Opción B: Ejecución Local y Pruebas (Desarrollo)

Para replicar el entorno y validar la suite de calidad en local:

1. **Clonar el repositorio:**

```bash
git clone [https://github.com/jlandaa/Retail-Price-Scraper.git](https://github.com/jlandaa/Retail-Price-Scraper.git)
cd Retail-Price-Scraper
```

2. **Instalar dependencias de Python y herramientas de calidad:**

```bash
pip install -r requirements.txt
pip install ruff pytest
```

3. **Ejecutar linting, formateo y pruebas unitarias (sin necesidad de API Key):**

```bash
ruff check .
ruff format --check .
pytest -v
```

4. **Ejecutar el scraper (requiere configurar `SCRAPER_API_KEY` en variables de entorno):**

```bash
export SCRAPER_API_KEY="tu_api_key"
python scraper/Fravega_Completo.py
```

5. **Procesar en la nube:**
   - Importar `notebooks/Scraping_Retail.ipynb` a un Workspace de Databricks.
   - Adjuntar a un clúster activo y ejecutar las celdas de transformación.

---

👨‍💻 **Juan Manuel Landa** — *Computer Engineer | Data Analyst & BI Consultant*  
🔗 [LinkedIn](https://ar.linkedin.com/in/juan-manuel-landa/en) • 🌐 [Portfolio](https://juan-manuel-landa.netlify.app/) • ✉️ [Contacto](mailto:jmlanda93@gmail.com)
