from dotenv import load_dotenv
import os
from openai import OpenAI

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

client = OpenAI()

def prioritize(tasks: list | str, context: str = "", criteria: str = "impact") -> str:
    criteria_map = {
        "impact":   "impact business et valeur pour les utilisateurs",
        "effort":   "ratio effort vs impact (favoriser les quick wins)",
        "urgency":  "urgence et deadlines",
        "risk":     "réduction des risques techniques et business",
    }
    criteria_label = criteria_map.get(criteria, "impact business")

    if isinstance(tasks, list):
        tasks_str = "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks))
    else:
        tasks_str = tasks

    context_block = f"\nContexte du projet : {context}\n" if context else ""

    prompt = f"""Tu es un expert en gestion de produit agile. Analyse ce backlog et priorise les tâches.
{context_block}
Critère principal : {criteria_label}

Tâches à analyser :
{tasks_str}

Réponds avec :
1. **Ordre de priorité recommandé** (numéroté)
2. **Justification** pour chaque tâche (1-2 phrases)
3. **Quick wins** : tâches à fort impact et faible effort
4. **Risques** : tâches bloquantes ou à risque élevé
5. **Recommandation globale** (2-3 phrases de synthèse)

Sois concis, pratique et actionnable."""

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1200,
    )
    return res.choices[0].message.content