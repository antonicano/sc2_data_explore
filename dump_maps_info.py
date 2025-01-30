import sc2reader
import pandas as pd
import os
import hashlib

def calcular_id_mapa(nombre_mapa):
    """Genera un ID único basado en el nombre del mapa."""
    return hashlib.md5(nombre_mapa.encode()).hexdigest()

def normalizar_nombre(nombre):
    """Normaliza nombres eliminando espacios extra y convirtiendo a minúsculas."""
    return nombre.strip().lower()

def cargar_mapas_existentes(archivo_csv):
    """Carga los nombres de los mapas ya guardados en el CSV para evitar duplicados."""
    if os.path.exists(archivo_csv):
        try:
            df = pd.read_csv(archivo_csv)
            return set(df["nombre_mapa"].dropna().apply(normalizar_nombre))  # Cargar nombres normalizados
        except Exception as e:
            print(f"Error al cargar {archivo_csv}: {e}")
            return set()
    return set()

def extraer_info_mapa(ruta_replay, archivo_csv, mapas_existentes):
    """Extrae la información del mapa desde una repetición y la guarda en un CSV evitando duplicados."""
    try:
        # Cargar la repetición
        replay = sc2reader.load_replay(ruta_replay, load_level=2)

        # Extraer el nombre del mapa y normalizarlo
        nombre_mapa = replay.map_name.strip() if hasattr(replay, 'map_name') else "Desconocido"
        nombre_mapa_normalizado = normalizar_nombre(nombre_mapa)

        # Si el mapa ya está en la lista de mapas guardados, omitirlo
        if nombre_mapa_normalizado in mapas_existentes:
            print(f"Mapa '{nombre_mapa}' ya registrado. Omitiendo...")
            return

        # Generar un ID único basado en el nombre del mapa
        mapa_id = calcular_id_mapa(nombre_mapa_normalizado)

        # Extraer el creador del mapa (si está disponible)
        creador_mapa = getattr(replay, "map_author", "Desconocido")

        # Extraer la expansión del juego
        expansion = replay.expansion if hasattr(replay, 'expansion') else "Desconocido"

        # Crear un diccionario con los datos del mapa
        datos_mapa = {
            "id_mapa": mapa_id,
            "nombre_mapa": nombre_mapa,
            "creador_mapa": creador_mapa,
            "expansion": expansion,
        }

        # Convertir el diccionario a un DataFrame de pandas
        df = pd.DataFrame([datos_mapa])

        # Guardar en el CSV con manejo de errores
        try:
            df.to_csv(archivo_csv, mode='a', index=False, header=not os.path.exists(archivo_csv))
            print(f"Información guardada: {nombre_mapa}")

            # 🔥 **Actualizar en memoria los mapas existentes** para evitar futuros duplicados
            mapas_existentes.add(nombre_mapa_normalizado)

        except PermissionError:
            print(f"Error: No se puede escribir en {archivo_csv}. Verifica permisos.")

    except Exception as e:
        print(f"Error procesando {ruta_replay}: {e}")

def procesar_todos_los_mapas(directorio_base, archivo_csv):
    """Recorre todas las subcarpetas en `directorio_base` y procesa cada archivo .SC2Replay."""
    # Cargar los nombres de mapas existentes **una sola vez**
    mapas_existentes = cargar_mapas_existentes(archivo_csv)

    for root, _, files in os.walk(directorio_base):
        for file in files:
            if file.endswith(".SC2Replay"):
                ruta_replay = os.path.join(root, file)
                extraer_info_mapa(ruta_replay, archivo_csv, mapas_existentes)

# Ruta base donde se encuentran las carpetas con repeticiones
directorio_replays = "./replays"
archivo_csv = "./csv/info_mapas.csv"

# Procesar todas las repeticiones y extraer info de los mapas
procesar_todos_los_mapas(directorio_replays, archivo_csv)

print("Proceso finalizado.")
