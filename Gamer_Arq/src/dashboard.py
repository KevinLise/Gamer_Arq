"""Etapa 4 - Dashboard GameHub (parte 2).

Lee SOLO archivos de data/gold/ y arma la cuadrícula "bento":
  - Tarjeta verde: Top 10 de juegos con su gráfico de barras.
  - Tarjeta lima:  géneros más populares con sus barras.
  - Tarjetas blancas: precio promedio por año (línea) y valoración por año (barras).

Ejecutar:  streamlit run src/dashboard.py
"""

import html
from pathlib import Path

import pandas as pd
import streamlit as st

GOLD_DIR = Path("data/gold")

# ==================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA (siempre va primero)
# ==================================================================
st.set_page_config(page_title="GameHub", layout="wide")

# ==================================================================
# 2. CSS PERSONALIZADO (paleta y formas de la guía de estilo)
# ==================================================================
CSS = """
<style>
/* ---------- Paleta ---------- */
:root{
  --verde:#2B6355;      /* tarjetas principales, banners, botones */
  --lima:#B7E22D;       /* acento, botón principal, resaltados  */
  --fondo:#F6F7F2;      /* fondo de la página (blanco hueso)    */
  --blanco:#FFFFFF;     /* tarjetas claras                      */
  --texto:#111111;      /* texto principal                      */
  --texto2:#6B7280;     /* texto secundario                     */
  --pill:#E3EBE5;       /* etiquetas                            */
  --radio:24px;         /* esquinas redondeadas                 */
}

/* ---------- Base ---------- */
.stApp{
  background:var(--fondo);
  color:var(--texto);
  font-family:"Inter","Segoe UI",system-ui,-apple-system,Arial,sans-serif;
}
header[data-testid="stHeader"]{ background:transparent; }
.block-container{ max-width:1180px; padding-top:1.4rem; padding-bottom:3rem; }

/* ---------- Encabezado ---------- */
.gh-header{ display:flex; align-items:center; justify-content:space-between;
            padding:6px 0 26px; }
.gh-logo{ display:flex; align-items:center; gap:10px; font-size:20px; font-weight:800; }
.gh-mark{ width:28px; height:28px; border-radius:9px; background:var(--lima);
          color:var(--verde); display:flex; align-items:center; justify-content:center;
          font-size:15px; font-weight:900; }
.gh-nav{ display:flex; gap:30px; font-size:14px; color:var(--texto2); }
.gh-nav .activo{ color:var(--texto); font-weight:700; }
.gh-btn{ background:var(--verde); color:#fff; border-radius:999px;
         padding:11px 24px; font-size:14px; font-weight:700; }

/* ---------- Banner KPI ---------- */
.kpi{ position:relative; background:var(--verde); color:#fff; border-radius:28px;
      text-align:center; padding:54px 24px; overflow:hidden; }
.kpi-numero{ font-size:92px; font-weight:800; line-height:1; letter-spacing:-2px; }
.kpi-label{ margin-top:16px; font-size:13px; letter-spacing:.24em;
            text-transform:uppercase; color:#CFE3D9; }
.kpi-star{ position:absolute; color:var(--lima); }
.kpi-star.izq{ left:40px; top:46px; font-size:18px; }
.kpi-star.der{ right:48px; bottom:50px; font-size:26px; }
.kpi-star.der2{ right:130px; top:42px; font-size:13px; opacity:.55; }

/* ---------- Cuadrícula bento y tarjetas ---------- */
.bento{ display:grid; grid-template-columns:repeat(3,1fr); gap:24px; margin-top:26px; }
.col-1{ grid-column:span 1; }
.col-2{ grid-column:span 2; }
.col-3{ grid-column:span 3; }
.tarjeta{ position:relative; border-radius:var(--radio); padding:28px 30px 30px;
          box-shadow:0 8px 26px rgba(17,17,17,.05); }
.tarjeta-verde{ background:var(--verde); color:#fff; }
.tarjeta-lima{ background:var(--lima); color:var(--texto); }
.tarjeta-blanca{ background:var(--blanco); color:var(--texto); }

/* Muesca: esquina superior derecha recortada + estrellita de 4 puntas */
.muesca::after{ content:""; position:absolute; top:-1px; right:-1px; z-index:1;
                width:56px; height:56px; background:var(--fondo);
                border-bottom-left-radius:26px; }
.muesca::before{ content:"✦"; position:absolute; top:12px; right:15px; z-index:2;
                 font-size:20px; color:var(--verde); }
.tarjeta-verde.muesca::before{ color:var(--lima); }

/* ---------- Etiquetas (pill) y títulos ---------- */
.pill{ display:inline-block; background:var(--pill); color:#31413A; font-size:11px;
       font-weight:700; letter-spacing:.1em; text-transform:uppercase;
       padding:7px 15px; border-radius:999px; }
.tarjeta-verde .pill{ background:rgba(255,255,255,.16); color:#DDEBE3; }
.tarjeta-lima .pill{ background:rgba(17,17,17,.10); color:#1F2A24; }
.titulo{ font-size:26px; font-weight:800; text-transform:uppercase; margin:16px 0 4px; }
.col-1 .titulo{ font-size:21px; }
.subtitulo{ font-size:13px; color:var(--texto2); margin-bottom:18px; }
.tarjeta-verde .subtitulo{ color:#B9CFC5; }
.tarjeta-lima .subtitulo{ color:rgba(17,17,17,.65); }

/* ---------- Barras horizontales ---------- */
.fila{ display:grid; grid-template-columns:minmax(170px,320px) 1fr 96px 64px; gap:16px;
       align-items:center; padding:11px 0; border-bottom:1px solid rgba(255,255,255,.12); }
.fila:last-child{ border-bottom:none; padding-bottom:0; }
.fila-3{ display:grid; grid-template-columns:minmax(84px,132px) 1fr 64px; gap:12px;
         align-items:center; padding:9px 0; border-bottom:1px solid rgba(255,255,255,.12); }
.fila-3:last-child{ border-bottom:none; padding-bottom:0; }
.fila-nombre{ font-size:14px; font-weight:600; white-space:nowrap; overflow:hidden;
              text-overflow:ellipsis; }
.fila-pista{ height:10px; background:rgba(255,255,255,.14); border-radius:999px;
             overflow:hidden; }
.fila-lleno{ height:100%; background:var(--lima); border-radius:999px; }
.fila-valor{ font-size:13px; font-weight:800; text-align:right;
             font-variant-numeric:tabular-nums; }
.fila-pct{ font-size:12px; color:#B9CFC5; text-align:right; }
.tarjeta-verde .fila-valor{ color:var(--lima); }

/* Barras sobre tarjeta lima */
.tarjeta-lima .fila-3{ border-bottom-color:rgba(17,17,17,.12); }
.tarjeta-lima .fila-pista{ background:rgba(17,17,17,.12); }
.tarjeta-lima .fila-lleno{ background:var(--verde); }
.tarjeta-lima .fila-valor{ color:#17331F; }

/* Barras sobre tarjeta blanca */
.tarjeta-blanca .fila-3{ border-bottom-color:#EDF0EA; }
.tarjeta-blanca .fila-pista{ background:#EDF0EA; }
.tarjeta-blanca .fila-lleno{ background:var(--verde); }
.tarjeta-blanca .fila-valor{ color:var(--verde); }

/* ---------- Gráfico de líneas (SVG) ---------- */
.svg-grafico{ width:100%; height:auto; display:block; margin-top:6px; }

/* ---------- Gráfico de barras verticales (valoración) ---------- */
.vchart{ display:flex; border-bottom:1px solid #E1E4DD; }
.vcol{ flex:1; display:flex; flex-direction:column; align-items:center; }
.vzona{ height:200px; width:100%; display:flex; align-items:flex-end; }
.vbar{ position:relative; width:calc(100% - 8px); background:var(--verde);
       border-radius:5px 5px 0 0; }
.vbar span{ position:absolute; top:-16px; left:-6px; right:-6px; text-align:center;
            font-size:10px; font-weight:700; color:var(--texto2); }
.vanios{ display:flex; margin-top:7px; }
.vanios span{ flex:1; text-align:center; font-size:10px; color:var(--texto2); }

/* ---------- Separador fino ---------- */
.linea{ border:none; border-top:1px solid #E1E4DD; margin:34px 0 0; }
</style>
"""

