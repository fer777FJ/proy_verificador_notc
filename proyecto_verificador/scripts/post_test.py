import requests

url = 'http://127.0.0.1:8000/verificar-texto'
payload = {
    'titular': 'Gary Rodriguez: Si las exportaciones caen o se frenan debido el arancel impuesto por EEUU habra menos dolares y menos empleo',
    'contenido': 'El presidente de los Estados Unidos ha fijado un arancel del 10% a los productos...'
}

resp = requests.post(url, json=payload)
print('status', resp.status_code)
print(resp.text)
