
from pathlib import Path
from collections import Counter

base = Path("datos")
extensiones = {".jpg", ".jpeg", ".png"}

for categoria in ["PDC", "Triconicas"]:
    carpeta = base / categoria
    imagenes = [
        f for f in carpeta.rglob("*")
        if f.is_file() and f.suffix.lower() in extensiones
    ]

    print(f"\n--- {categoria} ---")
    conteo = Counter()

    for archivo in imagenes:
        nombre = archivo.stem.upper()

        if "REFERENCIA" in nombre or "REFERENCE" in nombre:
            etiqueta = "IMAGEN DE REFERENCIA"
        else:
            etiqueta = nombre

            # Quitar sufijos numéricos como " 1" o " 2"
            while etiqueta and etiqueta[-1].isdigit():
                etiqueta = etiqueta[:-1].rstrip()

        conteo[etiqueta] += 1

    for etiqueta, cantidad in sorted(conteo.items()):
        print(f"{cantidad:2} | {etiqueta}")