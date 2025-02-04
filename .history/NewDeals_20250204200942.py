import json
import os
from datetime import datetime

import pywhatkit # type: ignore
import requests # type: ignore
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações
API_KEY = os.getenv('PIPEDRIVE_API_KEY')
FILTER_ID = os.getenv('PIPEDRIVE_FILTER_ID')
WHATSAPP_RECIPIENT = os.getenv('WHATSAPP_RECIPIENT')
STORAGE_FILE = "sent_ids.json"

# Validação das variáveis de ambiente
if not all([API_KEY, FILTER_ID, WHATSAPP_RECIPIENT]):
    raise ValueError("As variáveis de ambiente necessárias não estão configuradas.")

def get_pipedrive_deals():
    url = f"https://poloarbauru2.pipedrive.com/api/v1/deals?api_token={API_KEY}&filter_id={FILTER_ID}"
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
    try:
        # Remove o '+' do número se existir
        numero = WHATSAPP_RECIPIENT.replace('+', '')
        # Adiciona o '+' no formato correto
        numero_formatado = f"+{numero}"
        
        # Envia a mensagem instantaneamente
        pywhatkit.sendwhatmsg_instantly(
            numero_formatado,
            message,
            wait_time=20,  # Tempo de espera em segundos
        )
        print(f"Mensagem enviada com sucesso para {numero_formatado}")
    except Exception as e:
        raise Exception(f"Erro ao enviar mensagem via WhatsApp: {e}")

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
        print("Nenhum novo ID dos negócios acima de R$15k encontrado.")
        message = f"Nenhum novo ID dos negócios acima de R$15k encontrado."
        send_whatsapp_message(message)
        return
    # Construir mensagem
    if len(sent_ids) > 0:
        message = f"Além dos {last_count} IDs dos negócios acima de R$15k informados anteriormente, seguem os outros IDs:\n"
        message += ", ".join(map(str, new_ids))
        new_count = len(new_ids)
    else:
        message = "IDs dos negócios acima de R$15k encontrados:\n"
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