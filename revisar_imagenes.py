
from pathlib import Path

base = Path("datos")

for categoria in ["PDC", "Triconicas"]:
    carpeta = base / categoria

    imagenes = [
        archivo
        for archivo in carpeta.rglob("*")
        if archivo.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ]

    print(f"\n{categoria}: {len(imagenes)} imágenes")

    for imagen in imagenes[:5]:
        print(" -", imagen.name)

print("\nRevisión terminada.")