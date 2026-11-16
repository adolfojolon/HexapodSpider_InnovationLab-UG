# Hardware

## Placas e I2C

| Dirección | Dispositivo | Nota |
|---|---|---|
| `0x42` | HAT de servos PCA9685 | Jumper **A1** soldado (0x40 + 0x02). 16 canales. |
| `0x70` | All-call del PCA9685 / display del Rainbow HAT | Normal, se ignora. |
| `0x77` | Sensor BMP280 del Rainbow HAT (probable) | **No usar** para una placa de servos: choca. |
| `0x40` | Sugerida para una 2.ª PCA9685 genérica | No choca con las anteriores. |

La dirección de una PCA9685 genérica se cambia soldando los puentes A0-A5: cada uno suma `0x01, 0x02, 0x04, 0x08, 0x10, 0x20` a la base `0x40`.

Comprobar el bus:

```bash
sudo i2cdetect -y 1
```

## Mapeo de canales

Cada pata usa 3 canales seguidos, en el orden **tibia, fémur, coxa**.

| Pata | Tibia | Fémur | Coxa |
|---|---|---|---|
| L1 | 0 | 1 | 2 |
| L2 | 3 | 4 | 5 |
| L3 | 6 | 7 | 8 |
| R1 | 9 | 10 | 11 |
| R2 | 12 | 13 | 14 |
| R3 | 15 | 16* | 17* |

\* Los canales 16 y 17 requieren una **segunda placa PCA9685**.

> Suposición: los canales 0-8 son las patas **izquierdas** (L1-L3). Las patas R tienen `invert: True` en la calibración; si el montaje real es el contrario, hay que corregirlo en `config.py`.

Los grupos del paso trípode son `A = L1, L3, R2` y `B = L2, R1, R3`.

## Alimentación

- Los servos se alimentan con una **fuente externa de 5 V**, no desde la Pi. Con 18 servos conviene una fuente de **3 A o más** (depende de los servos).
- GND común entre la fuente, la placa PCA9685 y la Pi.
- Si los servos tiemblan, se mueven a tirones o la Pi se reinicia, casi siempre es la fuente.

## Apendice: módulo Tessel servo-pca9685 (descartado)

Se probó el módulo oficial de Tessel como segunda placa y se descartó. Lo aprendido, por si se retoma:

- El módulo **no** es un PCA9685 genérico. Según el driver oficial (`tessel/servo-pca9685`, `index.js`):
  - `G3` es la entrada **OE** (output enable) y debe ir a **GND**; si queda flotando o en alto, las salidas no se mueven aunque el I2C responda.
  - `G2` y `G1` fijan bits de dirección sobre la base `0x73`: G2 suma 4 y G1 suma 8 → `0x73`, `0x77`, `0x7B` o `0x7F`.
- Con G2 en alto y G1 en GND la dirección es `0x77`, que **choca con el sensor del Rainbow HAT**. Durante las pruebas el `0x77` del escaneo probablemente nunca fue el Tessel.
- Conectando G1 y G2 a 3v3 debería quedar en `0x7F`.
- El cableado mínimo era `3v3, gnd, sda, scl, G3→GND, G1/G2→3v3`, más 5 V externos en el jack barril.
