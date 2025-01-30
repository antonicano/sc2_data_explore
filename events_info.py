import sc2reader
import pandas as pd
import os
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
    try:
        # Cargar la repetición
        replay = sc2reader.load_replay(ruta_replay)

        # Calcular el ID único de la repetición
        replay_id = calcular_hash_archivo(ruta_replay)

        # Obtener los jugadores (asumiendo que hay exactamente 2 jugadores)
        jugadores = {player.pid: player.name for player in replay.players if player.is_human}

        # Lista de eventos a guardar (solo si son realizados por los jugadores)
        eventos_permitidos = {
            "CommandEvent", "SelectionEvent", "ControlGroupEvent", "CameraEvent", "HotkeyEvent",
            "UnitBornEvent", "UnitDiedEvent", "UnitDoneEvent", "UnitPositionEvent",
            "PlayerStatsEvent", "UnitAttackEvent", "UnitDamageEvent", "UnitKillEvent",
            "BuildingConstructionStartEvent", "BuildingConstructionCompleteEvent", "UpgradeCompleteEvent",
            "AbilityEvent", "GameStartEvent", "GameEndEvent", "PlayerLeaveEvent", "ChatEvent",
            "TargetPointCommandEvent", "TargetUnitCommandEvent", "TrainUnitEvent", "MorphUnitEvent",
            "ResearchEvent", "AchievementEvent", "CameraSaveEvent", "CameraMoveEvent"
        }

        # Lista para almacenar los eventos filtrados
        eventos_filtrados = []

        # Recorrer todos los eventos de la repetición
        for event in replay.events:
            # Verificar si el evento tiene un jugador y si el evento está en la lista de eventos permitidos
            if event.name in eventos_permitidos and hasattr(event, 'player') and event.player and event.player.pid in jugadores:
                tiempo_evento = timedelta(seconds=event.second)
                horas = tiempo_evento.seconds // 3600
                minutos = (tiempo_evento.seconds % 3600) // 60
                segundos = tiempo_evento.seconds % 60

                nombre_jugador = jugadores[event.player.pid]

                # Extraer datos específicos para algunos eventos
                datos_relevantes = {}

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
                    unidades_seleccionadas = [unit.name for unit in event.new_units] if hasattr(event, 'new_units') else []
                    datos_relevantes = {"unidades_seleccionadas": unidades_seleccionadas}
                elif event.name == "TargetUnitCommandEvent":
                    unidad_objetivo = event.target_unit.name if hasattr(event, 'target_unit') and event.target_unit else "Desconocido"
                    datos_relevantes = {"unidad_objetivo": unidad_objetivo}
                elif event.name == "TargetPointCommandEvent":
                    coordenadas = (event.target.x, event.target.y) if hasattr(event, 'target') and event.target else (None, None)
                    datos_relevantes = {"coordenadas_objetivo": coordenadas}

                # Filtrar eventos que no ocurren en el segundo 0
                if segundos > 0 or minutos > 0 or horas > 0:
                    eventos_filtrados.append({
                        "id_partida": replay_id,
                        "evento": event.name,
                        "jugador": nombre_jugador,
                        "hora": horas,
                        "minuto": minutos,
                        "segundo": segundos,
                        "datos_relevantes": json.dumps(datos_relevantes)
                    })

        # Convertir la lista de eventos a un DataFrame de pandas
        df = pd.DataFrame(eventos_filtrados)

        # Guardar el DataFrame en un archivo CSV
        if not os.path.exists(archivo_csv):
            df.to_csv(archivo_csv, mode='w', index=False)
        else:
            df.to_csv(archivo_csv, mode='a', index=False, header=False)

        print(f"Eventos guardados para {ruta_replay}")

    except Exception as e:
        print(f"Error procesando {ruta_replay}: {e}")

def procesar_todas_las_replays(directorio_base, archivo_csv):
    """Recorre todas las subcarpetas en `directorio_base` y procesa cada archivo .SC2Replay."""
    for root, _, files in os.walk(directorio_base):
        for file in files:
            if file.endswith(".SC2Replay"):
                ruta_replay = os.path.join(root, file)
                guardar_eventos_en_csv(ruta_replay, archivo_csv)

# Ruta base donde se encuentran las carpetas con repeticiones
directorio_replays = "./replays"
archivo_csv = "./csv/eventos_replays.csv"

# Procesar todas las repeticiones
procesar_todas_las_replays(directorio_replays, archivo_csv)

print("Proceso finalizado.")
