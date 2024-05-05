import locale
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode

app = Flask(__name__)

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def parse_date(date_str):
    date_obj = datetime.strptime(date_str, '%B %d, %Y')
    iso_date_str = date_obj.isoformat()
    return iso_date_str

def scrape_taqui(url):
    response = requests.get(url)

    if response.status_code == 200:
        data = []
        soup = BeautifulSoup(response.content, "html.parser")
        titles = soup.find_all("div", class_="info-element-title")
        descriptions = soup.find_all("div", class_="info-element-description")

        for title, description in zip(titles, descriptions):
            description = description.text
            parts = description.split(": ")
            city = parts[2].split(" ")[0]

            if city == "Cali":
                date = parts[3].split(" Lugar")[0].split(" ", 1)[1]
                date = date.replace(" de", "").replace(" Del", "")
                date = date.split(" ")

                try:
                    date = date[0] + " " + date[1] + " " + date[2]
                    date = datetime.strptime(date, "%d %B %Y").isoformat()

                    place = parts[4].split(" Hora")[0]
                    data.append({
                        'title': title.text,
                        'description': 'No posee descripcion',
                        'date': date,
                        'place': place
                    })
                except Exception as e:
                    continue

        return data

    else:
        print(f"Error: {response.status_code} al obtener la página")
        return []

def scrape_teatro_calima(url):
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

        components = date_time.split(', ')[1].split(' de ')
        day = components[0]
        month = components[1]
        year = components[2].split()[0]
        time = components[2].split()[1]

        iso_date = datetime.strptime(f'{year}-{month}-{day} {time}', '%Y-%B-%d %H:%M').strftime('%Y-%m-%dT%H:%M')
        place = event_soup.find('div', class_='font18 boldear600').text.strip()

        events.append({
            'title': title,
            'description': 'No posee descripción',
            'date': iso_date,
            'place': place
        })

    return events

@app.route('/scrape_all')
def scrape_all():
    taqui_data = scrape_taqui("https://www.taqui-co.com/")
    teatro_calima_data = scrape_teatro_calima("https://teatrocalima.com.co/inicio/entretenimiento/#page-content")
    eticket_data = scrape_eticket('https://www.eticket.co/eventos.aspx?idciudad=160')

    all_data = taqui_data + teatro_calima_data + eticket_data

    return jsonify(all_data)

if __name__ == '__main__':
    app.run(debug=True)
