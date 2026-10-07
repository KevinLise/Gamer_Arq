# Plan: Pipeline de datos para GameHub (versión simple)

## Contexto

Proyecto académico: pipeline de datos para una plataforma de videojuegos, usando arquitectura **Medallion** (Bronze → Silver → Gold) con enfoque **ELT**.
Quien lo construye es **principiante**, así que el código debe ser **simple, comentado y explicado**.

## Reglas para el asistente (OpenCode)

1. Trabaja **una etapa a la vez**. Al terminar cada etapa, **detente** y espera confirmación antes de seguir.
2. Explica en español, con palabras sencillas, qué hace cada archivo y cada bloque importante.
3. Usa solo las herramientas listadas abajo. **No agregues** Kafka, Spark, Docker ni AWS.
4. Código corto y legible. Prefiere claridad sobre "elegancia".
5. Al terminar cada etapa, muestra cómo ejecutarla y cómo verificar que funcionó.

## Stack

- Python 3.10+
- pandas (lectura, limpieza y agregaciones)
- pyarrow (para guardar en formato Parquet)
- Streamlit (dashboard)
- PostgreSQL: **opcional**, solo si el usuario lo pide en la Etapa 5

## Fuente de datos

Dataset de Kaggle en formato CSV sobre videojuegos (ej. Steam games, estadísticas de jugadores o compras).
Dataset elegido: `[PONER NOMBRE Y ENLACE DEL DATASET AQUÍ]`

El CSV descargado se coloca en `data/raw/`.

## Estructura de carpetas

```
gamehub-pipeline/
├── data/
│   ├── raw/          # CSV original descargado de Kaggle (no se modifica)
│   ├── bronze/       # copia cruda de los datos
│   ├── silver/       # datos limpios
│   └── gold/         # métricas listas para el dashboard
├── src/
│   ├── bronze.py
│   ├── silver.py
│   ├── gold.py
│   └── dashboard.py
├── requirements.txt
└── README.md
```

## Etapas

### Etapa 0: Preparación

- Crear la estructura de carpetas.
- Crear `requirements.txt` con pandas, pyarrow y streamlit.
- Explicar cómo crear y activar un entorno virtual.
- Explorar el CSV: mostrar columnas, tipos, cantidad de filas y valores nulos.

**Entregable:** proyecto listo y un resumen del dataset.

### Etapa 1: Bronze (cargar datos originales)

- `src/bronze.py` lee el CSV de `data/raw/` y lo guarda **sin cambios** en `data/bronze/`.
- Agregar dos columnas de control: `ingested_at` (fecha de carga) y `source_file` (nombre del archivo).
- Objetivo: conservar el dato original para poder reprocesarlo.

**Entregable:** archivo en `data/bronze/` y mensaje con la cantidad de filas cargadas.

### Etapa 2: Silver (limpiar y validar)

`src/silver.py` lee Bronze y:

- Elimina filas duplicadas.
- Normaliza nombres de columnas (minúsculas, sin espacios).
- Convierte tipos (fechas, números, texto).
- Maneja nulos (rellenar o descartar, explicando la decisión).
- Separa los registros inválidos y los guarda en `data/silver/rejected.parquet`.
- Guarda los registros válidos en `data/silver/clean.parquet`.

**Entregable:** reporte impreso con filas de entrada, filas válidas y filas rechazadas.

### Etapa 3: Gold (métricas de negocio)

`src/gold.py` lee Silver y calcula, según las columnas disponibles:

- Ranking de juegos más populares / mejor valorados.
- Ingresos o ventas por período (si hay precio o fecha).
- Distribución por género o categoría.
- Estadísticas generales (promedios, totales).

Cada métrica se guarda como un archivo separado en `data/gold/`.

**Entregable:** archivos Gold y una explicación de qué responde cada métrica.

### Etapa 4: Dashboard

`src/dashboard.py` con Streamlit lee solo `data/gold/` y muestra:

- Tarjetas con números clave.
- Gráficos de barras y líneas con los rankings y las tendencias.
- Una tabla filtrable.

**Estilo visual:** seguir la sección "Guía de estilo del dashboard" de este documento (colores, tarjetas, botones y distribución). Usar CSS personalizado en Streamlit (`st.markdown(..., unsafe_allow_html=True)`).

**Ejecución:** `streamlit run src/dashboard.py`

**Entregable:** dashboard funcionando en el navegador.

### Etapa 5 (opcional): PostgreSQL