# Inyectamos el CSS en la página (sin esto no hay estilos)
st.markdown(CSS, unsafe_allow_html=True)


# ==================================================================
# 3. FUNCIONES AUXILIARES
# ==================================================================
def cargar(nombre: str) -> pd.DataFrame:
    """Lee un archivo Parquet de la capa Gold."""
    return pd.read_parquet(GOLD_DIR / f"{nombre}.parquet")


def entero(valor) -> str:
    """27075 -> '27.075' (formato español)."""
    return f"{int(valor):,}".replace(",", ".")


def grafico_linea(x, y) -> str:
    """Dibuja una línea de tendencia en SVG puro (sin librerías extra).

    x: lista de valores del eje horizontal (años)
    y: lista de valores del eje vertical (precio promedio)
    """
    ancho, alto = 700, 240
    izq, der, arr, abajo = 48, 16, 18, 32
    plot_ancho = ancho - izq - der
    plot_alto = alto - arr - abajo
    ymin, ymax = min(y), max(y)
    rango = (ymax - ymin) or 1.0
    n = len(x)

    # Coordenadas de cada punto
    coords = []
    for i, valor in enumerate(y):
        px = izq + plot_ancho * (i / (n - 1))
        py = arr + plot_alto * (1 - (valor - ymin) / rango)
        coords.append((px, py))
    base = arr + plot_alto

    # Área bajo la línea
    area = (
        f"M {coords[0][0]:.1f},{base:.1f} "
        + " ".join(f"L {px:.1f},{py:.1f}" for px, py in coords)
        + f" L {coords[-1][0]:.1f},{base:.1f} Z"
    )

    # Líneas guía y etiquetas del eje Y
    guias = ""
    for valor in (ymin, (ymin + ymax) / 2, ymax):
        py = arr + plot_alto * (1 - (valor - ymin) / rango)
        guias += (
            f'<line x1="{izq}" y1="{py:.1f}" x2="{ancho - der}" y2="{py:.1f}" '
            f'stroke="#E1E4DD" stroke-width="1"/>'
            f'<text x="{izq - 8}" y="{py + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#6B7280">{valor:.1f}</text>'
        )

    # Etiquetas del eje X (5 años repartidos)
    marcas = sorted({0, (n - 1) // 4, (n - 1) // 2, 3 * (n - 1) // 4, n - 1})
    ejes = "".join(
        f'<text x="{coords[i][0]:.1f}" y="{alto - 10}" text-anchor="middle" '
        f'font-size="11" fill="#6B7280">{x[i]}</text>'
        for i in marcas
    )

    # Puntos de la serie
    puntos_svg = "".join(
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#2B6355" '
        f'stroke="#FFFFFF" stroke-width="1.5"/>'
        for px, py in coords
    )

    return (
        f'<svg class="svg-grafico" viewBox="0 0 {ancho} {alto}">'
        f'<path d="{area}" fill="#B7E22D" fill-opacity="0.35"/>'
        f"{guias}"
        f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in coords)}" '
        f'fill="none" stroke="#2B6355" stroke-width="3" stroke-linejoin="round"/>'
        f"{puntos_svg}{ejes}"
        f"</svg>"
    )


