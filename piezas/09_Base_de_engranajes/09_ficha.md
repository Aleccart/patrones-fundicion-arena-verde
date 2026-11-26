# Patrón 09: Base de engranajes

13 de octubre de 2026. Estado: **preliminar** (por confirmar con el taller). Fundición en arena en verde, aluminio ≈ 7 % Si.

## Reglas fijas (decididas por el equipo, valen para todas las piezas)

- Salida de 3° en todas las paredes.
- Se mecanizan todas las caras: sobremetal mínimo de 3 mm, y 4,5 mm en la cara de partición (queda arriba en el molde).
- Sin perforaciones ni machos: los agujeros y huecos menores de 24 mm se rellenan en el patrón y se mecanizan después; los huecos grandes pasantes en la dirección de extracción se dejan como islas de arena formadas por el propio patrón.
- Contracción 1,3 % (escala ×1,013).
- Radios mínimos de 3 mm en las aristas convexas y los rincones.

## Pieza de partida

Archivo `Base de engranajes.STEP`. Marco rectangular de 42,5 × 70 × 18 mm con una ventana central pasante y agujeros transversales.

- Caja envolvente: 42,5 × 70,0 × 18,0 mm. Volumen 33,3 cm³ (≈ 87 g en aluminio).

## Orientación y partición

- La cara plana del patrón (plano de partición) corresponde a la cara de Y máximo del STEP (Y = 13,8 mm). Esa cara queda arriba en el molde, y el resto de la pieza cuelga dentro de la caja inferior.
- Patrón de una sola pieza, plano de partición plano, sin machos. La orientación se eligió automáticamente como la de menor volumen de bruto entre las seis posibles (volumen aproximado de bruto en cm³: +Z 113 | −Z 113 | +X 106 | −X 106 | +Y 94 | −Y 88).

## Patrón y bruto

- Bruto fundido esperado (sin contraer): 51,5 × 78,3 × 26,1 mm, 84,8 cm³ (≈ 220 g de aluminio).
- Patrón (×1,013): 52,1 × 79,3 × 26,4 mm. El bruto sin contraer es el patrón dividido entre 1,013.
- Sobremetal mínimo comprobado: 3,0 mm en todas las caras (4,5 mm en la cara de partición); salida de 3° en todas las paredes.
- Huecos pasantes rellenados (diámetro equivalente aproximado, mm): ninguno.
- Huecos pasantes conservados: 33,3.
- Verificación: pieza contenida en el bruto, malla cerrada, 0 % de área con contrasalida o con salida insuficiente.

## Mazarota

- Una mazarota cónica, Ø39 mm en la base y Ø33 mm arriba, 54 mm de alto (`09_mazarota_forma.stl`). Ubicación: ver M1 en la planta de `09_comprobacion.png`, centrada sobre la zona más gruesa de la cara plana. Van en la caja superior, sobre la cara de 4,5 mm de sobremetal, así que su huella se mecaniza después.
- Cálculo (módulo de Chvorinov): módulo de la pieza 0,60 cm (0,64 cm descontando la huella de la mazarota); módulo de la mazarota 0,79 cm; relación 1,24 (mayor que 1,2).
- Peso: 143 g por mazarota frente a ≈ 220 g de la pieza en bruto; rendimiento 61 % (sin bebedero).
- Cajas: la superior al menos 79 mm de alto (mazarota más 25 mm de arena) y la inferior al menos 56 mm (bruto de 26,0 mm más 30 mm).
- Colada: lo más simple es verter por una mazarota; si prefieren un bebedero aparte, que entre por la zona alta de la pieza con un canal corto en el plano de partición. Lo decide el taller.

## Observaciones

- La ventana central (≈ 33 mm de diámetro equivalente) se conserva: en el molde queda como una isla de arena de 16 mm de ancho mínimo en el plano de partición y ≈ 12 mm de alto (relación alto/ancho 0,7), estable en arena en verde. Si se rompiera al desmoldar, se rellena y se mecaniza.
- La base de la mazarota se solapa parcialmente con la ventana: no es problema, esa parte queda sobre arena.
- Los valores son típicos de arena en verde artesanal; la aleación del laboratorio no está certificada y no se simuló la solidificación.

## Archivos

- `09_patron_3grados_x1.013.stl`: patrón listo para imprimir (cara plana sobre la cama, sin soportes).
- `09_mazarota_forma.stl`: forma de la mazarota para imprimir.
- `09_comprobacion.png`: planta y secciones con la pieza final dentro del bruto y la mazarota.
- `09_vistas_patron.png`: vistas del bruto, mapa de relieve y de espesor.
