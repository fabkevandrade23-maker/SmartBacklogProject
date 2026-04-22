from jose import jwt  # Librairie pour créer et gérer les tokens JWT
from datetime import datetime, timedelta  # Gestion du temps (expiration possible des tokens)

SECRET = "SECRET_KEY"  # Clé secrète utilisée pour signer le token

def create_token(data: dict):
    # Fonction qui génère un token JWT à partir des données utilisateur
    return jwt.encode(data, SECRET, algorithm="HS256")
    # Encode les données avec l'algorithme HS256
