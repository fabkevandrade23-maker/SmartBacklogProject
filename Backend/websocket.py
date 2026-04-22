
from fastapi import WebSocket  # Import du type WebSocket de FastAPI

clients = []  # Liste globale qui va stocker tous les clients connectés

async def websocket_endpoint(websocket: WebSocket):
    # Fonction principale appelée quand un client se connecte

    await websocket.accept()
    # Accepte la connexion WebSocket (sinon refusée)

    clients.append(websocket)
    # On ajoute ce client à la liste des clients connectés

    while True:
        # Boucle infinie pour écouter les messages en continu

        data = await websocket.receive_text()
        # Attend qu’un client envoie un message (texte)

        for client in clients:
            # Parcourt tous les clients connectés

            await client.send_text(data)
            # Envoie le message reçu à TOUS les clients
            #  c’est un système de broadcast (comme un chat)