# ==================================================================
# 4. DATOS (solo de data/gold/)
# ==================================================================
resumen = cargar("resumen")
valores = dict(zip(resumen["metrica"], resumen["valor"]))
ranking_top = cargar("ranking_juegos").head(10)
generos_top = cargar("por_genero").head(8)
anios = cargar("por_anio")

# ==================================================================
# 5. ENCABEZADO
# ==================================================================
st.markdown(
    """
<div class="gh-header">
  <div class="gh-logo"><span class="gh-mark">G</span>GameHub</div>
  <nav class="gh-nav">
    <span class="activo">Resumen</span>
    <span>Ranking</span>
    <span>Géneros</span>
    <span>Precios</span>
  </nav>
  <span class="gh-btn">Explorar datos</span>
</div>
""",
    unsafe_allow_html=True,
)

# ==================================================================
# 6. BANNER KPI
# ==================================================================
st.markdown(
    f"""
<div class="kpi">
  <span class="kpi-star izq">&#10022;</span>
  <span class="kpi-star der2">&#10022;</span>
  <span class="kpi-star der">&#10022;</span>
  <div class="kpi-numero">{entero(valores['total_juegos'])}</div>
  <div class="kpi-label">Juegos analizados en Steam</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==================================================================
# 7. TARJETA VERDE: TOP 10 DE JUEGOS
# ==================================================================
max_opiniones = ranking_top["total_ratings"].max()

# Ojo: sin salto de línea al final. Si el trozo termina en "\n" se genera una
# línea en blanco y Streamlit deja de interpretar el HTML (lo corta ahí).
filas_top = []
for posicion, juego in ranking_top.iterrows():
    ancho = 100 * juego["total_ratings"] / max_opiniones
    # Cada fila en una sola línea y sin sangría: si no, Streamlit la pinta
    # como bloque de código en vez de HTML.
    filas_top.append(
        f'<div class="fila">'
        f'<span class="fila-nombre">{posicion + 1}. {html.escape(str(juego["name"]))}</span>'
        f'<div class="fila-pista"><div class="fila-lleno" style="width:{ancho:.1f}%"></div></div>'
        f'<span class="fila-valor">{entero(juego["total_ratings"])}</span>'
        f'<span class="fila-pct">{juego["pct_positivo"]:.1f}%</span>'
        "</div>"
    )
filas_top = "\n".join(filas_top)

# ==================================================================
# 8. TARJETA LIMA: GÉNEROS MÁS POPULARES
# ==================================================================
max_juegos_genero = generos_top["juegos"].max()

filas_genero = []
for genero in generos_top.itertuples():
    ancho = 100 * genero.juegos / max_juegos_genero
    filas_genero.append(
        f'<div class="fila-3">'
        f'<span class="fila-nombre">{html.escape(str(genero.genero))}</span>'
        f'<div class="fila-pista"><div class="fila-lleno" style="width:{ancho:.1f}%"></div></div>'
        f'<span class="fila-valor">{entero(genero.juegos)}</span>'
        "</div>"
    )
filas_genero = "\n".join(filas_genero)

# ==================================================================
# 9. TARJETAS BLANCAS: PRECIO (línea) Y VALORACIÓN (barras)
# ==================================================================
svg_precio = grafico_linea(list(anios["anio"]), list(anios["precio_promedio"]))

# Solo años con suficientes lanzamientos (evita años con 1 o 2 juegos)
valoracion = anios[anios["juegos"] >= 20]

barras_valor = []
anios_barras = []
for fila in valoracion.itertuples():
    pct = fila.pct_positivo_prom
    barras_valor.append(
        f'<div class="vcol"><div class="vzona">'
        f'<div class="vbar" style="height:{pct:.0f}%">'
        f'<span>{pct:.0f}%</span></div></div></div>'
    )
    anios_barras.append(f"<span>{fila.anio}</span>")
barras_valor = "\n".join(barras_valor)
anios_barras = "".join(anios_barras)

# ==================================================================
# 10. CUADRÍCULA BENTO
# ==================================================================
st.markdown(
    f"""
<div class="bento">
  <div class="tarjeta tarjeta-verde muesca col-2">
    <span class="pill">Ranking</span>
    <div class="titulo">Top 10 juegos con más opiniones</div>
    <div class="subtitulo">Barra = número total de opiniones &nbsp;·&nbsp; % = opiniones positivas</div>
{filas_top}
  </div>
  <div class="tarjeta tarjeta-lima muesca col-1">
    <span class="pill">Géneros</span>
    <div class="titulo">Géneros más populares</div>
    <div class="subtitulo">Número de juegos de cada género (un juego puede tener varios)</div>
{filas_genero}
  </div>
  <div class="tarjeta tarjeta-blanca col-2">
    <span class="pill">Precios</span>
    <div class="titulo">Precio promedio por año</div>
    <div class="subtitulo">Precio de lanzamiento promedio de los juegos de cada año</div>
{svg_precio}
  </div>
  <div class="tarjeta tarjeta-blanca col-1">
    <span class="pill">Valoración</span>
    <div class="titulo">Valoración positiva por año</div>
    <div class="subtitulo">% medio de opiniones positivas (años con 20+ lanzamientos)</div>
    <div class="vchart">
{barras_valor}
    </div>
    <div class="vanios">
{anios_barras}
    </div>
  </div>
</div>
""".strip(),
    unsafe_allow_html=True,
)

# Separador fino (la parte 3 agregará filtros y tabla debajo)
st.markdown('<hr class="linea">', unsafe_allow_html=True)
