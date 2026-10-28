
from pathlib import Path
import pandas as pd
import re
import unicodedata

base = Path("datos")
registros = []

extensiones = {".jpg", ".jpeg", ".png"}

def quitar_acentos(texto):
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )

def clasificar(nombre):
    nombre = quitar_acentos(nombre.upper())
    nombre = re.sub(r"\s+", " ", nombre).strip()

    # Quitar números añadidos antes del código entre paréntesis
    nombre = re.sub(r"\s+\d+(?=\s*\()", "", nombre)
    nombre = re.sub(r"\s+\d+$", "", nombre)
    nombre = re.sub(r"\s+", " ", nombre).strip()

    # Unificar variantes confirmadas
    if "BALLED UP" in nombre:
        return "BALLED UP (BU)"

    if "BROKEN CUTTERS" in nombre or "BROKEN TEETH" in nombre:
        return "BROKEN TEETH / CUTTERS (BT)"

    if "WEAR TOOTH" in nombre or "WORN TEETH" in nombre:
        return "WORN TEETH (WT)"

    if "CHIPPED TEETH" in nombre:
        return "CHIPPED TEETH (CT)"

    if "BOND FAILURE" in nombre:
        return "BOND FAILURE (BF)"

    if "HEAT CHECKING" in nombre:
        return "HEAT CHECKING (HC)"

    if "JUNK DAMAGE" in nombre:
        return "JUNK DAMAGE (JD)"

    if "LOST NOZZLE" in nombre:
        return "LOST NOZZLE (LN)"

    if "PLUGGED NOZZLE" in nombre:
        return "PLUGGED NOZZLE (PN)"

    if "RING OUT" in nombre:
        return "RING OUT (RO)"

    if "WASHED OUT" in nombre:
        return "WASHED OUT (WO)"

    if "CONE DRAGGED" in nombre:
        return "CONE DRAGGED (CD)"

    if "EROSION" in nombre:
        return "EROSION (ER)"

    if "LOST TEETH" in nombre:
        return "LOST TEETH (LT)"

    if "SHIRTTAIL DAMAGE" in nombre:
        return "SHIRTTAIL DAMAGE (SD)"

    # Las demás categorías quedan pendientes de revisión
    return nombre

for tipo_barrena in ["PDC", "Triconicas"]:
    carpeta = base / tipo_barrena

    if not carpeta.exists():
        print(f"No se encontró la carpeta: {carpeta}")
        continue

    for archivo in carpeta.rglob("*"):
        if not archivo.is_file():
            continue

        if archivo.suffix.lower() not in extensiones:
            continue

        nombre = quitar_acentos(archivo.stem.upper())

        # Excluir diagramas de referencia del entrenamiento
        if "DESGASTE INTERNO Y EXTERNO" in nombre:
            registros.append({
                "archivo": archivo.name,
                "tipo_barrena": tipo_barrena,
                "categoria": "REFERENCIA - NO ENTRENAR",
                "incluir_entrenamiento": "NO",
                "ruta": str(archivo)
            })
            continue

        registros.append({
            "archivo": archivo.name,
            "tipo_barrena": tipo_barrena,
            "categoria": clasificar(archivo.stem),
            "incluir_entrenamiento": "PENDIENTE DE REVISION",
            "ruta": str(archivo)
        })

df = pd.DataFrame(registros)

salida = base / "inventario_categorias.csv"
df.to_csv(salida, index=False, encoding="utf-8-sig")

print(f"\nArchivos revisados: {len(df)}")
print("\nArchivos por tipo de barrena:")
print(df["tipo_barrena"].value_counts())

print("\nCategorías detectadas:")
print(
    df.groupby(["tipo_barrena", "categoria"])
      .size()
      .to_string()
)

print(f"\nInventario guardado en: {salida}")
print("Las fotografías originales no se modificaron.")