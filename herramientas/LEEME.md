# Herramientas de los patrones de fundición

Scripts con los que se generaron los patrones de las piezas 02 a 10. La pieza 01 se hizo antes con un cálculo directo y su script está en `piezas/01_Soporte_superior_de_engranes/`.

- `s2m.py`: convierte un STEP en un STL por sólido. Necesita CadQuery.
- `process_piece.py`: a partir del STL calcula el bruto con sobremetal, salida y contracción, la orientación, las mazarotas y las imágenes de comprobación. Necesita NumPy, SciPy, Matplotlib y scikit-image.
- `hfcast.py`: funciones comunes de `process_piece.py`. Debe estar en la misma carpeta.

## Entorno

Instala los paquetes en un entorno virtual aparte, sin tocar el Python del sistema (ver el README principal).

## Uso

```powershell
python herramientas\s2m.py "pieza.STEP" carpeta_mallas
python herramientas\process_piece.py --mesh carpeta_mallas\pieza_0.stl --outdir salida --tag 11 --name "Nombre de la pieza"
```

Opciones de `process_piece.py`:

- `--orient auto|+z|-z|+x|-x|+y|-y`: dirección de extracción. Por defecto elige la de menor volumen de bruto.
- `--a 3.0`: sobremetal mínimo en mm. `--acope 4.5`: sobremetal en la cara de partición.
- `--draft 3.0`: salida en grados. `--rin 3.0`: radio mínimo de rincones. `--shrink 0.013`: contracción.
- `--dkeep 24`: los huecos menores de este diámetro (mm) se rellenan. Los mayores se conservan como islas de arena.
- `--revolve`: para engranes, usa la envolvente de revolución (cono o cilindro de las puntas) en lugar de los dientes.
- `--nrisers N`: número de mazarotas (0 calcula el número necesario).
- `--riserf 1.2`: relación entre el módulo de la mazarota y el de la pieza.
- `--pitch 0.4`: tamaño de celda de la malla en mm.

## Qué hace

1. Toma el mapa de alturas de la pieza en la dirección de extracción y rellena los huecos y entallas menores de 24 mm.
2. Lo dilata con un elemento que da el sobremetal en todas las caras y la salida exacta. Los bordes convexos quedan redondeados con radio igual al sobremetal.
3. Recorta en el plano de partición (con 4,5 mm de sobremetal), cierra la malla y la escala × 1,013 para el patrón.
4. Dimensiona la mazarota por el módulo de Chvorinov (1,2 veces el de la pieza) y la ubica sobre la zona más gruesa.

Es un modelo para decidir y preparar el patrón. No simula la solidificación.
