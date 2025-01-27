import sc2reader
import pandas as pd
from datetime import datetime
import hashlib

def calcular_hash_archivo(ruta):
    """Calcula el hash MD5 de un archivo para usarlo como ID único."""
    hasher = hashlib.md5()
    with open(ruta, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def calcular_apm(replay, player):
    """Calcula las APM (acciones por minuto) de un jugador."""
    game_duration_minutes = replay.game_length.seconds / 60
    
    # Filtrar eventos que son acciones del jugador
    actions = [
        event for event in replay.events
        if getattr(event, 'player', None) == player and hasattr(event, 'is_action') and event.is_action
    ]
    
    return len(actions) / game_duration_minutes if game_duration_minutes > 0 else 0

def guardar_datos_replay_en_csv(ruta_replay, archivo_csv):
    """Extrae datos de una repetición y los guarda en un archivo CSV."""
    # Cargar la repetición
    replay = sc2reader.load_replay(ruta_replay)

    # Calcular el ID único de la repetición
    replay_id = calcular_hash_archivo(ruta_replay)

    # Obtener los jugadores (asumiendo que hay exactamente 2 jugadores)
    if len(replay.players) != 2:
        raise ValueError("La repetición debe tener exactamente 2 jugadores.")
    jugador1, jugador2 = replay.players

    # Obtener el ganador
    ganador = jugador1.name if jugador1.result == "Win" else jugador2.name

    # Obtener la duración de la partida
    duracion = replay.game_length.seconds

    # Obtener la hora de inicio y fin
    hora_inicio = datetime.fromtimestamp(replay.unix_timestamp).strftime('%H:%M:%S')
    hora_fin = (datetime.fromtimestamp(replay.unix_timestamp) + replay.game_length).strftime('%H:%M:%S')

    # Obtener la fecha
    fecha = datetime.fromtimestamp(replay.unix_timestamp).strftime('%Y-%m-%d')

    # Obtener la expansión del juego
    expansion = replay.expansion

    # Obtener la región
    region = replay.region

    # Calcular las APM de cada jugador
    apm_jugador1 = calcular_apm(replay, jugador1)
    apm_jugador2 = calcular_apm(replay, jugador2)

    # Crear un diccionario con los datos
    datos = {
        "id": [replay_id],
        "jugador1": [jugador1.name],
        "jugador2": [jugador2.name],
        "ganador": [ganador],
        "duracion_segundos": [duracion],
        "hora_inicio": [hora_inicio],
        "hora_fin": [hora_fin],
        "fecha": [fecha],
        "expansion": [expansion],
        "region": [region],
        "apm_jugador1": [apm_jugador1],
        "apm_jugador2": [apm_jugador2]
    }

    # Convertir el diccionario a un DataFrame de pandas
    df = pd.DataFrame(datos)

    # Guardar el DataFrame en un archivo CSV
    df.to_csv(archivo_csv, mode='a', index=False, header=not pd.io.common.file_exists(archivo_csv))

# Ejemplo de uso
replay_name = "16 pool.SC2Replay"
ruta_replay = "./replays/"+replay_name
archivo_csv = "./csv/datos_replays.csv"
guardar_datos_replay_en_csv(ruta_replay, archivo_csv)