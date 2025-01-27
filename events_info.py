import sc2reader
import pandas as pd
from datetime import timedelta
import hashlib
import json

def calcular_hash_archivo(ruta):
    """Calcula el hash MD5 de un archivo para usarlo como ID único."""
    hasher = hashlib.md5()
    with open(ruta, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def guardar_eventos_en_csv(ruta_replay, archivo_csv):
    """Extrae eventos específicos de una repetición y los guarda en un archivo CSV."""
    # Cargar la repetición
    replay = sc2reader.load_replay(ruta_replay)

    # Calcular el ID único de la repetición
    replay_id = calcular_hash_archivo(ruta_replay)

    # Lista de tipos de eventos que queremos guardar
    eventos_permitidos = {
        # Eventos de jugador (acciones)
        "CommandEvent",
        "SelectionEvent",
        "ControlGroupEvent",
        "CameraEvent",
        "HotkeyEvent",
        # Eventos de unidades
        "UnitBornEvent",
        "UnitDiedEvent",
        "UnitDoneEvent",
        "UnitPositionEvent",
        # Eventos de economía
        "PlayerStatsEvent",
        # Eventos de combate
        "UnitAttackEvent",
        "UnitDamageEvent",
        "UnitKillEvent",
        # Eventos de construcción
        "BuildingConstructionStartEvent",
        "BuildingConstructionCompleteEvent",
        "UpgradeCompleteEvent",
        # Eventos de habilidades
        "AbilityEvent",
        # Eventos de juego
        "GameStartEvent",
        "GameEndEvent",
        "PlayerLeaveEvent",
        # Eventos de chat
        "ChatEvent",
        # Eventos de objetivos
        "TargetPointCommandEvent",
        "TargetUnitCommandEvent",
        # Eventos de logística
        "TrainUnitEvent",
        "MorphUnitEvent",
        # Eventos de tecnología
        "ResearchEvent",
        # Eventos de logros
        "AchievementEvent",
        # Eventos de cámara
        "CameraSaveEvent",
        "CameraMoveEvent",
    }

    # Lista para almacenar los eventos filtrados
    eventos_filtrados = []

    # Recorrer todos los eventos de la repetición
    for event in replay.events:
        # Verificar si el evento es de un tipo permitido
        if event.name in eventos_permitidos:
            # Calcular el tiempo del evento en horas, minutos y segundos
            tiempo_evento = timedelta(seconds=event.second)
            horas = tiempo_evento.seconds // 3600
            minutos = (tiempo_evento.seconds % 3600) // 60
            segundos = tiempo_evento.seconds % 60

            # Obtener el jugador asociado al evento (si existe)
            jugador = getattr(event, 'player', None)
            nombre_jugador = jugador.name if jugador else "Sistema"

            # Inicializar datos relevantes
            datos_relevantes = {}

            # Extraer datos relevantes según el tipo de evento
            if event.name == "PlayerStatsEvent":
                datos_relevantes = {
                    "minerales_recolectados": event.minerals_current,
                    "gas_recolectado": event.vespene_current,
                    "poblacion_actual": event.food_used,
                }
            elif event.name == "UnitDiedEvent":
                datos_relevantes = {
                    "unidad_muerta": event.unit.name if hasattr(event, 'unit') and event.unit else "Desconocido",
                }
            elif event.name == "UnitBornEvent":
                datos_relevantes = {
                    "unidad_nacida": event.unit.name if hasattr(event, 'unit') and event.unit else "Desconocido",
                }
            elif event.name == "SelectionEvent":
                # Extraer nombres de las unidades seleccionadas
                unidades_seleccionadas = [unit.name for unit in event.new_units] if hasattr(event, 'new_units') else []
                datos_relevantes = {
                    "unidades_seleccionadas": unidades_seleccionadas,
                }
            elif event.name == "TargetUnitCommandEvent":
                # Extraer la unidad objetivo del comando (si existe)
                if hasattr(event, 'target_unit') and event.target_unit:
                    unidad_objetivo = event.target_unit.name
                else:
                    unidad_objetivo = "Desconocido"
                datos_relevantes = {
                    "unidad_objetivo": unidad_objetivo,
                }
            elif event.name == "TargetPointCommandEvent":
                # Extraer las coordenadas del punto objetivo (si existen)
                if hasattr(event, 'target') and event.target:
                    coordenadas = (event.target.x, event.target.y)
                else:
                    coordenadas = (None, None)
                datos_relevantes = {
                    "coordenadas_objetivo": coordenadas,
                }

            # Filtrar eventos que no ocurren en el segundo 0
            if segundos > 0 or minutos > 0 or horas > 0:
                # Guardar los detalles del evento
                eventos_filtrados.append({
                    "id_partida": replay_id,
                    "evento": event.name,
                    "jugador": nombre_jugador,
                    "hora": horas,
                    "minuto": minutos,
                    "segundo": segundos,
                    "datos_relevantes": json.dumps(datos_relevantes)  # Convertir a JSON
                })

    # Convertir la lista de eventos a un DataFrame de pandas
    df = pd.DataFrame(eventos_filtrados)

    # Guardar el DataFrame en un archivo CSV
    df.to_csv(archivo_csv, mode='a', index=False, header=not pd.io.common.file_exists(archivo_csv))

# Ejemplo de uso
replay_name = "16 pool.SC2Replay"
ruta_replay = "./replays/"+replay_name
archivo_csv = "./csv/eventos_replays.csv"
guardar_eventos_en_csv(ruta_replay, archivo_csv)