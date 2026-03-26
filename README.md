# 📊 Retail Competitiveness & Pricing Strategy: End-to-End Data Pipeline

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)]()
[![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)]()

## 📌 Visión General del Proyecto
Este proyecto es una solución integral de Business Intelligence diseñada para monitorear la competitividad diaria en el sector retail. A través de un pipeline automatizado, se realiza web scraping para extraer precios, stock y descuentos del e-commerce de **Frávega** (enfocado en las categorías de tecnología y electrodomésticos). Los datos se procesan en la nube y se disponibilizan en un dashboard interactivo para analizar su estrategia comercial.

🔗 **[Ver Dashboard Interactivo (Publicado en Power BI)](https://app.powerbi.com/view?r=eyJrIjoiNjljMGY0NDUtYjBjMC00ODkxLWFjYWYtNzU3ZDkxN2QwOWE3IiwidCI6IjZjYmMyOTllLWIxZDUtNDJjZi1hMWRjLTgwNjZmMTdiN2QwNyIsImMiOjR9)**


## 💼 Impacto de Negocio
En la industria del retail, la agilidad para ajustar precios frente a la competencia define la cuota de mercado. Esta herramienta permite a los equipos de Pricing y Comercial:
* **Analizar la agresividad de descuentos** por categoría de producto (Audio, Climatización, Smartphones, etc.).
* **Monitorear el posicionamiento de marcas** (ej. Samsung, Motorola, LG) frente a rebajas de competidores.
* **Detectar oportunidades de margen** mediante el análisis de dispersión entre el precio regular y el precio de oferta.

## 🏗️ Arquitectura del Pipeline
El flujo de datos sigue las mejores prácticas de Data Engineering, dividiéndose en cuatro etapas clave:
1. **Extracción (Ingesta):** Scripts de Python utilizando ScraperAPI, implementando manejo de excepciones, sistema de reintentos (retries) y paginación para garantizar la robustez de la captura diaria.
2. **Procesamiento (ETL):** Databricks y PySpark se encargan de la limpieza de strings, casteo estricto de tipos de datos y aplicación de lógica de negocio.
3. **Almacenamiento (Data Warehouse):** Modelado de datos optimizado bajo un **Esquema Estrella**, generando Claves Subrogadas numéricas (Surrogate Keys) y guardando la información en formato Delta.
4. **Visualización (BI):** Power BI conectado al modelo para análisis interactivo, diseño UX/UI y reportes de nivel ejecutivo.

## ⚙️ Características Técnicas Destacadas
* **Performance Optimizada:** Implementación de un modelo de datos en estrella (Star Schema) en Databricks, reemplazando cadenas de texto largas por identificadores numéricos únicos (`id_producto`) para cruzar hechos y dimensiones con máxima velocidad.
* **Código Limpio y Modular:** Lógica de extracción separada por categorías estratégicas y diccionarios de marcas.
* **Data Storytelling:** Diseño de dashboard en Power BI optimizado para lectura rápida de KPIs, análisis de dispersión de precios y detección de outliers.
* **Manejo de Historial:** Política de retención de datos y partición de tablas temporales para análisis evolutivo.

## 📂 Estructura del Repositorio
```text
├── dashboard/              # Archivo .pbix original del dashboard interactivo
├── notebooks/              # Notebooks de Databricks con la lógica de transformación (SQL/PySpark)
├── scraper/                # Scripts de Python para la extracción diaria de datos
├── README.md               # Documentación del proyecto
└── requirements.txt        # Dependencias de Python para ejecutar el scraper
```

## 1. 🚀 Cómo ejecutar este proyecto localmente
Clonar el repositorio:
```bash
git clone https://github.com/jlandaa/Analisis-Precios-Fravega.git
```
## 2. Instalar dependencias de Python:
```bash
pip install -r requirements.txt
```
## 3. Ejecutar el scraper:
```bash
python scraper/Fravega_Completo.py
```
## 4. Procesar en la nube:
Subir los datos resultantes a Databricks y ejecutar el notebook
```text
notebooks/Scraping_Retail.ipynb
```


## 👨‍💻 Sobre mí
**Juan Manuel Landa**
* **Ingeniero en Computación** | **Data Analyst & BI Consultant**
* 📍 Quilmes, Buenos Aires, Argentina
* 💼 [LinkedIn](https://ar.linkedin.com/in/juan-manuel-landa/en)
* 🌐 [Portfolio Personal](https://juan-manuel-landa.netlify.app/)

Este proyecto forma parte de mi búsqueda activa de nuevas oportunidades en el área de **Data & Business Intelligence**.
