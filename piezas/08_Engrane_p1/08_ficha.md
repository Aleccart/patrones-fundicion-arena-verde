# Patrón 08: Engrane p1

13 de octubre de 2026. Estado: **preliminar** (por confirmar con el taller). Fundición en arena en verde, aluminio ≈ 7 % Si.

## Reglas fijas (decididas por el equipo, valen para todas las piezas)

- Salida de 3° en todas las paredes.
- Se mecanizan todas las caras: sobremetal mínimo de 3 mm, y 4,5 mm en la cara de partición (queda arriba en el molde).
- Sin perforaciones ni machos: los agujeros y huecos menores de 24 mm se rellenan en el patrón y se mecanizan después; los huecos grandes pasantes en la dirección de extracción se dejan como islas de arena formadas por el propio patrón.
- Contracción 1,3 % (escala ×1,013).
- Radios mínimos de 3 mm en las aristas convexas y los rincones.

## Pieza de partida

Archivo `Engrane p1.STEP`. Engranaje cónico de Ø98,7 mm y 15,9 mm de espesor, con 4 agujeros de ≈ Ø4,5 mm en el centro.

- Caja envolvente: 98,7 × 98,7 × 15,8 mm. Volumen 73,8 cm³ (≈ 192 g en aluminio).

## Orientación y partición

- La cara plana del patrón (plano de partición) corresponde a la cara de Y máximo del STEP (Y = 28,8 mm). Esa cara queda arriba en el molde, y el resto de la pieza cuelga dentro de la caja inferior.
- Patrón de una sola pieza, plano de partición plano, sin machos. La orientación se eligió automáticamente como la de menor volumen de bruto entre las seis posibles (volumen aproximado de bruto en cm³: +Z 774 | −Z 774 | +X 774 | −X 774 | +Y 210 | −Y 185).

## Patrón y bruto

- Bruto fundido esperado (sin contraer): 107,2 × 107,2 × 23,9 mm, 178,8 cm³ (≈ 465 g de aluminio).
- Patrón (×1,013): 108,6 × 108,6 × 24,2 mm. El bruto sin contraer es el patrón dividido entre 1,013.
- Sobremetal mínimo comprobado: 3,3 mm en todas las caras (4,5 mm en la cara de partición); salida de 3° en todas las paredes.
- Huecos pasantes rellenados (diámetro equivalente aproximado, mm): 4,5, 4,5, 4,5, 4,5.
- Huecos pasantes conservados: ninguno.
- Verificación: pieza contenida en el bruto, malla cerrada, 0 % de área con contrasalida o con salida insuficiente.

## Mazarota

- Una mazarota cónica, Ø51 mm en la base y Ø43 mm arriba, 70 mm de alto (`08_mazarota_forma.stl`). Ubicación: ver M1 en la planta de `08_comprobacion.png`, centrada sobre la zona más gruesa de la cara plana. Van en la caja superior, sobre la cara de 4,5 mm de sobremetal, así que su huella se mecaniza después.
- Cálculo (módulo de Chvorinov): módulo de la pieza 0,76 cm (0,83 cm descontando la huella de la mazarota); módulo de la mazarota 1,03 cm; relación 1,24 (mayor que 1,2).
- Peso: 317 g por mazarota frente a ≈ 465 g de la pieza en bruto; rendimiento 59 % (sin bebedero).
- Cajas: la superior al menos 95 mm de alto (mazarota más 25 mm de arena) y la inferior al menos 54 mm (bruto de 23,9 mm más 30 mm).
- Colada: lo más simple es verter por una mazarota; si prefieren un bebedero aparte, que entre por la zona alta de la pieza con un canal corto en el plano de partición. Lo decide el taller.

## Observaciones

- Los dientes no se funden: el bruto es el disco con el cono envolvente de las puntas, con sobremetal y salida; los dientes se tallan después en CNC.
- Los 4 agujeros de ≈ Ø4,5 mm se rellenan y se taladran después.
- Los valores son típicos de arena en verde artesanal; la aleación del laboratorio no está certificada y no se simuló la solidificación.

## Archivos

- `08_patron_3grados_x1.013.stl`: patrón listo para imprimir (cara plana sobre la cama, sin soportes).
- `08_mazarota_forma.stl`: forma de la mazarota para imprimir.
- `08_comprobacion.png`: planta y secciones con la pieza final dentro del bruto y la mazarota.
- `08_vistas_patron.png`: vistas del bruto, mapa de relieve y de espesor.
