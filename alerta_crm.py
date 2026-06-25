import os
import time
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

CRM_EMAIL = os.environ["CRM_EMAIL"]
CRM_PASSWORD = os.environ["CRM_PASSWORD"]

BASE_URL = "https://crm-ventas-production.up.railway.app"
CHECK_SECONDS = 15

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": texto})


def login_crm():
    url = f"{BASE_URL}/api/auth/login"
    response = requests.post(
        url,
        json={
            "email": CRM_EMAIL,
            "password": CRM_PASSWORD,
        },
    )
    response.raise_for_status()
    return response.json()["token"]


def obtener_leads(token):
    url = f"{BASE_URL}/api/leads"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code in [401, 403]:
        return None

    response.raise_for_status()
    return response.json()


print("✅ Revisando CRM...")

token = login_crm()
leads_actuales = obtener_leads(token) or []

if not leads_actuales:
    print("No hay leads.")
else:
    ultimo_lead = leads_actuales[0]

    nombre = ultimo_lead.get("name") or ultimo_lead.get("nombre") or "Sin nombre"
    telefono = ultimo_lead.get("phone") or ultimo_lead.get("telefono") or "Sin teléfono"
    email = ultimo_lead.get("email") or "Sin email"

    mensaje = f"🔔 REVISIÓN CRM\n\n👤 {nombre}\n📞 {telefono}\n📧 {email}"
    enviar_telegram(mensaje)

    print(f"Lead enviado: {nombre}")
