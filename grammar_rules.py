# -*- coding: utf-8 -*-

import utility

REGOLE_GENERALI_COMMAND = "/1 Regole Generali"
RECOLE_ARTICOLI_COMMAND = "/2 Articoli"
REGOLE_PRONOMI_COMMAND = "/3 Pronomi"
REGOLE_VERBI_COMMAND = "/4 Verbi"
REGOLE_AGGETTIVI_SOSTANTIVI_COMMAND = "/5 Aggettivi e sostantivi"
REGOLE_AVVERBI_COMMAND = "/6 Avverbi"
CONNETTIVI = "/7 Connettivi"
REGOLE_IDIOMI_COMMAND = "/8 Espressioni idiomatiche"


COMMANDS = [
    REGOLE_GENERALI_COMMAND,
    RECOLE_ARTICOLI_COMMAND,
    REGOLE_PRONOMI_COMMAND,
    REGOLE_VERBI_COMMAND,
    REGOLE_AGGETTIVI_SOSTANTIVI_COMMAND,
    REGOLE_AVVERBI_COMMAND,
    CONNETTIVI,
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
🔹 L'ordine sintattico di base è Soggetto Verbo Oggetto: ℹ’🍽🍮 = io mangio la polenta.
🔹 La frase passiva viene trasformata in attiva per rispettare l'ordine di base.
🔹 Il soggetto va sempre espresso.
🔹 Due underscore delimitano, a destra e a sinistra, i segni composti: _🏠⚒_ = bottega, _'👞🔙_ = tornare. In generale è delimitata da underscore ogni sequenza di segni (emoji e/o diacritici) il cui significato si definisce sinteticamente dalla sequenza stessa.
🔹 Nei segni composti il determinato precede il determinante: _🏠⚒_ = bottega (casa degli attrezzi)
🔹 La punteggiatura del testo originale è conservata.
""",

RECOLE_ARTICOLI_COMMAND:
"""
Regole degli articoli:
🔹 L'articolo determinativo viene omesso: 🏠 = la casa.
🔹 L'articolo indeterminativo viene indicato con 1⃣ prima del sostantivo: 1⃣🏠 = una casa.
""",

REGOLE_PRONOMI_COMMAND:
"""
Regole dei pronomi personali:
🔹 I pronomi personali al singolare sono:  ℹ️ = io, 👆= tu,  🚹 = egli,  🚺 = ella. 
🔹 Il plurale dei pronomi personali si ottiene duplicando il singolare: _ℹ️ℹ️_ = noi, _👆👆_ = voi, _🚹🚹_ = essi, _🚺🚺_ = esse.
🔹 Questi pronomi valgono sia come pronome soggetto che come pronome complemento.
🔹 I pronomi possessivi si ottengono inserendo ⏩ prima del pronome personale: _⏩ℹ_ = il mio (di me).
""",

REGOLE_VERBI_COMMAND:
"""
Regole dei verbi:
🔹 Il verbo è invariabile nella persona, con esplicitazione obbligatoria del soggetto: ℹ'🈶 = io sono, ﻿👆'🈶 = tu sei, _👆👆_ '🈶 = voi siete.
🔹 Marcatore del verbo ' (a sinistra dell'emoji): 👞 = scarpa, '👞 = andare.
🔹Il verbo col solo marcatore ' vale come infinito, indicativo semplice, e/o tempo presente.

