import requests
import os
import json
from datetime import datetime
import pytz

# Configurações
API_KEY = "SUA_API_KEY_DO_PIPEDRIVE"
FILTER_ID = "ID_DO_SEU_FILTRO"
WHATSAPP_RECIPIENT = "NUMERO_DO_COLEGA"  # Formato internacional, ex: 5511999999999
STORAGE_FILE = "sent_ids.json"

def get_pipedrive_deals():
    url = f"https://api.pipedrive.com/v1/deals?api_key={API_KEY}&filter_id={FILTER_ID}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['data']

def load_sent_ids():
    try:
        with open(STORAGE_FILE, 'r') as f:
            data = json.load(f)
            return set(data['ids']), data.get('last_message_count', 0)
    except FileNotFoundError:
        return set(), 0

def save_sent_ids(ids, count):
    with open(STORAGE_FILE, 'w') as f:
        json.dump({'ids': list(ids), 'last_message_count': count}, f)

def send_whatsapp_message(message):
    
    # Implemente o método de envio do WhatsApp de sua preferência
    # Exemplo usando a biblioteca pywhatkit:
    # import pywhatkit
    # pywhatkit.sendwhatmsg_instantly(WHATSAPP_RECIPIENT, message)
    
    print(f"Mensagem enviada:\n{message}")  # Remova este print quando implementar o envio real

def main():
    # Carregar IDs enviados anteriormente
    sent_ids, last_count = load_sent_ids()
    
    # Buscar negócios no Pipedrive
    try:
        deals = get_pipedrive_deals()
    except Exception as e:
        print(f"Erro ao buscar negócios: {e}")
        return

    current_ids = {deal['id'] for deal in deals}
    new_ids = current_ids - sent_ids

    if not new_ids:
        print("Nenhum novo ID encontrado.")
        return

    # Construir mensagem
    if len(sent_ids) > 0:
        message = f"Além dos {last_count} informados anteriormente, seguem os outros IDs:\n"
        message += ", ".join(map(str, new_ids))
        new_count = len(new_ids)
    else:
        message = "IDs encontrados:\n"
        message += ", ".join(map(str, new_ids))
        new_count = len(new_ids)

    # Enviar mensagem
    try:
        send_whatsapp_message(message)
        # Atualizar IDs armazenados
        save_sent_ids(sent_ids.union(new_ids), new_count)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

if __name__ == "__main__":
    main()