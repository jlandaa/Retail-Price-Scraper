# 🛒 Retail Price Scraper: Automated ETL & BI Pipeline

[![ETL Frávega](https://github.com/jlandaa/Retail-Price-Scraper/actions/workflows/etl_fravega.yml/badge.svg)](https://github.com/jlandaa/Retail-Price-Scraper/actions)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)](https://www.databricks.com/)
[![Apache Spark](https://img.shields.io/badge/PySpark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](https://powerbi.microsoft.com/)

## 📌 Visión General del Proyecto
Este proyecto es una solución integral de Business Intelligence y Data Engineering diseñada para monitorear la competitividad diaria en el sector retail. A través de un pipeline 100% automatizado, se extraen precios, stock y descuentos del e-commerce de **Frávega** (categorías de tecnología y electrodomésticos). Los datos se procesan mediante computación distribuida y se disponibilizan en un modelo semántico para análisis estratégico.

🔗 **[Ver Dashboard Interactivo (Publicado en Power BI)](https://app.powerbi.com/view?r=eyJrIjoiNjljMGY0NDUtYjBjMC00ODkxLWFjYWYtNzU3ZDkxN2QwOWE3IiwidCI6IjZjYmMyOTllLWIxZDUtNDJjZi1hMWRjLTgwNjZmMTdiN2QwNyIsImMiOjR9)**


## 💼 Impacto de Negocio
En la industria del retail, la agilidad para ajustar precios frente a la competencia define la cuota de mercado. Esta arquitectura permite a los equipos de Pricing y Comercial:
- **Analizar la agresividad de descuentos** por categoría de producto (Audio, Climatización, Smartphones, etc.).
- **Monitorear el posicionamiento de marcas** (ej. Samsung, Motorola, LG) frente a rebajas de competidores.
- **Detectar oportunidades de margen** mediante el análisis de dispersión entre el precio regular y el precio de oferta.

## 🏗️ Arquitectura de Datos (End-to-End)
El flujo de datos sigue las mejores prácticas de automatización y escalabilidad en la nube:

1. **Orquestación (CI/CD):** **GitHub Actions** dispara el pipeline automáticamente de forma bi-semanal mediante *Cron Jobs*, eliminando la necesidad de intervención manual.
2. **Ingesta (Web Scraping):** Scripts en Python utilizando `ScraperAPI` con manejo de excepciones, sistema de reintentos (*retries*) y rotación de proxies para garantizar la robustez de la captura.
3. **Procesamiento Distribuido (ETL):** **Databricks** y **PySpark** gestionan la limpieza de strings, casteo estricto de tipos de datos y aplicación de lógica de negocio.
4. **Almacenamiento (Delta Lake):** Modelado dimensional optimizado bajo un **Esquema Estrella**, generando Claves Subrogadas (*Surrogate Keys*) numéricas (`id_producto`) para máxima performance.
5. **Capa Semántica y Visualización (BI):** Power BI conectado al modelo Delta para análisis interactivo y data storytelling orientado a nivel ejecutivo.

## ⚙️ Características Técnicas Destacadas
* **Performance Optimizada:** Implementación de un modelo de datos en estrella (Star Schema) en Databricks, reemplazando cadenas de texto largas por identificadores numéricos únicos (`id_producto`) para cruzar hechos y dimensiones con máxima velocidad.
* **Código Limpio y Modular:** Lógica de extracción separada por categorías estratégicas y diccionarios de marcas.
* **Data Storytelling:** Diseño de dashboard en Power BI optimizado para lectura rápida de KPIs, análisis de dispersión de precios y detección de outliers.
* **Manejo de Historial:** Política de retención de datos y partición de tablas temporales para análisis evolutivo.

## 📂 Estructura del Repositorio
```text
📦 Retail-Price-Scraper
 ┣ 📂 .github/workflows/    # Orquestación CI/CD (GitHub Actions)
 ┣ 📂 scraper/              # Módulo de ingesta en Python
 ┃ ┗ 📜 Fravega_Completo.py # Lógica core de web scraping
 ┣ 📂 notebooks/            # Procesamiento distribuido
 ┃ ┗ 📜 Scraping_Retail.ipynb # Transformaciones ETL en PySpark / SQL
 ┣ 📂 dashboard/            # Capa de visualización
 ┃ ┗ 📜 Dashboard_Fravega.pbix
 ┣ 📜 requirements.txt      # Dependencias del entorno de ingesta
 ┗ 📜 README.md             # Documentación técnica
```

## 🚀 Despliegue y Ejecución
### Opción A: Pipeline Automatizado (Producción)
El proyecto está desplegado en producción. El flujo de trabajo .github/workflows/etl_fravega.yml se ejecuta automáticamente mediante un cron schedule. Los logs de ingesta pueden auditarse directamente en la pestaña Actions del repositorio.

### Opción B: Ejecución Local (Desarrollo)
Para replicar el entorno de ingesta en local:
1. Clonar el repositorio:
```bash
git clone https://github.com/jlandaa/Retail-Price-Scraper.git
cd Retail-Price-Scraper
```
2. Instalar dependencias de Python:
```bash
pip install -r requirements.txt
```
3. Ejecutar el scraper:
```bash
python scraper/Fravega_Completo.py
```
4. Procesar en la nube:
* Importar notebooks/Scraping_Retail.ipynb a un Workspace de Databricks.
* Adjuntar a un clúster activo y ejecutar las celdas de transformación.


---
👨‍💻 **Juan Manuel Landa** — *Computer Engineer | Data Analyst & BI Consultant*  
🔗 [LinkedIn](https://ar.linkedin.com/in/juan-manuel-landa/en) • 🌐 [Portfolio](https://juan-manuel-landa.netlify.app/) • ✉️ [Contacto](mailto:jmlanda93@gmail.com)