Altri tempi e modi sono riconoscibili da specifici marcatori:
🔹 Marcatore del passato ◀ Esempio: ℹ️_'👞◀_ = io sono andato, io andavo, io andai, io ero andato (ecc.).
🔹 Marcatore del futuro ▶ Esempio: ℹ️_'👞▶_ = io andrò, io sarò andato (ecc.).
🔹 Marcatore del gerundio e del participio presente ⬅ Esempio:  _'👞⬅_ = andando, andante.
🔹 Marcatore del causativo ➡ Esempio: _➡️'👞_ = far andare.
🔹 Marcatore del riflessivo (quando non esplicitato nella resa linguistica del verbo)  👈 posposto al verbo Esempio: _'⏰👈_  = svegliarsi.
🔹 Marcatore del reciproco (quando non esplicitato nella resa linguistica del verbo) 👥 posposto al verbo Esempio: _'👊👥_ = picchiarsi.
🔹 Marcatore del condizionale 🎲 Esempio: ℹ️_🎲'👞_ = io andrei.
🔹 Marcatore dell'imperativo e dell’esortativo❗️Esempio: 👆_❗'👞_  = vai!
🔹 Marcatore dell'interrogativo❓Esempio: 👆_❓'👞_ = vai?
""",

REGOLE_AGGETTIVI_SOSTANTIVI_COMMAND:
"""
Regole degli aggettivi e dei sostativi:
🔹 L'aggettivo è collocato a destra del sostantivo: 🏠🔆= (la) bella casa, (la) casa bella.
🔹 Il plurale dei sostantivi e degli aggettivi si ottiene con la duplicazione del segno: 🏠= casa, _🏠🏠_= case, _🏠⚒_ = bottega, _🏠⚒🏠⚒_ = botteghe, _🏠⚒_🐽  = bottega sporca, _🏠⚒_🐽_🏠⚒_🐽 = botteghe sporche.
🔹 Il marcatore (◀) viene inserito a destra del verbo corrispondente ma senza diacritico ' per indicare il participio passato (con valore aggettivale o sostantivato): _👞◀_ andato.
🔹 Gli aggettivi possessivi si ottengono inserendo ⏩ prima del pronome personale: _⏩ℹ_ = mio (di me).
""",

REGOLE_AVVERBI_COMMAND:
"""
Regole degli avverbi:
🔹 Il simbolo ⬅ viene inserito a destra dell'aggettivo per trasformarlo in avverbio: 🐌 = lento, _🐌⬅_ = lentamente.
""",

CONNETTIVI:
"""
Regole dei connettivi:
🔹 E (congiunzione) ➕ Esempio: 🏃➕_👨💟_ _'👞🔙_▶️🏠 = Pinocchio e Geppetto tornarono a casa.
🔹 O, Invece di (avversativo) 🔁 Esempio: 🚹🚹_'🈶🃏🃏🔁_🚹🚹_'🈶👿👿! = Sono matti o imbroglioni
🔹 Che (oggettivo) ⏬ Esempio: 🚹_'👀◀️_⏬🤖_'🔄◀️_ = egli vide che il burattino si muoveva.
🔹 Che (relativo) ↪️ Esempio: 🏃,↪️_'😋◀️_, _'🍽◀️_ = Pinocchio, che aveva fame, mangiò.
🔹 Di ⏩ Esempio: 👃⏩🏃 = il naso di Pinocchio; 🔩⏩🚪= pezzo di legno.
🔹 A (direzione) ▶️ Esempio: ℹ'👞▶🏠 = io vado a casa.
🔹 Da (provenienza, derivazione) ◀️ Esempio: ℹ_'👞👇_◀️🏠 = io vengo da casa.
🔹 In (dentro) ⏺ Esempio: ℹ'🍽⏺🏠 = io mangio in/a casa.
🔹 Su 🔼 Esempio: ‘📈🔼 = salire su.
🔹 Giù 🔽 Esempio: 📎👅🔽 = con la lingua giù.
🔹 Sopra qualcosa ⤵️ Esempio: 🚹_📥◀️_🔨⤵️⛩ = egli mise il martello sul tavolo.
🔹 Sotto qualcosa ⤴️ Esempio: 🚹_📥◀️_👞👞_⤴️🛏 = egli mise le scarpe sotto il letto.
🔹 Al centro di (tra, in mezzo a) 🎯 Esempio: 🎯_🔲🏠 = al centro della stanza.
🔹 Con (compagnia)  📎 Esempio: 🏃_'👞🔙_▶️🏠📎_👨💟_ = Pinocchio tornò a casa con Geppetto.
🔹 Per (a causa di) ↙️ Esempio: 🏃_'😱◀️_ ↙️🚹_'👂◀️_ _😈🗡😈🗡_ _'👞👇 _ = Pinocchio era spaventato perché (per il fatto che) sentiva gli assassini arrivare.
🔹 Per (allo scopo di) ↗️ Esempio: ↗️🏃_'👐◀️_ _⚜️⚜️_ = affinché/perché Pinocchio consegnasse le monete.
🔹 Verso, contro, di fronte a, nei confronti di 🆚 Esempio: _👨💟_ _’🔄◀️_🆚🏃= Geppetto si voltò verso Pinocchio.
🔹 Così che (consecutivo) 🔝➡️  Esempio: 🏃_'😱◀️_ _🔝➡️_🚹_'🍃◀️_ = Pinocchio era tanto spaventato che tremava.
🔹 Benché (concessivo) _➕👍🎲_ Esempio: _➕👍🎲_🏃🙅_'🙏‼️◀️_, 🏃_'👞◀️_▶🏠 = benché non volesse (anche se non voleva), Pinocchio andò a casa.
""",

REGOLE_IDIOMI_COMMAND:
"""
Regole delle espressioni idiomatiche:
🔹 Le voci idiomatiche o figurate sono rese con equivalenti della lingua piana; il glossario registra l'accezione del testo originale e anche l'espressione italiana equivalente non figurata. _'👊🔝_ = darne un sacco è una sporta, picchiare molto forte.
""",

}

