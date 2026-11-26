# Patrón 10: Engrane p2

13 de octubre de 2026. Estado: **preliminar** (por confirmar con el taller). Fundición en arena en verde, aluminio ≈ 7 % Si.

## Reglas fijas (decididas por el equipo, valen para todas las piezas)

- Salida de 3° en todas las paredes.
- Se mecanizan todas las caras: sobremetal mínimo de 3 mm, y 4,5 mm en la cara de partición (queda arriba en el molde).
- Sin perforaciones ni machos: los agujeros y huecos menores de 24 mm se rellenan en el patrón y se mecanizan después; los huecos grandes pasantes en la dirección de extracción se dejan como islas de arena formadas por el propio patrón.
- Contracción 1,3 % (escala ×1,013).
- Radios mínimos de 3 mm en las aristas convexas y los rincones.

## Pieza de partida

Archivo `Engrane p2.STEP`. Cilindro de Ø35 mm y 32 mm de largo con ranuras y 4 agujeros pequeños en los extremos.

- Caja envolvente: 35,0 × 35,0 × 32,0 mm. Volumen 30,1 cm³ (≈ 78 g en aluminio).

## Orientación y partición

- La cara plana del patrón (plano de partición) corresponde a la cara de Y mínimo del STEP (Y = -3,2 mm). Esa cara queda arriba en el molde, y el resto de la pieza cuelga dentro de la caja inferior.
- Patrón de una sola pieza, plano de partición plano, sin machos. La orientación se eligió automáticamente como la de menor volumen de bruto entre las seis posibles (volumen aproximado de bruto en cm³: +Z 67 | −Z 67 | +X 67 | −X 67 | +Y 62 | −Y 62).

## Patrón y bruto

- Bruto fundido esperado (sin contraer): 45,7 × 45,7 × 40,0 mm, 60,2 cm³ (≈ 157 g de aluminio).
- Patrón (×1,013): 46,3 × 46,3 × 40,6 mm. El bruto sin contraer es el patrón dividido entre 1,013.
- Sobremetal mínimo comprobado: 3,1 mm en todas las caras (4,5 mm en la cara de partición); salida de 3° en todas las paredes.
- Huecos pasantes rellenados (diámetro equivalente aproximado, mm): ninguno.
- Huecos pasantes conservados: ninguno.
- Verificación: pieza contenida en el bruto, malla cerrada, 0 % de área con contrasalida o con salida insuficiente.

## Mazarota

- Una mazarota cónica, Ø54 mm en la base y Ø47 mm arriba, 75 mm de alto (`10_mazarota_forma.stl`). Ubicación: ver M1 en la planta de `10_comprobacion.png`, centrada sobre la zona más gruesa de la cara plana. Van en la caja superior, sobre la cara de 4,5 mm de sobremetal, así que su huella se mecaniza después.
- Cálculo (módulo de Chvorinov): módulo de la pieza 0,72 cm (0,89 cm descontando la huella de la mazarota); módulo de la mazarota 1,10 cm; relación 1,24 (mayor que 1,2).
- Peso: 391 g por mazarota frente a ≈ 157 g de la pieza en bruto; rendimiento 29 % (sin bebedero).
- Cajas: la superior al menos 100 mm de alto (mazarota más 25 mm de arena) y la inferior al menos 70 mm (bruto de 40,1 mm más 30 mm).
- Colada: lo más simple es verter por una mazarota; si prefieren un bebedero aparte, que entre por la zona alta de la pieza con un canal corto en el plano de partición. Lo decide el taller.

## Observaciones

- Pieza compacta: la mazarota (Ø54 mm en la base) pesa más que la pieza y el rendimiento es de solo 29 %. El taller puede probar una mazarota más baja con cuello o dos laterales.
- Los valores son típicos de arena en verde artesanal; la aleación del laboratorio no está certificada y no se simuló la solidificación.

## Archivos

- `10_patron_3grados_x1.013.stl`: patrón listo para imprimir (cara plana sobre la cama, sin soportes).
- `10_mazarota_forma.stl`: forma de la mazarota para imprimir.
- `10_comprobacion.png`: planta y secciones con la pieza final dentro del bruto y la mazarota.
- `10_vistas_patron.png`: vistas del bruto, mapa de relieve y de espesor.
