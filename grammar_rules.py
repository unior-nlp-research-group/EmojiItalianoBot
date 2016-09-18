# -*- coding: utf-8 -*-

import utility

REGOLE_GENERALI_COMMAND = "/1 Regole Generali"
RECOLE_ARTICOLI_COMMAND = "/2 Articoli"
REGOLE_PRONOMI_COMMAND = "/3 Pronomi"
REGOLE_VERBI_COMMAND = "/4 Verbi"
REGOLE_AGGETTIVI_SOSTANTIVI_COMMAND = "/5 Aggettivi e sostantivi"
REGOLE_AVVERBI_COMMAND = "/6 Avverbi"
REGOLE_COMPLEMENTI = "/7 Complementi"
REGOLE_SINTASSI_FRASI = "/8 Sintassi delle frasi"
REGOLE_IDIOMI_COMMAND = "/9 Espressioni idiomatiche"


COMMANDS = [
    REGOLE_GENERALI_COMMAND,
    RECOLE_ARTICOLI_COMMAND,
    REGOLE_PRONOMI_COMMAND,
    REGOLE_VERBI_COMMAND,
    REGOLE_AGGETTIVI_SOSTANTIVI_COMMAND,
    REGOLE_AVVERBI_COMMAND,
    REGOLE_COMPLEMENTI,
    REGOLE_SINTASSI_FRASI,
    REGOLE_IDIOMI_COMMAND
]

GRAMMAR_INSTRUCTIONS = utility.unindent(
    """
    Queste sono le regole grammaticali di emojitaliano.
    Premi sul numero della regola che vuoi visualizzare.\n\n{}
    """.format('\n'.join(COMMANDS))
)


