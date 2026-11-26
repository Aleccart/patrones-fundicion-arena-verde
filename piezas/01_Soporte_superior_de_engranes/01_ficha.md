# Patrón 01: Soporte superior de engranes

13 de octubre de 2026. Estado: **versión 2, preliminar** (por confirmar con el taller). Fundición en arena en verde, aluminio ≈ 7 % Si.

## Reglas fijas (decididas por el equipo, valen para todas las piezas)

- Salida de 3° en todas las paredes.
- Se mecanizan todas las caras: sobremetal mínimo de 3 mm, y 4,5 mm en la cara de partición (queda arriba en el molde).
- Sin perforaciones ni machos: todos los agujeros se rellenan en el patrón y se taladran después.
- Contracción 1,3 % (escala ×1,013).
- R3 en los bordes convexos de la cara lejana.

## Pieza de partida

Se partió de `Soporte superior de engranes.STEP`. El STEP y el STL "mod de fundición" tienen exactamente la misma geometría que el original (mismos 179 puntos y 38 superficies; solo cambia el nombre), así que no traían salidas, rellenos ni sobremetal.

- Barra de 65 × 17 × 27 mm con esquinas verticales R5.
- 2 agujeros Ø4,5 pasantes (eje Z) con rebaje cilíndrico Ø8 × 4 mm para la cabeza del tornillo, en x = ±26,5 mm.
- 6 agujeros Ø2,5 (eje Y) en rejilla de 3 × 2, a 15 mm en X y 10 mm en Z.
- Volumen 27,8 cm³ (≈ 72 g en aluminio). Sin paredes delgadas (la dimensión mínima es 17 mm).

## Patrón

- Extracción en Z. La cara plana del patrón es el plano de partición y queda arriba en el molde.
- Sobremetal lateral real: 3,2 mm junto a la cara lejana y 4,8 mm en la partición (la salida suma material). Arriba 3 mm; en la cara de partición 4,5 mm.
- Esquinas R9,8 en la partición (R5 más sobremetal).
- Bruto fundido esperado (sin contraer): 74,6 × 26,6 en la partición, 34,5 mm de alto, 59,6 cm³, ≈ 155 g de aluminio sin bebedero ni mazarota.
- Patrón (×1,013): 75,6 × 27,0 × 34,9 mm.

## Mazarota

- **Dónde:** una sola, centrada sobre la cara plana de partición, en el centro de la pieza (x = 0, y = 0). Va en la caja superior. Esa cara es la de 4,5 mm de sobremetal, así que la huella de la mazarota se mecaniza después.
- **Forma y tamaño:** cónica, Ø42 mm en la base y Ø36 mm arriba, 58 mm de alto (`01_mazarota_forma.stl`, para imprimir con la base ancha apoyada). La base sobresale unos 7,7 mm a cada lado del ancho de la pieza (26,6 mm); no es problema.
- **Cálculo (módulo de Chvorinov):** módulo de la pieza 0,63 cm (0,71 cm descontando la huella de la mazarota); módulo de la mazarota 0,85 cm. Relación 1,36 (1,21 descontando la huella), mayor que 1,2. Es una estimación para arena en verde artesanal; el taller puede ajustarla.
- **Rendimiento:** la mazarota pesa ≈ 180 g frente a ≈ 155 g de la pieza (rendimiento del 46 %).
- **Cajas:** la caja superior debe tener al menos 85 mm de alto (mazarota de 58 mm más 25 mm de arena) y la inferior unos 65 mm (pieza de 34,5 mm más 30 mm).
- **Colada:** lo más simple es verter por la propia mazarota. Si prefieren un bebedero aparte, que vaya en un extremo, con un canal corto en el plano de partición que entre por la zona alta de la pieza. Lo decide el taller.

## Mecanizado posterior previsto

1. Fresar las seis caras hasta 65 × 17 × 27 mm y cortar las esquinas R5.
2. Taladrar 2 × Ø4,5 pasantes y hacer el rebaje Ø8 × 4 desde la cara superior (la de 27 mm de altura).
3. Taladrar los 6 × Ø2,5 de la cara en Y.

## Archivos

- `01_patron_3grados_x1.013.stl`: patrón listo para imprimir (cara plana sobre la cama, sin soportes).
- `01_mazarota_forma.stl`: forma de la mazarota para imprimir.
- `01_bruto_sin_contraccion.stl`: bruto fundido esperado, para el CAM o para comprobar.
- `01_comprobacion.png` y `01_vistas_patron.png`: pieza final y mazarota dentro del molde, y vistas del patrón.
- `generar_patron_01.py` y `dimensionar_mazarota_01.py`: generan los STL con otros parámetros.
