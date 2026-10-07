"""Etapa 2 - Silver: limpia y valida los datos de Bronze.

Lee data/bronze/steam_bronze.parquet y produce dos archivos:
  - data/silver/clean.parquet      -> registros válidos (listos para Gold)
  - data/silver/rejected.parquet   -> registros inválidos, con su motivo

Reglas aplicadas (en este orden):
  1. Normalizar nombres de columnas (minúsculas y sin espacios raros).
  2. Eliminar filas duplicadas.
  3. Convertir tipos: fechas a datetime, números a numérico, texto a str.
  4. Rechazar filas que incumplen las reglas de validez.
  5. Rellenar los nulos que no invalidan el registro.
"""

import re
from pathlib import Path

import pandas as pd

BRONZE_FILE = Path("data/bronze/steam_bronze.parquet")
CLEAN_FILE = Path("data/silver/clean.parquet")
REJECTED_FILE = Path("data/silver/rejected.parquet")

# Columnas que deben ser numéricas
COLUMNAS_NUMERICAS = [
    "appid", "english", "required_age", "achievements",
    "positive_ratings", "negative_ratings",
    "average_playtime", "median_playtime", "price",
]

# Todas las columnas de texto del dataset
COLUMNAS_TEXTO = [
    "name", "developer", "publisher", "platforms",
    "categories", "genres", "steamspy_tags", "owners",
]

# Columnas de texto donde el nulo se rellena (no son clave para analizar)
COLUMNAS_TEXTO_RELLENO = ["developer", "publisher"]

# Valor con el que se rellenan los vacíos de esas columnas
VALOR_RELLENO = "Desconocido"


def normalizar_nombre_columna(columna: str) -> str:
    """'Release Date' -> 'release_date'"""
    limpia = re.sub(r"[^0-9a-z]+", "_", columna.strip().lower())
    return limpia.strip("_")


def detectar_problemas(df: pd.DataFrame) -> dict:
    """Devuelve {motivo: máscara booleana} con los problemas de cada fila.

    Una fila con la máscara en True es una fila inválida (se rechaza).
    """
    return {
        "appid duplicado": df["appid"].notna() & df["appid"].duplicated(keep=False),
        "appid faltante": df["appid"].isna(),
        "nombre vacío": df["name"].isna() | (df["name"].fillna("").str.strip() == ""),
        "fecha inválida": df["release_date"].isna(),
        "precio negativo": df["price"] < 0,
        "rating negativo": (df["positive_ratings"] < 0) | (df["negative_ratings"] < 0),
        "número inválido": df[COLUMNAS_NUMERICAS].isna().any(axis=1),
    }


def run() -> None:
    df = pd.read_parquet(BRONZE_FILE)
    filas_entrada = len(df)

    # --- 1. Nombres de columnas en minúsculas y sin espacios ---
    df.columns = [normalizar_nombre_columna(c) for c in df.columns]

    # --- 2. Filas duplicadas ---
    antes = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    duplicadas = antes - len(df)

    # --- 3. Conversión de tipos ---
    # Fecha: lo que no se pueda parsear queda en NaT y después se rechaza.
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    # Números: lo que no se pueda convertir queda en NaN y después se rechaza.
    for columna in COLUMNAS_NUMERICAS:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    # Texto: quitar espacios sobrantes al inicio y al final.
    for columna in COLUMNAS_TEXTO:
        df[columna] = df[columna].str.strip()

    # --- 4. Reglas de validez ---
    motivos = detectar_problemas(df)

    # Motivo de rechazo de cada fila (vacío = fila válida)
    df["reject_reason"] = ""
    for motivo, mascara in motivos.items():
        df.loc[mascara, "reject_reason"] = df.loc[mascara, "reject_reason"].apply(
            lambda texto: f"{texto}, {motivo}" if texto else motivo
        )

    rechazadas = df[df["reject_reason"] != ""].copy()
    validas = df[df["reject_reason"] == ""].drop(columns="reject_reason").copy()

    # --- 5. Nulos en los registros válidos ---
    # Decisión: NO descartamos por nulos en developer/publisher porque no son
    # clave para las métricas; los rellenamos para poder agruparlos después.
    rellenos = {}
    for columna in COLUMNAS_TEXTO_RELLENO:
        vacios = validas[columna].isna() | (validas[columna].fillna("").str.strip() == "")
        rellenos[columna] = int(vacios.sum())
        validas.loc[vacios, columna] = VALOR_RELLENO

    # --- Guardamos ---
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    validas.to_parquet(CLEAN_FILE, index=False)
    rechazadas.to_parquet(REJECTED_FILE, index=False)

    # --- Reporte ---
    print("=== SILVER ===")
    print(f"Filas de entrada (Bronze)   : {filas_entrada}")
    print(f"Duplicadas eliminadas       : {duplicadas}")
    print(f"Filas evaluadas             : {filas_entrada - duplicadas}")
    print(f"Filas válidas -> clean      : {len(validas)}")
    print(f"Filas rechazadas -> rejected: {len(rechazadas)}")
    print(f"Motivos de rechazo          : {rechazadas['reject_reason'].value_counts().to_dict() or 'ninguno'}")
    print(f"Nulos rellenados con '{VALOR_RELLENO}': {rellenos}")
    print(f"Archivos: {CLEAN_FILE} | {REJECTED_FILE}")


if __name__ == "__main__":
    run()
