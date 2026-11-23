"""Trae al proyecto una calibracion vieja, quedandose solo con lo que se usa.

Del JSON viejo conserva unicamente las 18 claves del montaje actual:
    h:0 .. h:8     (patas izquierdas, placa 1)
    h2:0 .. h2:8   (patas derechas,   placa 2)
y descarta el resto (canales del Tessel, canales 9-15, etc.). No modifica ni
borra el archivo viejo.

Uso:
    python3 tools/migrar_calibracion.py                      # lee ~/calibracion_servos.json
    python3 tools/migrar_calibracion.py ruta/al/viejo.json
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "calibracion_servos.json")
ORIGEN = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/calibracion_servos.json")

VALIDAS = [f"h:{i}" for i in range(9)] + [f"h2:{i}" for i in range(9)]

if not os.path.exists(ORIGEN):
    sys.exit(f"No encontre {ORIGEN}")
if os.path.exists(DESTINO):
    sys.exit(f"Ya existe {DESTINO}; no lo sobrescribo. Borralo o renombralo si quieres migrar de nuevo.")

with open(ORIGEN) as f:
    viejo = json.load(f)

nuevo = {k: viejo[k] for k in VALIDAS if k in viejo}
descartadas = sorted(set(viejo) - set(nuevo))

with open(DESTINO, "w") as f:
    json.dump(nuevo, f, indent=2)

print(f"Origen : {ORIGEN} ({len(viejo)} claves)")
print(f"Destino: {DESTINO} ({len(nuevo)} claves)")
print(f"Descartadas ({len(descartadas)}): {', '.join(descartadas) or 'ninguna'}")
faltan = [k for k in VALIDAS if k not in nuevo]
print(f"Faltan por calibrar ({len(faltan)}): {', '.join(faltan) or 'ninguna'}")
