# Patrón 04: BR-012B Cuerpo Superior 01

13 de octubre de 2026. Estado: **preliminar** (por confirmar con el taller). Fundición en arena en verde, aluminio ≈ 7 % Si.

## Reglas fijas (decididas por el equipo, valen para todas las piezas)

- Salida de 3° en todas las paredes.
- Se mecanizan todas las caras: sobremetal mínimo de 3 mm, y 4,5 mm en la cara de partición (queda arriba en el molde).
- Sin perforaciones ni machos: los agujeros y huecos menores de 24 mm se rellenan en el patrón y se mecanizan después; los huecos grandes pasantes en la dirección de extracción se dejan como islas de arena formadas por el propio patrón.
- Contracción 1,3 % (escala ×1,013).
- Radios mínimos de 3 mm en las aristas convexas y los rincones.

## Pieza de partida

Archivo `BR-012B_Cuerpo_Superior_01.STEP`. Soporte en L: placa horizontal circular con hueco central de ≈ Ø24 mm y 6 agujeros, y una pared vertical de 74 mm de profundidad con fondo redondeado.

- Caja envolvente: 91,7 × 106,2 × 73,5 mm. Volumen 87,4 cm³ (≈ 227 g en aluminio).

## Orientación y partición

- La cara plana del patrón (plano de partición) corresponde a la cara de Z máximo del STEP (Z = 8,0 mm). Esa cara queda arriba en el molde, y el resto de la pieza cuelga dentro de la caja inferior.
- Patrón de una sola pieza, plano de partición plano, sin machos. La orientación se eligió automáticamente como la de menor volumen de bruto entre las seis posibles (volumen aproximado de bruto en cm³: +Z 770 | −Z 232 | +X 329 | −X 350 | +Y 739 | −Y 316).

## Patrón y bruto

- Bruto fundido esperado (sin contraer): 101,7 × 116,4 × 81,5 mm, 224,6 cm³ (≈ 584 g de aluminio).
- Patrón (×1,013): 103,0 × 117,9 × 82,6 mm. El bruto sin contraer es el patrón dividido entre 1,013.
- Sobremetal mínimo comprobado: 3,2 mm en todas las caras (4,5 mm en la cara de partición); salida de 3° en todas las paredes.
- Huecos pasantes rellenados (diámetro equivalente aproximado, mm): 4,5, 4,5, 4,5, 4,5, 4,5, 4,6, 24,0.
- Huecos pasantes conservados: ninguno.
- Verificación: pieza contenida en el bruto, malla cerrada, 0 % de área con contrasalida o con salida insuficiente.

## Mazarotas

- 2 mazarotas cónicas, Ø44 mm en la base y Ø38 mm arriba, 61 mm de alto (`04_mazarota_forma.stl`, imprimir 2 copias). Ubicación: ver M1 a M2 en la planta de `04_comprobacion.png`, centradas sobre la zona más gruesa de la cara plana. Van en la caja superior, sobre la cara de 4,5 mm de sobremetal, así que su huella se mecaniza después.
- Cálculo (módulo de Chvorinov): módulo de la pieza 0,67 cm (0,72 cm descontando la huella de la mazarota); módulo de la mazarota 0,90 cm; relación 1,24 (mayor que 1,2).
- Peso: 210 g por mazarota frente a ≈ 584 g de la pieza en bruto; rendimiento 58 % (sin bebedero).
- Cajas: la superior al menos 86 mm de alto (mazarota más 25 mm de arena) y la inferior al menos 112 mm (bruto de 81,5 mm más 30 mm).
- Colada: lo más simple es verter por una mazarota; si prefieren un bebedero aparte, que entre por la zona alta de la pieza con un canal corto en el plano de partición. Lo decide el taller.

## Observaciones

- Con un patrón de una sola pieza el bruto pesa 2,6 veces la pieza (225 cm³ frente a 87 cm³) y la pared queda profunda: la caja inferior debe tener al menos 112 mm. La alternativa con menos mecanizado es un patrón partido por el plano medio de la pared (dos mitades con guías de alineación); no se hizo porque no es el caso simple de un solo patrón.
- Dos mazarotas: M1 sobre la pared (la zona más gruesa) y M2 sobre la placa circular.
- El hueco central (≈ Ø24 mm) y los 6 agujeros se rellenan y se mecanizan después.
- Los valores son típicos de arena en verde artesanal; la aleación del laboratorio no está certificada y no se simuló la solidificación.

## Archivos

- `04_patron_3grados_x1.013.stl`: patrón listo para imprimir (cara plana sobre la cama, sin soportes).
- `04_mazarota_forma.stl`: forma de la mazarota para imprimir.
- `04_comprobacion.png`: planta y secciones con la pieza final dentro del bruto y la mazarota.
- `04_vistas_patron.png`: vistas del bruto, mapa de relieve y de espesor.
