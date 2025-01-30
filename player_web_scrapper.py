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
options.add_argument("--headless")  # Ejecutar sin abrir ventana (puedes comentarlo si quieres ver el navegador)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Iniciar WebDriver con Firefox
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

# URL del perfil de Serral
url = "https://liquipedia.net/starcraft2/Serral"
driver.get(url)

# Esperar a que la página cargue
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fo-nttax-infobox-wrapper")))

# Inicializar diccionario con datos
data = {
    "Nick": "",
    "Name": "",
    "Raza": "",
    "Fecha de nacimiento": "",
    "Sexo": "",
    "País": "",
    "Ganancias totales": "",
    "Equipo": "",
    "Estado": "",
    "Servicio militar": "",
    "1er Puestos": 0,
    "2do Puestos": 0,
    "3er Puestos": 0,
}

#Busca el nick del jugador
try:
    nick = driver.find_element(By.CSS_SELECTOR, "div.infobox-header").text
    data["Nick"] = nick
except:
    data["Nick"] = "Desconocido"

cells = driver.find_elements(By.CSS_SELECTOR, "div.infobox-cell-2")

# Recorrer cada celda y buscar su div hermano en el mismo nivel
for cell in cells:
    try:
        # Buscar el div hermano anterior (usando XPath)
        sibling = cell.find_element(By.XPATH, "following-sibling::div")
        
        # Mostrar los datos extraídos
        if cell.text.strip() == 'Name:':
            data["Name"] = sibling.text.strip()
            
        elif cell.text.strip() == 'Nationality:':
            data["País"] = sibling.text.strip()
            
        elif cell.text.strip() == 'Born:':
            data["Fecha de nacimiento"] = sibling.text.strip()
            
        elif cell.text.strip() == 'Race:':
            data["Raza"] = sibling.text.strip()
            
        elif cell.text.strip() == 'Team:':
            data["Equipo"] = sibling.text.strip()
            
        elif cell.text.strip() == 'Approx. Total Winnings:':
            data["Ganancias totales"] = sibling.text.strip()
            
        elif cell.text.strip() == 'Military Service:':
            data["Servicio militar"] = sibling.text.strip()
            
        elif cell.text.strip() == 'Years Active:':
            data["Estado"] = sibling.text.strip()
            
        
    except:
        continue  # Si no hay un hermano, ignorar
    
placement_1_results = driver.find_elements(By.CSS_SELECTOR, "td.placement-1")
placement_2_results = driver.find_elements(By.CSS_SELECTOR, "td.placement-2")
placement_3_results = driver.find_elements(By.CSS_SELECTOR, "td.placement-3")

data["1er Puestos"] = len(placement_1_results)
data["2do Puestos"] = len(placement_2_results)
data["3er Puestos"] = len(placement_3_results)


# Cerrar Selenium
driver.quit()

# Guardar en CSV
df = pd.DataFrame([data])
df.to_csv("serral_stats_firefox.csv", index=False, encoding="utf-8")

print("Datos extraídos y guardados en 'serral_stats_firefox.csv'")
