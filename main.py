import json
import locale
from datetime import datetime
from unidecode import unidecode
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

# # Ejemplo de uso
# url = "https://www.taqui-co.com/"  # Reemplazar con la URL real
# data = getDataFromUrl(url)
#
# if data:
#     print("Títulos h2 encontrados:")
#     for titles, descriptions in data:
#         print("Titulo: ", titles, "\n", "Descripción: ", descriptions, "\n")
# else:
#     print("No se encontraron títulos h2")

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def parse_date(date_str):
    date_obj = datetime.strptime(date_str, '%B %d, %Y')
    iso_date_str = date_obj.isoformat()
    return iso_date_str

def scrape_posts(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    posts = []

    for post in soup.find_all('div', class_='post-list-item'):
        post_data = {}

        title = post.find('h3', class_='post-title').text.strip()
        post_data['title'] = title

        description = post.find('div', class_='post-excerpt').text.strip()
        post_data['description'] = description

        date_element = post.find('i', title='Hora de la entrada')
        if date_element:
            date_str = date_element.find_next_sibling('span', class_='post-footer-value').text.strip()
            iso_date_str = parse_date(date_str)
            post_data['date'] = iso_date_str

        post_data['place'] = "Teatro Calima"
        posts.append(post_data)

    return posts

# url = "https://teatrocalima.com.co/inicio/entretenimiento/#page-content"
# posts = scrape_posts(url)
#
# posts_json = json.dumps(posts, indent=4, ensure_ascii=False)
# print(posts_json)

def scrape_eticket(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    events = []

    for event_link in soup.find_all('a', class_='URLCOMPRA botonevento'):
        event_url = 'https://www.eticket.co/' + event_link['href']
        event_response = requests.get(event_url)
        event_soup = BeautifulSoup(event_response.content, 'html.parser')

        title = event_soup.find('div', class_='font22 boldear800').text.strip()
        date_time = unidecode(event_soup.find('div', class_='font16 boldear600 borde_artista mayusculas_primera').text.strip())
        print(date_time)

        components = date_time.split(', ')[1].split(' de ')
        day = components[0]
        month = components[1]
        year = components[2].split()[0]
        time = components[2].split()[1]


        # Convertir a formato ISO 8601
        iso_date = datetime.strptime(f'{year}-{month}-{day} {time}', '%Y-%B-%d %H:%M').strftime('%Y-%m-%dT%H:%M')
        place = event_soup.find('div', class_='font18 boldear600').text.strip()

        events.append({
            'title': title,
            'description': 'No posee descripción',
            'date': iso_date,
            'place': place
        })

    return events

# Prueba de la función
url = 'https://www.eticket.co/eventos.aspx?idciudad=160'
events_data = scrape_eticket(url)
for event in events_data:
    print(event)