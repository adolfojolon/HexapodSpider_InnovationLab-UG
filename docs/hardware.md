# Hardware

## Placas e I2C

| Dirección | Dispositivo | Nota |
|---|---|---|
| `0x42` | Placa 1 (HAT de servos) | Jumper **A1** soldado (0x40 + 0x02). Patas **izquierdas**. |
| `0x40` | Placa 2 (PCA9685 genérica) | Sin jumpers (dirección de fábrica). Patas **derechas**. |
| `0x70` | All-call del PCA9685 | Normal, aparece siempre y se ignora. |

El Rainbow HAT ya no se usa (su sensor ocupaba `0x77` y su display `0x70`).

La dirección de una PCA9685 se cambia soldando los puentes A0-A5: cada uno suma `0x01, 0x02, 0x04, 0x08, 0x10, 0x20` a la base `0x40`.

Comprobar el bus (debe mostrar `40`, `42` y `70`):

```bash
sudo i2cdetect -y 1
```

## Mapeo de canales

Cada pata usa 3 canales seguidos, en el orden **tibia, fémur, coxa**. Cada placa maneja 3 patas con sus canales **físicos 0-8**.

| Pata | Placa | Tibia | Fémur | Coxa |
|---|---|---|---|---|
| L1 | 1 (0x42) | 0 | 1 | 2 |
| L2 | 1 (0x42) | 3 | 4 | 5 |
| L3 | 1 (0x42) | 6 | 7 | 8 |
| R1 | 2 (0x40) | 0 | 1 | 2 |
| R2 | 2 (0x40) | 3 | 4 | 5 |
| R3 | 2 (0x40) | 6 | 7 | 8 |

En el código y en el calibrador, los canales de la placa 2 se numeran como **lógicos 16-24** (físico + 16). En `~/calibracion_servos.json` se guardan como `h:<canal>` (placa 1) y `h2:<canal físico>` (placa 2).

> Las patas R tienen `invert: True` en la calibración (el espejo mecánico del lado derecho lo resuelve el código).

Los grupos del paso trípode son `A = L1, L3, R2` y `B = L2, R1, R3`.

## Alimentación

- Los servos se alimentan con una **fuente externa de 5 V**, no desde la Pi. Con 18 servos conviene una fuente de **3 A o más** (depende de los servos).
- Cada placa necesita su alimentación de 5 V en el borne de servos. GND común entre la fuente, las dos placas y la Pi.
- Si los servos tiemblan, se mueven a tirones o la Pi se reinicia, casi siempre es la fuente.

## Apendice: módulo Tessel servo-pca9685 (descartado)

Se probó el módulo oficial de Tessel como segunda placa y se descartó. Lo aprendido, por si se retoma:

- El módulo **no** es un PCA9685 genérico. Según el driver oficial (`tessel/servo-pca9685`, `index.js`):
  - `G3` es la entrada **OE** (output enable) y debe ir a **GND**; si queda flotando o en alto, las salidas no se mueven aunque el I2C responda.
  - `G2` y `G1` fijan bits de dirección sobre la base `0x73`: G2 suma 4 y G1 suma 8 → `0x73`, `0x77`, `0x7B` o `0x7F`.
- Con G2 en alto y G1 en GND la dirección es `0x77`, que **choca con el sensor del Rainbow HAT**. Durante las pruebas el `0x77` del escaneo probablemente nunca fue el Tessel.
- Conectando G1 y G2 a 3v3 debería quedar en `0x7F`.
- El cableado mínimo era `3v3, gnd, sda, scl, G3→GND, G1/G2→3v3`, más 5 V externos en el jack barril.
