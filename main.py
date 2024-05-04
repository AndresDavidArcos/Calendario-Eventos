import requests
from bs4 import BeautifulSoup

def getDataFromUrl(url):
  response = requests.get(url)

  if response.status_code == 200:
    data = []
    soup = BeautifulSoup(response.content, 'html.parser')
    titles = soup.find_all('div', class_='info-element-title')
    descriptions = soup.find_all('div', class_='info-element-description')

    for title, description in zip(titles, descriptions):
        data.append((title.text, description.text))
        
    return data
    
  else:
    print(f"Error: {response.status_code} al obtener la página")
    return []

# Ejemplo de uso
url = "https://www.taqui-co.com/"  # Reemplazar con la URL real
data = getDataFromUrl(url)

if data:
    print("Títulos h2 encontrados:")
    for titles, descriptions in data:
        print("Titulo: ", titles, "\n", "Descripción: ", descriptions, "\n")
else:
    print("No se encontraron títulos h2")