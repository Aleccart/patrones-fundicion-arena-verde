# Patrón 05: Tapa 1 del nuevo contenedor

13 de octubre de 2026. Estado: **preliminar** (por confirmar con el taller). Fundición en arena en verde, aluminio ≈ 7 % Si.

## Reglas fijas (decididas por el equipo, valen para todas las piezas)

- Salida de 3° en todas las paredes.
- Se mecanizan todas las caras: sobremetal mínimo de 3 mm, y 4,5 mm en la cara de partición (queda arriba en el molde).
- Sin perforaciones ni machos: los agujeros y huecos menores de 24 mm se rellenan en el patrón y se mecanizan después; los huecos grandes pasantes en la dirección de extracción se dejan como islas de arena formadas por el propio patrón.
- Contracción 1,3 % (escala ×1,013).
- Radios mínimos de 3 mm en las aristas convexas y los rincones.

## Pieza de partida

Archivo `Tapa 1 del nuevo contenedor.STEP`. Tapa circular de Ø98 mm y 22 mm de alto, con un borde (aro) y un fondo delgado con 5 agujeros de ≈ Ø3,5 mm.

- Caja envolvente: 98,0 × 98,0 × 22,0 mm. Volumen 88,0 cm³ (≈ 229 g en aluminio).

## Orientación y partición

- La cara plana del patrón (plano de partición) corresponde a la cara de Z mínimo del STEP (Z = 0,0 mm). Esa cara queda arriba en el molde, y el resto de la pieza cuelga dentro de la caja inferior.
- Patrón de una sola pieza, plano de partición plano, sin machos. La orientación se eligió automáticamente como la de menor volumen de bruto entre las seis posibles (volumen aproximado de bruto en cm³: +Z 207 | −Z 271 | +X 347 | −X 347 | +Y 347 | −Y 347).

## Patrón y bruto

- Bruto fundido esperado (sin contraer): 107,8 × 107,8 × 30,1 mm, 200,4 cm³ (≈ 521 g de aluminio).
- Patrón (×1,013): 109,2 × 109,2 × 30,4 mm. El bruto sin contraer es el patrón dividido entre 1,013.
- Sobremetal mínimo comprobado: 3,2 mm en todas las caras (4,5 mm en la cara de partición); salida de 3° en todas las paredes.
- Huecos pasantes rellenados (diámetro equivalente aproximado, mm): 3,5, 3,5, 3,5, 3,6, 3,6.
- Huecos pasantes conservados: ninguno.
- Verificación: pieza contenida en el bruto, malla cerrada, 0 % de área con contrasalida o con salida insuficiente.

## Mazarotas

- 2 mazarotas cónicas, Ø45 mm en la base y Ø38 mm arriba, 62 mm de alto (`05_mazarota_forma.stl`, imprimir 2 copias). Ubicación: ver M1 a M2 en la planta de `05_comprobacion.png`, centradas sobre la zona más gruesa de la cara plana. Van en la caja superior, sobre la cara de 4,5 mm de sobremetal, así que su huella se mecaniza después.
- Cálculo (módulo de Chvorinov): módulo de la pieza 0,67 cm (0,73 cm descontando la huella de la mazarota); módulo de la mazarota 0,91 cm; relación 1,25 (mayor que 1,2).
- Peso: 219 g por mazarota frente a ≈ 521 g de la pieza en bruto; rendimiento 54 % (sin bebedero).
- Cajas: la superior al menos 87 mm de alto (mazarota más 25 mm de arena) y la inferior al menos 60 mm (bruto de 30,0 mm más 30 mm).
- Colada: lo más simple es verter por una mazarota; si prefieren un bebedero aparte, que entre por la zona alta de la pieza con un canal corto en el plano de partición. Lo decide el taller.

## Observaciones

- El interior de la tapa queda abierto hacia la caja inferior: la arena lo forma sola (isla de ≈ 78 mm de diámetro y ≈ 14 mm de alto), sin macho. Los 5 agujeros del fondo se rellenan.
- Dos mazarotas sobre el aro (M1 y M2), que es la zona más gruesa.
- Los valores son típicos de arena en verde artesanal; la aleación del laboratorio no está certificada y no se simuló la solidificación.

## Archivos

- `05_patron_3grados_x1.013.stl`: patrón listo para imprimir (cara plana sobre la cama, sin soportes).
- `05_mazarota_forma.stl`: forma de la mazarota para imprimir.
- `05_comprobacion.png`: planta y secciones con la pieza final dentro del bruto y la mazarota.
- `05_vistas_patron.png`: vistas del bruto, mapa de relieve y de espesor.
