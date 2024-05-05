import requests
from bs4 import BeautifulSoup
from datetime import datetime


def getDataFromUrl(url):
    response = requests.get(url)

    if response.status_code == 200:
        data = []
        soup = BeautifulSoup(response.content, "html.parser")
        titles = soup.find_all("div", class_="info-element-title")
        descriptions = soup.find_all("div", class_="info-element-description")

        months = {
            "enero": "January",
            "febrero": "February",
            "marzo": "March",
            "abril": "April",
            "mayo": "May",
            "junio": "June",
            "julio": "July",
            "agosto": "August",
            "septiembre": "September",
            "octubre": "October",
            "noviembre": "November",
            "diciembre": "December",
        }

        for title, description in zip(titles, descriptions):
            description = description.text
            parts = description.split(": ")
            city = parts[2].split(" ")[0]

            if city == "Cali":
                date = parts[3].split(" Lugar")[0].split(" ", 1)[1]

                date = date.replace(" de", "").replace(" Del", "")

                date = date.split(" ")

                try:
                    date = date[0] + " " + months[date[1].lower()] + " " + date[2]

                    date = datetime.strptime(date, "%d %B %Y")
                    date = datetime.isoformat(date)

                    place = parts[4].split(" Hora")[0]
                    data.append((title.text, city, date, place))
                except Exception as e:
                    continue

        return data

    else:
        print(f"Error: {response.status_code} al obtener la página")
        return []


# Ejemplo de uso
url = "https://www.taqui-co.com/"  # Reemplazar con la URL real
data = getDataFromUrl(url)

if data:
    for title, city, date, place in data:
        print(f"Titulo: {title}")
        print(f"Ciudad: {city}")
        print(f"Fecha: {date}")
        print(f"Lugar: {place}")
        print("-" * 30)
else:
    print("No se encontraron eventos")
