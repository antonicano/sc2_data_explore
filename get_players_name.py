from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import pandas as pd
import time

# Configuración de Selenium con Firefox
options = webdriver.FirefoxOptions()
options.add_argument("--headless")  # Ejecutar sin abrir ventana
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Iniciar WebDriver con Firefox
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

# Lista de regiones y sus URLs correspondientes
regions_urls = {
    "Europe": "https://liquipedia.net/starcraft2/Players_(Europe)",
    "US": "https://liquipedia.net/starcraft2/Players_(US)",
    "Asia": "https://liquipedia.net/starcraft2/Players_(Asia)",
    "Korea": "https://liquipedia.net/starcraft2/Players_(Korea)",
}

# Lista para almacenar los datos
players_data = []

# Recorrer cada URL y extraer los nombres de los jugadores
for region, url in regions_urls.items():
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Buscar los nombres de los jugadores
    cells = driver.find_elements(By.CSS_SELECTOR, "span.name")

    # Extraer los nombres y filtrar los vacíos
    players = [cell.text.strip() for cell in cells if cell.text.strip()]
    
    # Guardar los jugadores con su región
    for player in players:
        players_data.append({"Player": player, "Region": region})

# Cerrar el navegador
driver.quit()

# Guardar los datos en un CSV si hay jugadores encontrados
if players_data:
    df = pd.DataFrame(players_data)
    file_path = "./csv/players.csv"
    df.to_csv(file_path, index=False, encoding="utf-8")
    result_message = f"Se han guardado {len(players_data)} jugadores en '{file_path}'."
else:
    result_message = "No se encontraron jugadores para guardar."

# Mostrar el resultado
result_message
