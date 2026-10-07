"""Etapa 1 - Bronze: guarda una copia cruda de los datos originales.

Lee data/raw/steam.csv y lo escribe en data/bronze/ sin modificar sus valores.
Solo agrega dos columnas de control (ingested_at y source_file) para saber
cuándo y desde qué archivo se cargaron los datos.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

# Rutas de entrada y salida (relativas a la raíz del proyecto)
RAW_FILE = Path("data/raw/steam.csv")
BRONZE_FILE = Path("data/bronze/steam_bronze.parquet")


def run() -> None:
    # 1) Leemos el CSV original tal como está, sin convertir nada
    df = pd.read_csv(RAW_FILE)
    filas_entrada = len(df)

    # 2) Columnas de control: no cambian los datos, solo dejan la traza
    df["ingested_at"] = datetime.now()  # fecha y hora de la carga
    df["source_file"] = RAW_FILE.name   # nombre del archivo de origen

    # 3) Creamos la carpeta si no existe y guardamos en Parquet
    BRONZE_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(BRONZE_FILE, index=False)

    print("=== BRONZE ===")
    print(f"Archivo leído   : {RAW_FILE}")
    print(f"Archivo creado  : {BRONZE_FILE}")
    print(f"Filas cargadas  : {filas_entrada}")
    print(f"Columnas        : {len(df.columns)} (18 originales + 2 de control)")


if __name__ == "__main__":
    run()
