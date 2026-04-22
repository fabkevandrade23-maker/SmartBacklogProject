from gpt_service import prioritize
from jose import jwt  # Librairie pour créer et gérer les tokens JWT
from datetime import datetime, timedelta  # Gestion du temps (expiration possible des tokens)

SECRET = "SECRET_KEY"  # Clé secrète utilisée pour signer le token

def create_token(data: dict):
    # Fonction qui génère un token JWT à partir des données utilisateur
    return jwt.encode(data, SECRET, algorithm="HS256")
    # Encode les données avec l'algorithme HS256
from fastapi import APIRouter  # Permet de créer des routes modulaires

router = APIRouter()  # Création du routeur

@router.post("/login")
def login():
    # Route de connexion simple (version test)
    return {"token": "fake-jwt"}
    # Retourne un faux token (simulation)


@router.post("/prioritize")
def prioritize_tasks(data: dict):
    # Route qui reçoit une liste de tâches
    return {"result": prioritize(data["tasks"])}
    # Appelle la fonction prioritize (IA) pour classer les tâches


@router.post("/login")
def login(user: UserLogin):
    # Route de login avec un utilisateur (plus avancée)
    token = create_token({"user": user.email})
    # Génère un token avec l'email de l'utilisateur
    return {"access_token": token}
    # Retourne le token
    
@router.post("/generate")
def generate(data: dict):
    # Route pour générer des tâches automatiquement via IA
    return generate_tasks(data["prompt"])
    # Utilise une fonction IA pour générer les tâches

@router.post("/prioritize")
def prioritize_tasks(data: dict):
    # Route pour prioriser les tâches (version sans wrapper JSON)
    return prioritize(data["tasks"])
    # Retour direct du résultat IA



@router.get("/")
def get_stats():
    # Route pour obtenir des statistiques (exemple)
    return {
        "todo": 5,
        "progress": 3,
        "done": 8
    }