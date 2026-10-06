# TP Final — Pipeline ETL de exportaciones del NEA

**Diplomatura en Data Analytics e IA Aplicada**  
**UNNE / Extender — Unidad II: Fundamentos de la Programación**
## ¿Qué hace mi pipeline?

Mi pipeline toma datos sobre las **exportaciones de las provincias del NEA** desde una API pública del INDEC disponible en datos.gob.ar.

Primero, obtiene los datos originales y los guarda. Luego, los organiza y transforma para que sean más fáciles de analizar. Durante este proceso se agrega información como el **porcentaje que representa cada destino, la variación respecto al año anterior, la década, el ranking de los destinos y los principales rubros de exportación**.

Finalmente, el pipeline genera un archivo **CSV** con todos los datos organizados y preparados para realizar futuros análisis, gráficos y estadísticas.

En resumen:

```text
API del INDEC
      ↓
Obtención de datos
      ↓
Organización y transformación
      ↓
Archivo CSV
      ↓
Datos listos para analizar

## ¿Cómo instalar y ejecutar el proyecto?

Para utilizar el proyecto es necesario tener instalado **Python 3.8 o una versión superior**.

### 1. Abrir el proyecto

Descargar o clonar el proyecto y abrir la carpeta desde **Visual Studio Code**.

### 2. Abrir la terminal

En Visual Studio Code, ir a:

```text
Terminal → New Terminal
## ¿De dónde salen los datos?

Los datos utilizados en este proyecto provienen del **INDEC (Instituto Nacional de Estadística y Censos)** y se obtienen mediante una **API pública de datos.gob.ar**.

La información corresponde a las exportaciones de las provincias del **NEA**:

- Chaco
- Corrientes
- Formosa
- Misiones

Los datos abarcan el período **1993 a 2024** y muestran información sobre los valores exportados, los países de destino y los principales rubros de exportación.

Primero, el pipeline obtiene estos datos desde la API y los guarda en la carpeta:

```text
data/raw/
## Algo que encontré en los datos

Al revisar la base de datos encontré un cambio interesante en **China como destino de las exportaciones de Chaco**.

En 1993, las exportaciones hacia China eran de solamente **0,31 millones de dólares** y China ocupaba el puesto 10 entre los destinos registrados. :chatgpt-content-reference{index="0"}

En los años siguientes, China fue aumentando su importancia. Por ejemplo, en 2008 las exportaciones hacia China llegaron a **140,15 millones de dólares**, representando el **35,8 %** de las exportaciones de Chaco de ese año. :chatgpt-content-reference{index="1"}

En 2024, China registró **110,93 millones de dólares** y ocupó el segundo lugar entre los destinos de Chaco, representando el **27,61 %** del total de ese año. :chatgpt-content-reference{index="2"}

Esto me llamó la atención porque muestra que **China pasó de ser un destino muy pequeño en 1993 a convertirse en uno de los principales destinos de las exportaciones de Chaco**.