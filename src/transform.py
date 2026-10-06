"""
TRANSFORM — De datos crudos a un dataset analítico
=================================================

Este módulo convierte datos en formato ancho a un dataset analítico final,
con columnas derivadas y un join con rubros por provincia y año.
"""

import logging

import config

CLAVE_TOTAL = "__TOTAL__"

COLUMNAS = [
    "anio",
    "provincia",
    "destino",
    "region_destino",
    "valor_musd",
    "total_provincia_musd",
    "participacion_pct",
    "var_interanual_pct",
    "decada",
    "ranking_destino",
    "es_top3",
    "rubro_principal",
    "pp_participacion_pct",
]


# ======================================================================
# 1) ANCHO -> LARGO
# ======================================================================
def extraer_anio(fecha_texto):
    """Convierte '1993-01-01' en el entero 1993."""
    return int(fecha_texto[:4])


def ancho_a_largo(paquetes_destino):
    """Recibe paquetes crudos y devuelve filas en formato largo."""
    filas = []

    for paquete in paquetes_destino:
        provincia = paquete["provincia"]
        columnas = paquete["orden_columnas"]

        if CLAVE_TOTAL not in columnas:
            continue

        posicion_total = columnas.index(CLAVE_TOTAL)

        for fila_cruda in paquete["data"]:
            fecha = fila_cruda[0]
            valores = fila_cruda[1:]
            anio = extraer_anio(fecha)
            total = valores[posicion_total] if posicion_total < len(valores) else None

            for posicion, destino in enumerate(columnas):
                if destino == CLAVE_TOTAL:
                    continue

                if posicion >= len(valores):
                    continue

                valor = valores[posicion]
                if valor is None:
                    continue

                filas.append(
                    {
                        "anio": anio,
                        "provincia": provincia,
                        "destino": destino,
                        "valor_musd": round(valor, 2),
                        "total_provincia_musd": round(total, 2) if total is not None else None,
                    }
                )

    logging.info("  ancho_a_largo: %s filas", len(filas))
    return filas


# ======================================================================
# 2) COLUMNAS DERIVADAS SIMPLES
# ======================================================================
def clasificar_region(destino):
    """Devuelve la región geoeconómica de un país de destino."""
    return config.REGIONES.get(destino, config.REGION_POR_DEFECTO)


def calcular_decada(anio):
    """Devuelve la década de un año como texto."""
    inicio = (anio // 10) * 10
    return f"{inicio}s"


def calcular_participacion(valor, total):
    """Qué porcentaje del total exportado representa este destino."""
    if total is None or total == 0:
        return None
    return round((valor / total) * 100, 2)


def agregar_derivadas_simples(filas):
    """Agrega region_destino, decada y participacion_pct a cada fila."""
    for fila in filas:
        fila["region_destino"] = clasificar_region(fila["destino"])
        fila["decada"] = calcular_decada(fila["anio"])
        fila["participacion_pct"] = calcular_participacion(
            fila["valor_musd"], fila["total_provincia_musd"]
        )
    return filas


# ======================================================================
# 3) VARIACIÓN INTERANUAL
# ======================================================================
def calcular_variacion(actual, anterior):
    """Variación porcentual entre dos valores."""
    if anterior in (None, 0):
        return None
    return round(((actual - anterior) / anterior) * 100, 2)


def agregar_variacion_interanual(filas):
    """Agrega var_interanual_pct comparando cada fila con el año previo."""
    indice = {
        (fila["provincia"], fila["destino"], fila["anio"]): fila["valor_musd"]
        for fila in filas
    }

    for fila in filas:
        clave_anterior = (fila["provincia"], fila["destino"], fila["anio"] - 1)
        anterior = indice.get(clave_anterior)
        fila["var_interanual_pct"] = calcular_variacion(fila["valor_musd"], anterior)
    return filas


# ======================================================================
# 4) RANKING DE DESTINOS
# ======================================================================
def agregar_ranking(filas, top_n=None):
    """Agrega ranking_destino y es_top3 por provincia y año."""
    if top_n is None:
        top_n = config.TOP_N

    grupos = {}
    for fila in filas:
        clave = (fila["provincia"], fila["anio"])
        grupos.setdefault(clave, []).append(fila)

    for grupo in grupos.values():
        ordenado = sorted(grupo, key=lambda f: f["valor_musd"], reverse=True)
        for posicion, fila in enumerate(ordenado, start=1):
            fila["ranking_destino"] = posicion
            fila["es_top3"] = posicion <= top_n
    return filas


# ======================================================================
# 5) JOIN CON LOS RUBROS
# ======================================================================
def construir_indice_rubros(paquetes_rubro):
    """Recibe paquetes de rubros y devuelve un índice por (provincia, anio)."""
    indice = {}

    for paquete in paquetes_rubro:
        provincia = paquete["provincia"]
        columnas = paquete["orden_columnas"]

        for fila in paquete["data"]:
            fecha = fila[0]
            anio = extraer_anio(fecha)
            valores = {columna: valor for columna, valor in zip(columnas, fila[1:])}
            valores_validos = {k: v for k, v in valores.items() if v is not None}

            if not valores_validos:
                rubro_principal = None
                pp_participacion_pct = None
            else:
                rubro_principal = max(valores_validos, key=valores_validos.get)
                total = sum(valores_validos.values())
                primario = valores_validos.get("Productos primarios", 0)
                pp_participacion_pct = None if total == 0 else round((primario / total) * 100, 2)

            indice[(provincia, anio)] = {
                "rubro_principal": rubro_principal,
                "pp_participacion_pct": pp_participacion_pct,
            }

    logging.info("  índice de rubros: %s claves (provincia, año)", len(indice))
    return indice


def unir_con_rubros(filas, indice_rubros):
    """Hace LEFT JOIN por (provincia, anio) con el índice de rubros."""
    for fila in filas:
        match = indice_rubros.get((fila["provincia"], fila["anio"]))
        if match is None:
            fila["rubro_principal"] = None
            fila["pp_participacion_pct"] = None
        else:
            fila["rubro_principal"] = match["rubro_principal"]
            fila["pp_participacion_pct"] = match["pp_participacion_pct"]
    return filas


# ======================================================================
# ORQUESTACIÓN DEL TRANSFORM
# ======================================================================
def ordenar_columnas(filas):
    """Devuelve las filas con las claves en el orden definido por COLUMNAS."""
    return [{columna: fila.get(columna) for columna in COLUMNAS} for fila in filas]


def transformar(datos_crudos):
    """Recibe {'destino': [...], 'rubro': [...]} y devuelve el dataset final."""
    logging.info("TRANSFORM: iniciando")

    filas = ancho_a_largo(datos_crudos["destino"])
    filas = agregar_derivadas_simples(filas)
    filas = agregar_variacion_interanual(filas)
    filas = agregar_ranking(filas)

    indice = construir_indice_rubros(datos_crudos["rubro"])
    filas = unir_con_rubros(filas, indice)

    filas.sort(key=lambda f: (f["provincia"], f["anio"], f["ranking_destino"]))
    filas = ordenar_columnas(filas)

    logging.info("TRANSFORM OK: %s filas x %s columnas", len(filas), len(COLUMNAS))
    return filas