- Cargar las tablas Gold en PostgreSQL con `pandas.to_sql`.
- Hacer que el dashboard lea desde la base de datos en lugar de los archivos.

## Guía de estilo del dashboard

Inspirado en un diseño de referencia (web financiera, estilo verde y lima). **Solo se toma el estilo visual, no los textos, ilustraciones ni la tipografía pixelada.** Usar una fuente sans-serif limpia y moderna.

### Paleta (colores aproximados)

| Uso | Color |
|---|---|
| Verde oscuro (tarjetas principales, banners, botones) | `#2B6355` |
| Verde lima (tarjetas de acento, botón principal, resaltados) | `#B7E22D` |
| Fondo de la página | `#F6F7F2` (blanco hueso) |
| Tarjetas claras | `#FFFFFF` |
| Texto principal | `#111111` |
| Texto secundario | `#6B7280` |
| Etiquetas (pills) | `#E3EBE5` |

Tema **claro**. Los gráficos solo deben usar tonos de verde oscuro, lima y grises.

### Forma y componentes

- **Tarjetas:** esquinas muy redondeadas (~24 px), sin bordes marcados, sombra casi invisible. Alternar tres tipos: verde oscuro con texto blanco, lima con texto negro y blanca con texto negro.
- **Detalle característico:** a algunas tarjetas se les recorta una esquina (como una "muesca") y ahí va una pequeña estrella decorativa de 4 puntas. Hacerlo con CSS en 1 o 2 tarjetas, sin exagerar.
- **Botones:** forma de píldora (totalmente redondeados). Principal en verde lima o verde oscuro; secundario en negro.
- **Etiquetas (pills):** pequeñas, fondo gris verdoso claro, texto en mayúsculas pequeñas (ej. "RANKING", "GÉNEROS").
- **Títulos de sección:** en mayúsculas, grandes y en negrita.
- **Separadores:** líneas finas grises. Los filtros desplegables pueden usar un botón cuadrado pequeño con "+" / "−".
- **Decoración:** estrellitas y rombos pequeños en verde, muy discretos.

### Distribución (layout)

1. **Encabezado:** logo/nombre "GameHub" a la izquierda, navegación simple al centro, botón píldora a la derecha.
2. **Banner KPI:** franja en verde oscuro con esquinas redondeadas, un **número muy grande** centrado (ej. total de juegos analizados) y una etiqueta pequeña en mayúsculas debajo.
3. **Cuadrícula tipo "bento":** mezcla de tarjetas de distinto tamaño y color (verde oscuro, lima y blanca) con los rankings y gráficos principales. Una tarjeta verde oscuro para el Top de juegos, una lima para géneros populares y blancas para gráficos de precio/valoraciones.
4. **Sección de filtros y tabla:** fondo blanco, tarjeta redondeada, filtros como píldoras.
5. **Pie de página:** tarjeta blanca redondeada con el nombre del proyecto y los créditos del dataset.

### Reglas

- Mucho espacio en blanco; no saturar la pantalla.
- Mantener consistencia: mismos radios, mismos colores, mismos espacios en todo el dashboard.
- Los textos deben ser legibles (buen contraste sobre verde oscuro y lima).

## Evolución futura (solo para el documento, no se implementa)

| Tecnología | Cuándo se agregaría | Qué resuelve |
|---|---|---|
| Kafka | Si los eventos del juego llegan en tiempo real | Recibir y distribuir eventos continuamente |
| Spark | Si el volumen de datos supera lo que pandas maneja | Procesamiento distribuido (Batch y Streaming) |
| AWS S3 | Si se necesita almacenar datos a gran escala en la nube | Almacenamiento de objetos para el Data Lake |
| Docker | Si hay que reproducir el entorno en otras máquinas | Contenedores y entornos consistentes |

## Cómo encaja con los conceptos de la tarea

- **Medallion:** las carpetas `bronze/`, `silver/` y `gold/` son las capas.
- **ELT:** primero se carga el dato original (Bronze) y después se transforma (Silver y Gold).
- **Batch:** el pipeline procesa el CSV completo en lotes. Streaming queda como evolución futura con Kafka.

## Criterios de éxito

- [ ] El pipeline corre de principio a fin con un solo comando por etapa.
- [ ] Bronze conserva el dato original sin modificar.
- [ ] Silver reporta cuántos registros fueron rechazados y por qué.
- [ ] Gold contiene al menos 3 métricas útiles.
- [ ] El dashboard muestra las métricas sin errores.
- [ ] El README explica cómo instalar y ejecutar todo.
