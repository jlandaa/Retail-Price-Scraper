import glob
import hashlib
import logging
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def configurar_logging() -> None:
    """Configura el formato de logs con timestamp y nivel para auditoría en CI/CD."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def obtener_tz_argentina() -> ZoneInfo | timezone:
    """Devuelve la zona horaria de Buenos Aires con fallback a UTC-3 si falta tzdata."""
    try:
        return ZoneInfo("America/Argentina/Buenos_Aires")
    except ZoneInfoNotFoundError:
        return timezone(timedelta(hours=-3))


TZ_ARGENTINA = obtener_tz_argentina()

# Umbrales del Data Quality Gate
MIN_PRODUCTOS_VALIDOS = 100
MIN_RATIO_CATEGORIAS_OK = 0.50
MIN_RATIO_PRECIOS_VALIDOS = 0.50

# ==========================================
# 1. LISTA DE CATEGORÍAS
# ==========================================
CATEGORIAS_ESTRATEGICAS = [
    # --- TECNOLOGÍA ---
    {"url": "https://www.fravega.com/l/celulares/celulares-liberados/", "nombre": "Smartphones"},
    {"url": "https://www.fravega.com/l/tv-y-video/tv/", "nombre": "Televisores"},
    {"url": "https://www.fravega.com/l/informatica/notebooks/", "nombre": "Notebooks"},
    {"url": "https://www.fravega.com/l/videojuegos/", "nombre": "Gaming y Videojuegos"},
    # --- ELECTRODOMÉSTICOS ---
    {"url": "https://www.fravega.com/l/heladeras-freezers-y-cavas/", "nombre": "Heladeras"},
    {"url": "https://www.fravega.com/l/lavado/", "nombre": "Lavado"},
    {
        "url": "https://www.fravega.com/l/climatizacion/aire-acondicionado/",
        "nombre": "Aires Acondicionados",
    },
    {
        "url": "https://www.fravega.com/l/pequenos-electrodomesticos/",
        "nombre": "Pequeños Electrodomésticos",
    },
    # --- HOGAR Y ESTILO DE VIDA ---
    {"url": "https://www.fravega.com/l/muebles/", "nombre": "Muebles"},
    {"url": "https://www.fravega.com/l/colchones-y-sommiers/", "nombre": "Colchones y Sommiers"},
    {"url": "https://www.fravega.com/l/deportes-y-fitness/", "nombre": "Deportes y Fitness"},
    {
        "url": "https://www.fravega.com/e/belleza-y-cuidado-personal/",
        "nombre": "Belleza y Cuidado Personal",
    },
    {"url": "https://www.fravega.com/l/herramientas/", "nombre": "Herramientas"},
    # --- ENTRETENIMIENTO Y NIÑOS ---
    {"url": "https://www.fravega.com/l/audio/", "nombre": "Audio"},
    {"url": "https://www.fravega.com/l/juguetes-y-juegos/", "nombre": "Juguetes"},
    # --- BEBÉS ---
    {
        "url": "https://www.fravega.com/l/bebes-y-primera-infancia/cochecitos/",
        "nombre": "Bebés y Primera Infancia",
    },
    {
        "url": "https://www.fravega.com/l/bebes-y-primera-infancia/cunas-practicunas-y-corralitos/",
        "nombre": "Bebés y Primera Infancia",
    },
]

# ==========================================
# 2. DICCIONARIO DE MARCAS
# ==========================================
MARCAS_CONOCIDAS = [
    "SAMSUNG",
    "MOTOROLA",
    "APPLE",
    "XIAOMI",
    "TCL",
    "LG",
    "PHILIPS",
    "NOBLEX",
    "HISENSE",
    "BGH",
    "SONY",
    "LENOVO",
    "HP",
    "DELL",
    "ASUS",
    "ACER",
    "WHIRLPOOL",
    "DREAN",
    "PHILCO",
    "MABE",
    "GAFA",
    "PATRICK",
    "OSTER",
    "LILIANA",
    "ATMA",
    "MIDEA",
    "SURREY",
    "ALCATEL",
    "ZTE",
    "BANGHO",
    "PIONEER",
    "BOSCH",
    "BLACK+DECKER",
    "GAMA",
    "REMINGTON",
    "CHICCO",
    "KIDDY",
    "MACLAREN",
]

PATRONES_MARCAS = [
    (marca, re.compile(rf"(?<!\w){re.escape(marca)}(?!\w)", re.IGNORECASE))
    for marca in MARCAS_CONOCIDAS
    if marca != "GAMA"
]

# Reglas específicas para GA.MA / Gama (evita confundir con "alta gama", "media gama", etc.)
PATRON_GAMA_EXPLICITO = re.compile(r"(?<!\w)GA[\.\s]MA(?!\w)", re.IGNORECASE)
PATRON_GAMA_CONTEXTO = re.compile(
    r"(?<!alta\s)(?<!media\s)(?<!baja\s)(?<!\w)GAMA(?!\w)",
    re.IGNORECASE,
)

PALABRAS_EXCLUIDAS_PRECIO = ("imp", "cuota", "envío", "envio", "ahorr")


# ==========================================
# 3. FUNCIONES PURAS DE PARSEO Y CALIDAD (TESTEABLES)
# ==========================================
def extraer_sku(url_producto: str) -> tuple[str, str]:
    """Devuelve (sku_final, sku_crudo) con fallback MD5 determinístico."""
    partes_url = [part for part in url_producto.split("?")[0].split("/") if part]
    if partes_url:
        sku_crudo = partes_url[-1]
    else:
        sku_crudo = hashlib.md5(url_producto.encode("utf-8")).hexdigest()[:12]
    return f"FRA-{sku_crudo[:40]}", sku_crudo


def limpiar_nombre_producto(nombre_bruto: str) -> str:
    """Elimina precios, impuestos y textos de envío pegados al título."""
    return re.split(
        r"\$|Vendido por|Precio s/imp|Llega en|Retiralo",
        nombre_bruto.strip(),
    )[0].strip()


def detectar_marca(url_producto: str, nombre_producto: str, categoria: str = "") -> str:
    """Identifica la marca por palabra completa y desambigua GA.MA por formato/categoría."""
    texto_busqueda = f"{nombre_producto} {url_producto.replace('-', ' ').replace('/', ' ')}"
    for marca, patron in PATRONES_MARCAS:
        if patron.search(texto_busqueda):
            return marca

    if PATRON_GAMA_EXPLICITO.search(texto_busqueda):
        return "GAMA"

    if categoria == "Belleza y Cuidado Personal" and PATRON_GAMA_CONTEXTO.search(texto_busqueda):
        return "GAMA"

    return "OTRAS"


def extraer_cuotas(texto_cuotas: str | None) -> int:
    """Extrae la cantidad numérica de cuotas o devuelve 1 por defecto."""
    if not texto_cuotas:
        return 1
    nums_cuota = re.findall(r"\d+", texto_cuotas)
    return int(nums_cuota[0]) if nums_cuota else 1


def parsear_precios(textos_precios: list[str]) -> tuple[float, float, bool]:
    """Parsea precios en formato argentino y filtra impuestos, cuotas, envíos y ahorros."""
    valores: list[float] = []

    for texto in textos_precios:
        texto_limpio = texto.lower()
        if any(palabra in texto_limpio for palabra in PALABRAS_EXCLUIDAS_PRECIO):
            continue

        match = re.search(r"\$\s*([\d\.,]+)", texto)
        if match:
            num_str = match.group(1).replace(".", "").replace(",", ".")
            try:
                valores.append(float(num_str))
            except ValueError:
                continue

    if not valores:
        return 0.0, 0.0, False

    valores_unicos = sorted(set(valores), reverse=True)
    if len(valores_unicos) >= 2:
        return valores_unicos[0], valores_unicos[1], True
    return valores_unicos[0], valores_unicos[0], True


def parsear_html_pagina(html: str, nombre_categoria: str) -> list[dict]:
    """Extrae todos los productos válidos de una página HTML de listado."""
    soup = BeautifulSoup(html, "html.parser")
    enlaces_productos = soup.find_all("a", href=re.compile(r"/p/"))

    urls_vistas: set[str] = set()
    productos: list[dict] = []

    for link in enlaces_productos:
        url_producto = link["href"]
        if not url_producto.startswith("http"):
            url_producto = f"https://www.fravega.com{url_producto}"

        if url_producto in urls_vistas:
            continue
        urls_vistas.add(url_producto)

        contenedor = link.find_parent(["article", "div", "li"])
        if not contenedor:
            continue

        sku_final, sku_crudo = extraer_sku(url_producto)
        nombre_producto = limpiar_nombre_producto(link.text)

        if len(nombre_producto) < 5:
            span_titulo = contenedor.find("span", string=re.compile(r"[a-zA-Z]"))
            nombre_producto = (
                span_titulo.text.strip() if span_titulo else sku_crudo.replace("-", " ").title()
            )

        marca = detectar_marca(url_producto, nombre_producto, nombre_categoria)
        texto_cuotas = contenedor.find(string=re.compile(r"(?i)cuotas?"))
        cuotas_detectadas = extraer_cuotas(texto_cuotas)

        textos_precios = contenedor.find_all(string=re.compile(r"\$"))
        precio_regular, precio_oferta, hay_stock = parsear_precios(textos_precios)

        productos.append(
            {
                "sku_original": sku_final,
                "competidor": "Fravega",
                "marca": marca,
                "categoria": nombre_categoria,
                "nombre_producto": nombre_producto,
                "url_producto": url_producto,
                "precio_regular": precio_regular,
                "precio_oferta": precio_oferta,
                "cuotas": cuotas_detectadas,
                "hay_stock": hay_stock,
            }
        )

    return productos


def validar_calidad_datos(
    df: pd.DataFrame,
    categorias_exitosas: int,
    total_categorias: int,
    min_productos: int = MIN_PRODUCTOS_VALIDOS,
    min_ratio_categorias: float = MIN_RATIO_CATEGORIAS_OK,
    min_ratio_precios: float = MIN_RATIO_PRECIOS_VALIDOS,
) -> tuple[bool, list[str]]:
    """Data Quality Gate: evita publicar CSVs parciales o corruptos por cambios en el sitio."""
    errores: list[str] = []

    if df.empty:
        return False, ["El dataset resultante está vacío (0 productos)."]

    if len(df) < min_productos:
        errores.append(
            f"Volumen insuficiente: {len(df)} productos únicos (mínimo requerido: {min_productos})."
        )

    if total_categorias > 0:
        ratio_categorias = categorias_exitosas / total_categorias
        if ratio_categorias < min_ratio_categorias:
            errores.append(
                f"Cobertura de categorías baja: {categorias_exitosas}/{total_categorias} "
                f"({ratio_categorias:.0%}, mínimo requerido: {min_ratio_categorias:.0%})."
            )

    ratio_precios_validos = float((df["precio_oferta"] > 0).mean())
    if ratio_precios_validos < min_ratio_precios:
        errores.append(
            f"Porcentaje de precios válidos bajo: {ratio_precios_validos:.0%} "
            f"(mínimo requerido: {min_ratio_precios:.0%}). Posible cambio en el HTML de precios."
        )

    return len(errores) == 0, errores


# ==========================================
# 4. RETENCIÓN Y ORQUESTACIÓN
# ==========================================
def aplicar_politica_retencion(carpeta: str = "data", dias_retencion: int = 30) -> int:
    logger.info("Iniciando limpieza de CSVs mayores a %d días...", dias_retencion)
    if not os.path.exists(carpeta):
        return 0

    fecha_limite = datetime.now(TZ_ARGENTINA).date() - timedelta(days=dias_retencion)
    archivos_csv = glob.glob(os.path.join(carpeta, "fravega_*.csv"))
    eliminados = 0

    for archivo in archivos_csv:
        try:
            nombre_base = os.path.basename(archivo)
            fecha_str = nombre_base.replace("fravega_", "").replace(".csv", "")
            if datetime.strptime(fecha_str, "%Y-%m-%d").date() < fecha_limite:
                os.remove(archivo)
                eliminados += 1
                logger.info("Eliminado por retención: %s", nombre_base)
        except (ValueError, OSError) as exc:
            logger.warning("No se pudo procesar %s en retención: %s", archivo, exc)
            continue

    if eliminados > 0:
        logger.info("Limpieza exitosa: %d archivos eliminados.", eliminados)
    else:
        logger.info("Limpieza completada: no hubo archivos para eliminar.")
    return eliminados


def extraer_fravega_robusto(max_paginas: int = 5) -> None:
    api_key = os.environ.get("SCRAPER_API_KEY")
    if not api_key:
        logger.error("No se encontró SCRAPER_API_KEY en las variables de entorno.")
        sys.exit(1)

    datos_totales: list[dict] = []
    categorias_exitosas = 0
    total_categorias = len(CATEGORIAS_ESTRATEGICAS)

    with requests.Session() as session:
        for cat in CATEGORIAS_ESTRATEGICAS:
            url_base = cat["url"]
            nombre_categoria = cat["nombre"]
            sub_categoria = url_base.strip("/").split("/")[-1].replace("-", " ").title()
            logger.info("PROCESANDO: %s (%s)", nombre_categoria.upper(), sub_categoria)

            productos_en_categoria = 0

            for p in range(1, max_paginas + 1):
                url = url_base if p == 1 else f"{url_base}?page={p}"
                max_reintentos = 3
                exito_conexion = False
                response: requests.Response | None = None

                for intento in range(max_reintentos):
                    try:
                        time.sleep(random.uniform(2, 5))
                        payload = {"api_key": api_key, "url": url, "country_code": "ar"}
                        response = session.get(
                            "https://api.scraperapi.com",
                            params=payload,
                            timeout=60,
                        )

                        if response.status_code == 200:
                            exito_conexion = True
                            break

                        logger.warning(
                            "Status %d en %s pág %d (Intento %d/%d). Reintentando en 3s...",
                            response.status_code,
                            sub_categoria,
                            p,
                            intento + 1,
                            max_reintentos,
                        )
                        time.sleep(3)

                    except requests.exceptions.RequestException as exc:
                        logger.warning(
                            "Error de red (%s) en %s pág %d (Intento %d/%d). Esperando 5s...",
                            exc.__class__.__name__,
                            sub_categoria,
                            p,
                            intento + 1,
                            max_reintentos,
                        )
                        time.sleep(5)

                if not exito_conexion or response is None:
                    logger.error(
                        "Se agotaron los %d reintentos en %s. Saltando a la siguiente categoría.",
                        max_reintentos,
                        sub_categoria,
                    )
                    break

                try:
                    productos = parsear_html_pagina(response.text, nombre_categoria)
                    if not productos:
                        logger.info("Fin del catálogo en %s página %d.", sub_categoria, p)
                        break

                    datos_totales.extend(productos)
                    productos_en_categoria += len(productos)
                    logger.info(
                        "%d productos capturados en %s pág %d.",
                        len(productos),
                        sub_categoria,
                        p,
                    )

                except Exception as exc:
                    logger.error("Error en el parseo de %s pág %d: %s", sub_categoria, p, exc)
                    break

            if productos_en_categoria > 0:
                categorias_exitosas += 1

    if not datos_totales:
        logger.error("No se obtuvieron datos en ninguna categoría.")
        sys.exit(1)

    df = pd.DataFrame(datos_totales).drop_duplicates(subset=["sku_original", "categoria"])

    # Data Quality Gate antes de escribir el CSV
    es_valido, errores_calidad = validar_calidad_datos(
        df=df,
        categorias_exitosas=categorias_exitosas,
        total_categorias=total_categorias,
    )
    if not es_valido:
        logger.error("Data Quality Gate RECHAZADO. No se guardará el CSV:")
        for err in errores_calidad:
            logger.error("  - %s", err)
        sys.exit(1)

    carpeta_destino = "data"
    os.makedirs(carpeta_destino, exist_ok=True)
    fecha_hoy = datetime.now(TZ_ARGENTINA).strftime("%Y-%m-%d")
    nombre_archivo = os.path.join(carpeta_destino, f"fravega_{fecha_hoy}.csv")
    df.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")
    logger.info(
        "EXITOSO: %d productos únicos (%d/%d categorías OK) guardados en %s",
        len(df),
        categorias_exitosas,
        total_categorias,
        nombre_archivo,
    )
    aplicar_politica_retencion(carpeta_destino, 30)


if __name__ == "__main__":
    configurar_logging()
    extraer_fravega_robusto(max_paginas=5)
