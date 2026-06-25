import json
import os
from pathlib import Path

import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
CRM_EMAIL = os.environ["CRM_EMAIL"]
CRM_PASSWORD = os.environ["CRM_PASSWORD"]

BASE_URL = "https://crm-ventas-production.up.railway.app"
SEEN_FILE = Path("seen_leads.json")


def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": CHAT_ID, "text": texto})
    response.raise_for_status()


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
    response.raise_for_status()
    return response.json()


def cargar_ids_vistos():
    if not SEEN_FILE.exists():
        return set()

    with SEEN_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return set(data.get("ids_vistos", []))


def guardar_ids_vistos(ids_vistos):
    with SEEN_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            {"ids_vistos": sorted(list(ids_vistos))},
            file,
            ensure_ascii=False,
            indent=2,
        )


print("✅ Revisando CRM...")

token = login_crm()
leads = obtener_leads(token) or []

ids_vistos = cargar_ids_vistos()
nuevos = []

for lead in leads:
    lead_id = str(lead.get("id"))

    if lead_id and lead_id not in ids_vistos:
        nuevos.append(lead)
        ids_vistos.add(lead_id)

if not nuevos:
    print("No hay leads nuevos.")
else:
    for lead in nuevos:
        nombre = lead.get("name") or lead.get("nombre") or "Sin nombre"
        telefono = lead.get("phone") or lead.get("telefono") or "Sin teléfono"
        email = lead.get("email") or "Sin email"

        mensaje = f"🔔 NUEVO LEAD\n\n👤 {nombre}\n📞 {telefono}\n📧 {email}"
        enviar_telegram(mensaje)

        print(f"📩 Lead enviado: {nombre}")

guardar_ids_vistos(ids_vistos)
print("✅ Revisión terminada.")
