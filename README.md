# HexapodSpider – Innovation Lab UG

Documentación y código del robot araña (hexápodo de 6 patas, 3 servos por pata) controlado desde una Raspberry Pi con una placa PCA9685.

## Estructura

```
.
├── README.md
├── requirements.txt
├── calibracion_servos.example.json   # formato del archivo de calibración
├── spider_control/                   # el programa del robot
│   ├── main.py                       # arranca: neutral -> caminar -> neutral
│   ├── gaits.py                      # marcha trípode, giros, posturas
│   ├── leg.py                        # clase Leg (coxa, fémur, tibia)
│   ├── config.py                     # canales, direcciones I2C, calibración
│   └── pca_manager.py                # acceso a la(s) placa(s) PCA9685
├── tools/
│   └── calibrar_servos.py            # calibración interactiva por consola
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

config.py ──(lee al arrancar)──> ~/calibracion_servos.json
tools/calibrar_servos.py ──(escribe)──> ~/calibracion_servos.json
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
sudo i2cdetect -y 1               # debe aparecer 42
```

## Uso

```bash
source ~/venv/bin/activate

# 1. Calibrar (guarda ~/calibracion_servos.json)
python3 tools/calibrar_servos.py

# 2. Probar el robot (con el cuerpo en el aire la primera vez)
cd spider_control
python3 main.py
```

## Estado actual y pendientes

- **Una sola placa PCA9685 (0x42, 16 canales)**, pero el mapeo usa 18 canales (0-17). Los canales **16 y 17** (fémur y coxa de **R3**) no existen sin una **segunda placa**. Mientras no esté, el programa los ignora con un aviso: **no uses la marcha así**, R3 quedaría con dos servos sin control. Cuando tengas la placa, pon su dirección en `PCA_ADDR_2` (`config.py`) y calibra con `python3 tools/calibrar_servos.py 0x40`.
- Faltan calibrar los canales 13 a 17 (en el JSON de referencia solo había datos hasta el 12).
- Varios neutrales calibrados quedaron en los extremos (0 o 180). La coxa solo se puede mover hacia un lado y el servo puede forzarse contra su tope. Lo correcto es reposicionar el brazo (horn) de esos servos para que la pose de pie quede cerca de 90 y recalibrar.
- La alimentación de los servos debe ser una fuente externa de 5 V con varios amperios, con GND común con la Pi.

Ver `docs/hardware.md` y `docs/calibracion.md` para el detalle.
