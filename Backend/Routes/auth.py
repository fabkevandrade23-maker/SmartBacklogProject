from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt, bcrypt, json, os, re

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY           = "smartbacklog-secret-key-change-in-production"
ALGORITHM            = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24

USERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── Persistance ──
def _ensure():
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

def load_users() -> dict:
    _ensure()
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(users: dict):
    _ensure()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# ── Modèles ──
class Token(BaseModel):
    access_token: str
    token_type:   str
    username:     str
    role:         str

class RegisterRequest(BaseModel):
    username:  str
    password:  str
    full_name: Optional[str] = ""
    email:     Optional[str] = ""

class UserOut(BaseModel):
    username:   str
    full_name:  str
    email:      str
    role:       str
    created_at: str

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = ""
    email:     Optional[str] = ""

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ── Helpers ──
def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def validate_username(username: str):
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise HTTPException(status_code=422,
            detail="Nom d'utilisateur invalide : 3 à 20 caractères, lettres, chiffres et _ uniquement.")

def validate_password(password: str):
    if len(password) < 6:
        raise HTTPException(status_code=422,
            detail="Le mot de passe doit contenir au moins 6 caractères.")

# ── Dépendances ──
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token invalide")
        users = load_users()
        user  = users.get(username)
        if not user or user.get("disabled"):
            raise HTTPException(status_code=401, detail="Utilisateur introuvable ou désactivé")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré, veuillez vous reconnecter")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return user

# ── Routes ──
@router.post("/register", response_model=UserOut, status_code=201)
def register(body: RegisterRequest):
    validate_username(body.username)
    validate_password(body.password)
    users = load_users()

    if body.username.lower() in [u.lower() for u in users.keys()]:
        raise HTTPException(status_code=409,
            detail="Ce nom d'utilisateur est déjà pris. Choisissez-en un autre.")

    if body.email:
        existing_emails = [u.get("email", "").lower() for u in users.values()]
        if body.email.lower() in existing_emails:
            raise HTTPException(status_code=409,
                detail="Cette adresse email est déjà associée à un compte.")

    now  = datetime.utcnow().isoformat()
    role = "admin" if len(users) == 0 else "member"

    new_user = {
        "username":        body.username,
        "hashed_password": hash_password(body.password),
        "role":            role,
        "full_name":       body.full_name or body.username,
        "email":           body.email or "",
        "disabled":        False,
        "created_at":      now,
        "updated_at":      now,
    }
    users[body.username] = new_user
    save_users(users)

    return UserOut(username=new_user["username"], full_name=new_user["full_name"],
                   email=new_user["email"], role=new_user["role"], created_at=now)

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    users = load_users()
    user  = users.get(form.username)
    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"})
    if user.get("disabled"):
        raise HTTPException(status_code=403, detail="Compte désactivé. Contactez un administrateur.")
    token = create_token({"sub": user["username"], "role": user["role"]})
    return Token(access_token=token, token_type="bearer",
                 username=user["username"], role=user["role"])

@router.get("/me", response_model=UserOut)
def get_me(user=Depends(get_current_user)):
    return UserOut(username=user["username"], full_name=user.get("full_name", ""),
                   email=user.get("email", ""), role=user.get("role", "member"),
                   created_at=user.get("created_at", ""))

@router.put("/me")
def update_me(body: UpdateProfileRequest, user=Depends(get_current_user)):
    users = load_users()
    u = users[user["username"]]
    if body.full_name: u["full_name"] = body.full_name
    if body.email:     u["email"]     = body.email
    u["updated_at"] = datetime.utcnow().isoformat()
    save_users(users)
    return {"detail": "Profil mis à jour"}

@router.post("/change-password")
def change_password(body: ChangePasswordRequest, user=Depends(get_current_user)):
    users = load_users()
    u = users[user["username"]]
    if not verify_password(body.old_password, u["hashed_password"]):
        raise HTTPException(status_code=401, detail="Ancien mot de passe incorrect.")
    validate_password(body.new_password)
    u["hashed_password"] = hash_password(body.new_password)
    u["updated_at"]      = datetime.utcnow().isoformat()
    save_users(users)
    return {"detail": "Mot de passe modifié avec succès"}

@router.get("/users", response_model=list[UserOut])
def list_users(admin=Depends(require_admin)):
    users = load_users()
    return [UserOut(username=u["username"], full_name=u.get("full_name",""),
                    email=u.get("email",""), role=u.get("role","member"),
                    created_at=u.get("created_at","")) for u in users.values()]

@router.delete("/users/{username}")
def delete_user(username: str, admin=Depends(require_admin)):
    if username == admin["username"]:
        raise HTTPException(status_code=400, detail="Impossible de supprimer votre propre compte.")
    users = load_users()
    if username not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    del users[username]
    save_users(users)
    return {"detail": f"Utilisateur '{username}' supprimé."}

@router.patch("/users/{username}/disable")
def toggle_disable(username: str, admin=Depends(require_admin)):
    users = load_users()
    if username not in users:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    users[username]["disabled"] = not users[username].get("disabled", False)
    save_users(users)
    state = "désactivé" if users[username]["disabled"] else "activé"
    return {"detail": f"Compte '{username}' {state}."}