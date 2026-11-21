from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from scraper.Fravega_Completo import (
    TZ_ARGENTINA,
    aplicar_politica_retencion,
    detectar_marca,
    extraer_cuotas,
    extraer_sku,
    limpiar_nombre_producto,
    parsear_html_pagina,
    parsear_precios,
    validar_calidad_datos,
)


def test_extraer_sku_normal_y_fallback_deterministico() -> None:
    sku_final, sku_crudo = extraer_sku(
        "https://www.fravega.com/p/celular-samsung-a55-12345/?utm_source=test"
    )
    assert sku_final == "FRA-celular-samsung-a55-12345"
    assert sku_crudo == "celular-samsung-a55-12345"

    # Si la URL no tiene segmentos, el fallback MD5 debe ser idéntico entre ejecuciones
    sku_a, crudo_a = extraer_sku("///")
    sku_b, crudo_b = extraer_sku("///")
    assert sku_a == sku_b
    assert len(crudo_a) == 12
    assert sku_a.startswith("FRA-")


def test_limpiar_nombre_producto() -> None:
    bruto = "Smart TV Samsung 55 4K $ 1.250.999 Precio s/imp. nac. $ 1.033.883 Llega en 24hs"
    assert limpiar_nombre_producto(bruto) == "Smart TV Samsung 55 4K"


@pytest.mark.parametrize(
    ("url", "nombre", "categoria", "esperado"),
    [
        (
            "https://www.fravega.com/p/tv-55-pulgadas-generico-1",
            "Smart TV 55 Pulgadas 4K",
            "Televisores",
            "OTRAS",
        ),
        (
            "https://www.fravega.com/p/tv-lg-55-pulgadas-2",
            "Smart TV LG 55 Pulgadas",
            "Televisores",
            "LG",
        ),
        (
            "https://www.fravega.com/p/taladro-black-decker-3",
            "Taladro Black-Decker 500W",
            "Herramientas",
            "BLACK+DECKER",
        ),
        (
            "https://www.fravega.com/p/celular-alta-gama-4",
            "Celular Alta Gama 128GB",
            "Smartphones",
            "OTRAS",
        ),
        (
            "https://www.fravega.com/p/planchita-gama-5",
            "Planchita de Pelo Gama Elegance",
            "Belleza y Cuidado Personal",
            "GAMA",
        ),
        (
            "https://www.fravega.com/p/secador-ga-ma-6",
            "Secador de Pelo GA.MA Italy",
            "Pequeños Electrodomésticos",
            "GAMA",
        ),
    ],
)
def test_detectar_marca_y_edge_cases(url: str, nombre: str, categoria: str, esperado: str) -> None:
    assert detectar_marca(url, nombre, categoria) == esperado


def test_extraer_cuotas() -> None:
    assert extraer_cuotas("6 cuotas sin interés de $ 120.000") == 6
    assert extraer_cuotas("Hasta 12 cuotas fijas") == 12
    assert extraer_cuotas(None) == 1
    assert extraer_cuotas("Sin financiación") == 1


def test_parsear_precios_argentinos_y_filtros() -> None:
    textos = [
        "$ 1.250.999,50",
        "$ 999.999,00",
        "Precio s/imp. nac. $ 826.445",
        "6 cuotas de $ 166.666",
        "Envio gratis desde $ 50.000",
        "Ahorrá $ 251.000",
        "$ 0",
    ]
    regular, oferta, hay_stock = parsear_precios(textos)
    assert regular == 1250999.50
    assert oferta == 999999.00
    assert hay_stock is True

    # Sin precios válidos -> sin stock
    assert parsear_precios(["$ 0", "Envío $ 5.000"]) == (0.0, 0.0, False)


def test_parsear_html_pagina_en_memoria() -> None:
    html_ejemplo = """
    <html>
      <body>
        <article>
          <a href="/p/celular-samsung-a55-101">Celular Samsung A55 256GB $ 799.999</a>
          <span>$ 999.999</span>
          <span>$ 799.999</span>
          <span>6 cuotas sin interés</span>
        </article>
        <article>
          <a href="/p/celular-samsung-a55-101">Duplicado en la misma página</a>
        </article>
        <article>
          <a href="/p/auricular-generico-202">Auricular Inalámbrico Sin Stock</a>
        </article>
      </body>
    </html>
    """
    productos = parsear_html_pagina(html_ejemplo, "Smartphones")
    assert len(productos) == 2

    primero = productos[0]
    assert primero["sku_original"] == "FRA-celular-samsung-a55-101"
    assert primero["marca"] == "SAMSUNG"
    assert primero["precio_regular"] == 999999.0
    assert primero["precio_oferta"] == 799999.0
    assert primero["cuotas"] == 6
    assert primero["hay_stock"] is True

    segundo = productos[1]
    assert segundo["hay_stock"] is False
    assert segundo["precio_oferta"] == 0.0


def test_validar_calidad_datos_gate() -> None:
    df_ok = pd.DataFrame(
        [
            {"sku_original": "FRA-1", "precio_oferta": 100.0},
            {"sku_original": "FRA-2", "precio_oferta": 200.0},
            {"sku_original": "FRA-3", "precio_oferta": 300.0},
        ]
    )
    es_valido, errores = validar_calidad_datos(
        df=df_ok, categorias_exitosas=10, total_categorias=17, min_productos=3
    )
    assert es_valido is True
    assert errores == []

    # Falla por cobertura baja de categorías y mayoría de precios en 0
    df_malo = pd.DataFrame(
        [
            {"sku_original": "FRA-1", "precio_oferta": 0.0},
            {"sku_original": "FRA-2", "precio_oferta": 0.0},
            {"sku_original": "FRA-3", "precio_oferta": 150.0},
        ]
    )
    es_valido, errores = validar_calidad_datos(
        df=df_malo, categorias_exitosas=2, total_categorias=17, min_productos=3
    )
    assert es_valido is False
    assert len(errores) == 2


def test_aplicar_politica_retencion_en_carpeta_temporal(tmp_path: Path) -> None:
    hoy = datetime.now(TZ_ARGENTINA).date()
    fecha_vieja = (hoy - timedelta(days=45)).strftime("%Y-%m-%d")
    fecha_reciente = (hoy - timedelta(days=5)).strftime("%Y-%m-%d")

    archivo_viejo = tmp_path / f"fravega_{fecha_vieja}.csv"
    archivo_reciente = tmp_path / f"fravega_{fecha_reciente}.csv"
    archivo_viejo.write_text("col\n1\n", encoding="utf-8")
    archivo_reciente.write_text("col\n2\n", encoding="utf-8")

    eliminados = aplicar_politica_retencion(carpeta=str(tmp_path), dias_retencion=30)
    assert eliminados == 1
    assert not archivo_viejo.exists()
    assert archivo_reciente.exists()
