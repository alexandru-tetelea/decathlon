import paho.mqtt.client as mqtt
import requests
from bs4 import BeautifulSoup

URLS = [
    {
        "name": "Rockrider 540 M",
        "model": "2379152",
        "id": "rockride_540_M_barbati",
        "url": "https://www.decathlon.ro/bicicleta-mtb-st-540-275--id_8500757.html"
    }, {
        "name": "Rockrider 540 Dame",
        "id": "rockride_540_M_dame",
        "model": "2752986",
        "url": "https://www.decathlon.ro/bicicleta-mtb-st-540-275--id_8553362.html"
    }, {
        "name": "Rockrider 530 M Barbati",
        "id": "rockride_530_M_barbati",
        "model": "4010890",
        "url": "https://www.decathlon.ro/bicicleta-mtb-st-530-275-id_8582845.html"
    }
]

magazine_url = [
    {
        "name": "Rockrider 540 M",
        "model": "2379152",
        "id": "rockride_540_M_barbati",
        "city": "Iasi",
        "url": "https://www.decathlon.ro/ro/ChooseStore_getStoresWithAvailability?storeFullId=0070063100631&productId=2379152&_=1596317401483"
    }, {
        "name": "Rockrider 540 Dame",
        "model": "2752986",
        "id": "rockride_540_M_dame",
        "city": "Piatra",
        "url": "https://www.decathlon.ro/ro/ChooseStore_getStoresWithAvailability?storeFullId=0070201802018&productId=2752986&_=1596292968034"
    }, {
        "name": "Rockrider 540 Dame",
        "model": "2752986",
        "id": "rockride_540_M_dame",
        "city": "Iasi",
        "url": "https://www.decathlon.ro/ro/ChooseStore_getStoresWithAvailability?storeFullId=0070063100631&productId=2752986&_=1596292968043"
    }, {
        "name": "Rockrider 530 M Barbati",
        "id": "rockride_530_M_barbati",
        "model": "4010890",
        "url": "https://www.decathlon.ro/ro/ChooseStore_getStoresWithAvailability?storeFullId=0070063100631&productId=4010890&_=1596317494320"
    }
]

VALID_STATUSES = ["available", "disabled", "unavailable"]

client = mqtt.Client("rockrider540")


def send_mqtt_error(error, id):
    client.connect("10.0.1.150")
    client.publish(f"decathlon/error/{id}", error)


def send_mqtt_success(message, id):
    client.connect("10.0.1.150")
    client.publish(f"decathlon/success/{id}", message)


def check_online(url_parh, model, name, id):
    try:
        if is_available_online(url_parh, model):
            send_mqtt_success(f"Found for model: {name}, at url: {url_parh}", id)
    except Exception as e:
        send_mqtt_error(str(e), id)
        raise e


def check_in_store(url_parh, model, name, id, city):
    try:
        if is_available_in_store(url_parh, model):
            send_mqtt_success(f"Found in store in {city} for model: {name}, at url: {url_parh}", id)
    except Exception as e:
        send_mqtt_error(str(e), id)
        raise e


def is_available_online(url, model):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        status = soup.find("div", {"id": "dropdown-list-size"}).find("li", {"id": model}).get("class")[0]
        check_response_status(status)
        return status == "available"
    except Exception as e:
        raise Exception(f"For model: {model} we have exception: {str(e)}")


def is_available_in_store(url, model):
    try:
        response = requests.get(url)
        return len(response.json()["nbProductsList"]) > 0
    except Exception as e:
        raise Exception(f"For model: {model} we have exception: {str(e)}")


def check_response_status(status):
    if status not in VALID_STATUSES:
        raise Exception(f"Invalid status Response: {str(status)}")


if __name__ == '__main__':
    for url in URLS:
        check_online(url.get("url"), url.get("model"), url.get("name"), url.get("id"))

    for store in magazine_url:
        check_in_store(store.get("url"), store.get("model"), store.get("name"), store.get("id"), store.get("city"))
