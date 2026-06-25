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


print("✅ Iniciando avisador CRM...")

token = login_crm()
leads_iniciales = obtener_leads(token) or []
ids_vistos = {lead.get("id") for lead in leads_iniciales}

enviar_telegram("✅ Avisador CRM iniciado correctamente.")
print("🚀 Revisando nuevos leads...")

while True:
    try:
        leads_actuales = obtener_leads(token)

        if leads_actuales is None:
            print("🔄 Token caducado. Renovando...")
            token = login_crm()
            leads_actuales = obtener_leads(token) or []

        for lead in leads_actuales:
            lead_id = lead.get("id")

            if lead_id not in ids_vistos:
                ids_vistos.add(lead_id)

                nombre = lead.get("name") or lead.get("nombre") or "Sin nombre"
                telefono = lead.get("phone") or lead.get("telefono") or "Sin teléfono"
                email = lead.get("email") or "Sin email"

                mensaje = f"🔔 NUEVO LEAD\n\n👤 {nombre}\n📞 {telefono}\n📧 {email}"
                enviar_telegram(mensaje)
                print(f"📩 Nuevo lead enviado: {nombre}")

    except Exception as e:
        print(f"⚠️ Error: {e}")

    time.sleep(CHECK_SECONDS)
