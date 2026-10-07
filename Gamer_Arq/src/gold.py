"""Etapa 3 - Gold: métricas de negocio listas para el dashboard.

Lee data/silver/clean.parquet y guarda cada métrica en un archivo aparte
dentro de data/gold/:

  ranking_juegos.parquet  -> ¿Qué juegos son los más populares y mejor valorados?
  por_anio.parquet        -> ¿Cómo evolucionan lanzamientos e ingresos en el tiempo?
  por_genero.parquet      -> ¿Qué géneros dominan el catálogo y cómo se reciben?
  resumen.parquet         -> Números clave del catálogo (tarjetas del dashboard)
"""

from pathlib import Path

import pandas as pd

SILVER_FILE = Path("data/silver/clean.parquet")
GOLD_DIR = Path("data/gold")


def agregar_columnas_base(df: pd.DataFrame) -> pd.DataFrame:
    """Columnas auxiliares que usan varias métricas.

    - total_ratings  : suma de opiniones positivas y negativas.
    - pct_positivo   : % de opiniones positivas (0 si nadie opinó).
    - owners_min     : mínimo del rango de dueños ("100000-200000" -> 100000).
    - ingreso_estim  : price * owners_min. NO es dinero real: es una
                       aproximación porque el dataset no trae ventas.
    """
    out = df.copy()
    total = out["positive_ratings"] + out["negative_ratings"]
    out["total_ratings"] = total
    out["pct_positivo"] = (100 * out["positive_ratings"] / total).round(1)
    out.loc[total == 0, "pct_positivo"] = 0.0
    out["owners_min"] = out["owners"].str.split("-").str[0].astype("int64")
    out["ingreso_estim"] = (out["price"] * out["owners_min"]).round(2)
    return out


def metrica_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Ranking completo de juegos por cantidad de opiniones (popularidad)."""
    out = agregar_columnas_base(df)
    out = out[out["total_ratings"] > 0]  # sin opiniones no se puede opinar
    out = out.sort_values("total_ratings", ascending=False).reset_index(drop=True)
    out.insert(0, "rank", out.index + 1)
    columnas = [
        "rank", "appid", "name", "release_date", "genres", "owners", "price",
        "positive_ratings", "negative_ratings", "total_ratings", "pct_positivo",
    ]
    return out[columnas]


def metrica_por_anio(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por año de lanzamiento: juegos, precio promedio e ingreso estimado."""
    out = agregar_columnas_base(df)
    out["anio"] = out["release_date"].dt.year
    tabla = (
        out.groupby("anio")
        .agg(
            juegos=("appid", "count"),
            precio_promedio=("price", "mean"),
            ingreso_estimado=("ingreso_estim", "sum"),
            opiniones_totales=("total_ratings", "sum"),
            pct_positivo_prom=("pct_positivo", "mean"),
        )
        .reset_index()
    )
    tabla["precio_promedio"] = tabla["precio_promedio"].round(2)
    tabla["ingreso_estimado"] = tabla["ingreso_estimado"].round(0)
    tabla["pct_positivo_prom"] = tabla["pct_positivo_prom"].round(1)
    return tabla.sort_values("anio").reset_index(drop=True)


def metrica_por_genero(df: pd.DataFrame) -> pd.DataFrame:
    """Un juego puede tener varios géneros: se explota la lista y se cuenta cada uno."""
    out = agregar_columnas_base(df)
    out["genero"] = out["genres"].str.split(";")
    out = out.explode("genero")
    out["genero"] = out["genero"].str.strip()
    tabla = (
        out.groupby("genero")
        .agg(
            juegos=("appid", "count"),
            precio_promedio=("price", "mean"),
            pct_positivo_prom=("pct_positivo", "mean"),
            opiniones_totales=("total_ratings", "sum"),
        )
        .reset_index()
    )
    # % sobre el total de etiquetas de género (un juego puede tener varias)
    tabla["pct_etiquetas"] = (100 * tabla["juegos"] / tabla["juegos"].sum()).round(1)
    tabla["precio_promedio"] = tabla["precio_promedio"].round(2)
    tabla["pct_positivo_prom"] = tabla["pct_positivo_prom"].round(1)
    return tabla.sort_values("juegos", ascending=False).reset_index(drop=True)


def metrica_resumen(df: pd.DataFrame) -> pd.DataFrame:
    """Números clave en formato largo (metrica, valor) para las tarjetas."""
    out = agregar_columnas_base(df)
    gratis = int((out["price"] == 0).sum())
    pares = out[out["total_ratings"] > 0]
    pct_global = 100 * pares["positive_ratings"].sum() / pares["total_ratings"].sum()
    valores = {
        "total_juegos": float(len(out)),
        "precio_promedio": float(out["price"].mean().round(2)),
        "precio_maximo": float(out["price"].max()),
        "juegos_gratis": float(gratis),
        "pct_juegos_gratis": float(round(100 * gratis / len(out), 1)),
        "anio_primero": float(out["release_date"].dt.year.min()),
        "anio_ultimo": float(out["release_date"].dt.year.max()),
        "opiniones_totales": float(out["total_ratings"].sum()),
        "pct_positivo_global": float(pct_global.round(1)),
        "generos_distintos": float(out["genres"].str.split(";").explode().nunique()),
    }
    return pd.DataFrame({"metrica": list(valores), "valor": list(valores.values())})


def run() -> None:
    df = pd.read_parquet(SILVER_FILE)
    print("=== GOLD ===")
    print(f"Fuente: {SILVER_FILE} ({len(df)} filas)")

    metricas = {
        "ranking_juegos": metrica_ranking(df),
        "por_anio": metrica_por_anio(df),
        "por_genero": metrica_por_genero(df),
        "resumen": metrica_resumen(df),
    }

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    for nombre, tabla in metricas.items():
        ruta = GOLD_DIR / f"{nombre}.parquet"
        tabla.to_parquet(ruta, index=False)
        print(f"  {ruta} -> {len(tabla)} filas x {len(tabla.columns)} columnas")


if __name__ == "__main__":
    run()
