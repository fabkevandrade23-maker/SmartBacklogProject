

from openai import OpenAI  # Import du client OpenAI pour utiliser l’API GPT

client = OpenAI()
# Création d’une instance du client OpenAI (permet d’envoyer des requêtes à l’IA)


def prioritize(tasks):
    # Fonction qui prend une liste de tâches en entrée

    prompt = f"""
    Classe ces tâches par priorité (1 = urgent, 5 = faible) :
    {tasks}
    """
    # Création du prompt envoyé à l’IA
    #  On demande à GPT de classer les tâches par priorité
    #  Les tâches sont injectées directement dans le texte

    res = client.chat.completions.create(
        model="gpt-4o",
        # Modèle utilisé (GPT-4o)

        messages=[{"role": "user", "content": prompt}]
        # Message envoyé à l’IA
        # role = "user" → c’est une instruction utilisateur
        # content = prompt → le texte qu’on a construit
    )

    return res.choices[0].message.content
    # Retourne la réponse générée par l’IA
    # On récupère le premier choix (choices[0])
    # Puis le message généré (content)