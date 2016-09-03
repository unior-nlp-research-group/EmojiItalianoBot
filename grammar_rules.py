# -*- coding: utf-8 -*-

REGOLE_GENERALI_BUTTON = "Regole generali"
REGOLE_APOSTROFO_BUTTON = "'"
REGOLE_TRIANGOLO_SX_BUTTON = "◀"
REGOLE_TRIANGOLO_DX_BUTTON = "▶"
REGOLE_FRECCIA_SX_BUTTON = "⬅"
REGOLE_CONDIZIONALE_BUTTON = "🙏"
REGOLE_ESCLAMATIVO_BUTTON = "❗"
REGOLE_INTERROGATIVO_BUTTON = "❓"


GRAMMAR_RULES = {
REGOLE_GENERALI_BUTTON:
"""
Queste sono le regole generali:
  🔹 Ordine di lettura: da sinistra a destra
  🔹 Ordine sintattico: Soggetto Verbo Oggetto
  🔹 Aggetttivo invariabile
  🔹 Aggettivo (privo di indicatore), collocato a sinistra del sostantivo
  🔹 Plurale dei sostantivi: duplicazione del segno
""",

REGOLE_APOSTROFO_BUTTON: # (apostrofo)
"""
L'apostrofo (') viene inserito a sinistra del verbo per distinguerlo da un possibile sostantivo che usa lo stesso emoji.
  🔹 Esempio: parola / parlare
""",

REGOLE_TRIANGOLO_SX_BUTTON:
"""
Il simbolo ◀ viene inserito a sinistra del verbo per indicarne il tempo passato
  🔹 Esempio:
""",

REGOLE_TRIANGOLO_DX_BUTTON:
"""
Il simbolo ▶ viene inserito a sinistra del verbo per indicarne il tempo futuro
  🔹 Esempio:
""",

REGOLE_FRECCIA_SX_BUTTON:
"""
1️⃣ Il simbolo ⬅ viene inserito a destra dell'aggettivo per trasformarlo in avverbio
  🔹 Esempio:

2️⃣ Il simbolo ⬅ viene inserito a a destra del verbo per indicarne il tempo gerundio o participio presente
  🔹 Esempio:
""",

REGOLE_CONDIZIONALE_BUTTON:
"""
Il simbolo 🙏 viene inserito davanti al verbo per indicarne il modo condizionale
  🔹 Esempio: io vorrei andare: ℹ_’🙏👞_
""",

REGOLE_ESCLAMATIVO_BUTTON:
"""
Il simbolo ❗ viene inserito a inizio frase per segnalare imperativo.
  🔹 Esempio:
""",

REGOLE_INTERROGATIVO_BUTTON:
"""
Il simbolo ❓ viene inserito a inizio frase per segnalare che la frase è interrogativa.
  🔹 Esempio:
"""
}

FUNCTIONAL_EMOJIS = sorted([e for e in GRAMMAR_RULES.keys() if e != REGOLE_GENERALI_BUTTON])