GRAMMAR_RULES = {
REGOLE_GENERALI_COMMAND:
"""
Regole generali:
🔹 L'ordine di lettura è da sinistra a destra.
🔹 L'ordine sintattico di base è Soggetto Verbo Oggetto: ℹ’🍽🍮 = io mangio la polenta. 🔹 La frase passiva viene trasformata in attiva per rispettare l'ordine dato.
🔹 Il soggetto va sempre espresso.
🔹 Due underscore delimitano, a destra e a sinistra, i segni composti: _🏠⚒_ = bottega, _'👞🔙_ = tornare.
🔹 Nei segni composti il determinato precede il determinante: _🏠⚒_ = bottega (casa degli attrezzi)
🔹 La punteggiatura del testo originale è conservata.
""",

RECOLE_ARTICOLI_COMMAND:
"""
Regole degli articoli:
🔹 L'articolo determinativo viene omesso: 🏠 = la casa.
🔹 L'articolo indeterminativo viene indicato con 1⃣prima del sostantivo: 1⃣🏠 = una casa.
""",

REGOLE_PRONOMI_COMMAND:
"""
Regole dei pronomi personali:
🔹 I pronomi personali al singolare sono:  ℹ️ = io, 👆= tu,  🚹 = egli,  🚺 = ella.
🔹 Il plurale dei pronomi personali si ottiene duplicando il singolare: _ℹ️ℹ️_ = noi, _👆👆_ = voi, _🚹🚹_ = essi, _🚺🚺_ = esse.
🔹 Questi pronomi valgono sia come pronome soggetto che come pronomi complemento.
🔹 I pronomi possessivi si ottengono inserendo ⏩ prima del pronome: _⏩ℹ_ = mio (di me).
""",

REGOLE_VERBI_COMMAND:
"""
Regole dei verbi:
🔹 Il diacritico (') viene inserito a sinistra dell'emoji come indicatore della categoria “verbo”: 👞 = scarpa, '👞 = andare.
🔹 Il verbo è invariabile, con esplicitazione obbligatoria del soggetto: ℹ'🈶 = io sono, ﻿👆'🈶 = tu sei, _👆👆_ '🈶 = voi siete.
🔹 Il verbo senza marcatori (◀, ▶) è da considerarsi al tempo presente.
🔹 Il marcatore ◀ viene inserito a destra del verbo per indicarne forme verbali del passato:
ℹ️_'👞◀_ = io sono andato, io andavo, io andai, io ero andato (ecc.).
🔹 Il marcatore ▶ viene inserito a destra del verbo per indicarne forme verbali del futuro:
 ℹ️_'👞▶_ = io andrò, io sarò andato.
🔹 Il simbolo 🎲 viene inserito a sinistra del verbo per indicarne il modo condizionale: ℹ️_🎲'👞_ = io andrei.
🔹 Il simbolo ⬅ viene inserito a destra del verbo per indicare il gerundio e participio presente:  _'👞⬅_ = andando, andante.
🔹 Il simbolo ➡ ha funzione di causativo: _➡️'👞_ = far andare.
🔹 Il riflessivo, quando non esplicitato nella resa linguistica del verbo, viene indicato con il marcatore 👈 posposto al verbo: _'⏰👈_  = svegliarsi.
🔹 Il reciproco, quando non esplicitato nella resa linguistica del verbo, si ottiene con il marcatore 👥 posposto al verbo: _'👊👥_ = picchiarsi.
""",

REGOLE_AGGETTIVI_SOSTANTIVI_COMMAND:
"""
Regole degli aggettivi e dei sostativi:
🔹 L'aggettivo è collocato a destra del sostantivo: 🏠🔆= (la) bella casa, (la) casa bella.
🔹 Il plurale dei sostantivi e degli aggettivi si ottiene con la duplicazione del segno: 🏠= casa, _🏠🏠_= case, _🏠⚒_ = bottega, _🏠⚒🏠⚒_ = botteghe, _🏠⚒_🐽  = bottega sporca, _🏠⚒_🐽_🏠⚒_🐽 = botteghe sporche.
🔹 Il marcatore (◀) viene inserito a destra del verbo corrispondente ma senza diacritico (') per indicare il participio passato (con valore aggettivale o sostantivato): _👞◀_ andato.
🔹 Gli aggettivi possessivi si ottengono inserendo ⏩ prima del pronome: _⏩ℹ_ = mio (di me).
""",

REGOLE_AVVERBI_COMMAND:
"""
Regole degli avverbi:
🔹 Il simbolo ⬅ viene inserito a destra dell'aggettivo per trasformarlo in avverbio: 🐌 = lento, _🐌⬅_ = lentamente.
""",

REGOLE_COMPLEMENTI:
"""
Regole dei complementi:
🔹 Il complemento di specificazione è preceduto da ⏩. Esempio: 👃⏩🏃 = il naso di Pinocchio.
🔹 Il complemento di moto a luogo è preceduto da ▶️. Esempio: ℹ'👞▶🏠 = io vado a casa.
🔹 Il complemento di moto da luogo è preceduto da ◀️. Esempio: ℹ_'👞👇_◀️🏠 = io vengo da casa.
🔹 Il complemento di stato in luogo è preceduto da ⤵️. Esempio: ℹ'🍽⤵️🏠 = io mangio in/a casa.
""",

REGOLE_SINTASSI_FRASI:
"""
Regole della sintassi delle frasi:
🔹 La proposizione finale è segnalata da ↗️ iniziale.  Esempio: ↗️🏃_'👐◀️_ _⚜️⚜️_ = affinché/perché Pinocchio consegnasse le monete.
🔹 La proposizione causale è segnalata da ↘️ iniziale. Esempio: 🏃_'😱◀️_ _↘️🚹_'👂◀️_ _😈🗡😈🗡_ _'👞👇 _ = Pinocchio era spaventato perché (per il fatto che) sentiva gli assassini arrivare.
🔹 La proposizione relativa è segnalata da ↪️ iniziale.  Esempio: 🏃↪️_'😋◀️_, _'🍽◀️_ = Pinocchio, che aveva fame, mangiò.
🔹 La proposizione oggettiva è segnalata da ⏬ iniziale.  Esempio: 🚹_'👀◀️_⏬🤖_'🔄◀️_ = egli vide che il burattino si muoveva.
🔹 La proposizione consecutiva è segnalata da _🔝➡️_ iniziale.  Esempio: 🏃_'😱◀️_ _🔝➡️_🚹_'🍃◀️_ = Pinocchio era tanto spaventato che tremava.
🔹 La proposizione concessiva è segnalata da _➕👍🎲_ iniziale. Esempio: _➕👍🎲_🏃🙅_'‼️🙏◀️_, 🏃_'👞◀️_▶🏠 = benché non volesse (anche se non voleva), Pinocchio andò a casa.
🔹 La proposizione imperativa è segnalata da ❗️ a sinistra del verbo.  Esempio: 👆_❗'👞_  = vai!
🔹 La proposizione interrogativa è segnalata da❓ a sinistra del verbo.  Esempio: 👆_❓'👞_ = vai?
""",

REGOLE_IDIOMI_COMMAND:
"""
Regole delle espressioni idiomatiche:
🔹 Le voci idiomatiche o figurate sono rese con equivalenti della lingua piana; il glossario registra l'accezione del testo originale e anche l'espressione italiana equivalente non figurata. _'👊🔝_ = darne un sacco è una sporta, picchiare molto forte.
""",

}

