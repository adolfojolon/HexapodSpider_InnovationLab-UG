# HexapodSpider – Innovation Lab UG

Documentación y código del robot araña (hexápodo de 6 patas, 3 servos por pata) controlado desde una Raspberry Pi con dos placas PCA9685.

## Estructura

```
.
├── README.md
├── requirements.txt
├── calibracion_servos.example.json   # formato del archivo de calibración
├── calibracion_servos.json           # TUS ángulos (lo crea el calibrador; no se sube a git)
├── spider_control/                   # el programa del robot
│   ├── main.py                       # arranca: neutral -> caminar -> neutral
│   ├── control.py                    # control interactivo por consola (w/a/s/d)
│   ├── gaits.py                      # marcha trípode, giros, posturas
│   ├── leg.py                        # clase Leg (coxa, fémur, tibia)
│   ├── config.py                     # canales, direcciones I2C, calibración
│   └── pca_manager.py                # acceso a las dos placas PCA9685
├── tools/
│   ├── calibrar_servos.py            # calibración interactiva por consola
│   ├── ver_angulos.py                # muestra los ángulos que usa el robot (sin hardware)
│   └── migrar_calibracion.py         # trae un JSON viejo, conservando solo las 18 claves actuales
└── docs/
    ├── hardware.md                   # placas, direcciones I2C, cableado, canales
    └── calibracion.md                # cómo calibrar y probar las patas
```

## Cómo se conectan los archivos

```
main.py
  ├─ pca_manager.PCAManager ──> config (direcciones, resolve_channel)
  ├─ leg.Leg                ──> config (LEG_CHANNELS, SERVO_CALIBRATION)
  └─ gaits                  ──> config (SERVO_CALIBRATION)

config.py ──(lee al arrancar)──> calibracion_servos.json (raíz del proyecto)
tools/calibrar_servos.py ──(escribe)──> calibracion_servos.json (raíz del proyecto)
```

El robot **no** guarda los ángulos de reposo en el código: los lee del JSON que genera la herramienta de calibración. Si recalibras, basta con volver a ejecutar `main.py`.

## Instalación en la Raspberry Pi

Raspberry Pi OS (Bookworm) protege el Python del sistema, así que se usa un entorno virtual:

```bash
sudo raspi-config                 # Interface Options -> I2C -> habilitar
git clone https://github.com/adolfojolon/HexapodSpider_InnovationLab-UG.git
cd HexapodSpider_InnovationLab-UG
python3 -m venv ~/venv
source ~/venv/bin/activate        # repetir en cada terminal nueva
pip install -r requirements.txt
sudo i2cdetect -y 1               # deben aparecer 40, 42 y 70
```

## Uso

```bash
source ~/venv/bin/activate

# 1. Calibrar (guarda calibracion_servos.json en la raíz del proyecto)
python3 tools/calibrar_servos.py

# 2. Ver los ángulos que usará el robot (no mueve nada)
python3 tools/ver_angulos.py

# 3. Probar el robot (con el cuerpo en el aire la primera vez)
cd spider_control
python3 main.py       # guion fijo: neutral, 2 pasos, neutral
python3 control.py    # interactivo: w/s adelante-atrás, a/d giro, n neutral, p ángulos, q salir
```

## Hardware

Dos placas PCA9685 en el mismo bus I2C:

- **Placa 1, `0x42`**: patas izquierdas L1-L3 (canales 0-8).
- **Placa 2, `0x40`**: patas derechas R1-R3 (canales físicos 0-8, lógicos 16-24).

## Estado y pendientes

- Calibrar los 18 servos con `python3 tools/calibrar_servos.py`. Las patas derechas hay que calibrarlas de nuevo si antes estaban en otros canales.
- Varios neutrales calibrados quedaron en los extremos (0 o 180). La coxa solo se puede mover hacia un lado y el servo puede forzarse contra su tope. Lo correcto es reposicionar el brazo (horn) de esos servos para que la pose de pie quede cerca de 90 y recalibrar.
- La alimentación de los servos debe ser una fuente externa de 5 V con varios amperios, con GND común con la Pi. Con 18 servos, 3 A o más como referencia.
- Suposición a confirmar con el robot: las patas L están en la placa 1 y las R en la 2, con `invert` solo en las R. Si una pata sube o avanza al revés, es lo primero que hay que revisar.

Ver `docs/hardware.md` y `docs/calibracion.md` para el detalle.
