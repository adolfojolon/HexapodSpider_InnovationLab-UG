# Calibración

## Qué es el neutral

Es el ángulo de cada servo en la **postura de pie**. Se guarda en `calibracion_servos.json`, en la raíz del proyecto (junto a `spider_control/` y `tools/`), con claves `"h:<canal>"` (placa 1, 0x42, patas izquierdas) y `"h2:<canal físico>"` (placa 2, 0x40, patas derechas).

El JSON guarda el ángulo **físico** que recibe el servo. En las patas derechas el código lo invierte (`180 - ángulo`), así que `config.py` convierte solo; no hay que hacerlo a mano.

## Procedimiento

1. Con el brazo (horn) **sin atornillar**, manda el servo a 90° (el centro). Atornilla el brazo en la posición que quieras como neutral.
2. Corre `python3 tools/calibrar_servos.py` y elige el canal: **0-8** para las patas izquierdas y **16-24** para las derechas (el programa muestra a qué pata y articulación corresponde cada uno). Escribe un ángulo (0-180) para moverlo en vivo y `g` para guardarlo. Comandos: `o` apaga el canal, `s` salta, `q` sale.
3. Calibra con el robot **en el aire**; luego bájalo a una superficie plana.
4. Marca con plumón la posición del horn respecto al servo para poder recolocarlo igual.

## Cómo saber si quedó bien

- Las 6 patas tocan el piso al mismo tiempo.
- El cuerpo queda horizontal (nivel de burbuja).
- Prueba del papel: una tira debe resistirse de forma parecida bajo cada pata.
- Cada pata es reflejo de su pareja del lado opuesto.
- Al empujar el cuerpo hacia abajo, las 6 patas resisten por igual.
- Al caminar unos pasos, avanza derecho.

## Marcha

Marcha trípode: dos grupos de 3 patas (`A = L1, L3, R2`, `B = L2, R1, R3`) que se alternan; mientras un grupo está en el aire, el otro sostiene y empuja.

Todos los ángulos de la marcha son relativos al neutral de cada pata. Los parámetros están al inicio de `spider_control/gaits.py`:

| Parámetro | Efecto |
|---|---|
| `COXA_SWING` | Largo del paso (20° es conservador). |
| `FEMUR_LIFT_DELTA`, `TIBIA_LIFT_DELTA` | Cuánto se levanta la pata. Si arrastra, súbelos en valor absoluto. |
| `DEFAULT_MICRO_DELAY` | Velocidad: más alto = más lento (0.06 s con incremento de 1°). |
| `DEFAULT_PAUSE` | Pausa entre medios pasos. |

El movimiento está sincronizado: todas las articulaciones de un movimiento salen y llegan juntas, con arranque y frenado suaves.

## Problemas conocidos

- **Neutrales en los extremos (0 o 180):** la coxa solo puede moverse hacia un lado y el servo puede zumbar contra su tope. Reposiciona el horn para quedar cerca de 90 y recalibra.
- **Una pata sube al revés:** suele ser un `invert` mal puesto en esa pata o un servo montado en espejo.
- **Una pata cede lento al apagar:** los servos no tienen freno; sin señal PWM el peso del cuerpo los vence. Es normal. Baja el cuerpo a una postura estable antes de apagar.
- `release_all()` quita la señal de todos los canales al terminar `main.py`: las patas quedan sin fuerza.
