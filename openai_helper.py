import openai
import json
import os

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def charger_historique(nom_fichier):
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauvegarder_historique(nom_fichier, history):
    with open(nom_fichier, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def generate_response(contexte_patient, question, nom_fichier):
    system_prompt = (
        f"Tu es un assistant kinésithérapeute.\n"
        f"Voici les infos du patient : {contexte_patient}\n"
        f"Réponds de manière bienveillante, claire, sans poser de diagnostic médical."
    )

    messages = [{"role": "system", "content": system_prompt}]
    history = charger_historique(nom_fichier)
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.6
    )

    assistant_reply = response.choices[0].message.content
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": assistant_reply})
    sauvegarder_historique(nom_fichier, history)

    return assistant_reply
