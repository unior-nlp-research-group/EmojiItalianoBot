# -*- coding: utf-8 -*-

import utility

GRAMMAR_RULES_DOC_KEYS = '1wVyoEspmZWBkflAe498GbI1pV5l7RbPBFWAA5rszJHI'
GRAMMAR_RULES_DOC_URL = "https://docs.google.com/spreadsheets/d/{0}/export?format=tsv&gid=0".format(GRAMMAR_RULES_DOC_KEYS)

GRAMMAR_RULES_STRUCTURE = None # {'rule type': {'position': 1, 'rules': []}}

def getGrammarStructure():
    global GRAMMAR_RULES_STRUCTURE
    if GRAMMAR_RULES_STRUCTURE == None:
        buildGrammarRules()
    return GRAMMAR_RULES_STRUCTURE

def buildGrammarRules():
    import csv, requests
    global GRAMMAR_RULES_STRUCTURE
    GRAMMAR_RULES_STRUCTURE = {}
    r = requests.get(GRAMMAR_RULES_DOC_URL)
    spreadSheetTsv = r.iter_lines()
    spreadSheetReader = csv.reader(spreadSheetTsv, delimiter='\t', quoting=csv.QUOTE_NONE)
    line_num = 1
    position = 1
    current_title = ''
    current_title_rules = []
    def addRule(position, current_title, current_title_rules):
        if current_title and current_title_rules:
            GRAMMAR_RULES_STRUCTURE[current_title] = {
                'position': position,
                'rules': current_title_rules
            }
            return True
        return False
    for row in spreadSheetReader:
        if len(row)<2:
            continue
        if row[0]:
            if addRule(position, current_title, current_title_rules):
                position = position + 1
            current_title = row[0]
            current_title_rules = []
        if row[1]:
            current_title_rules.append(row[1])
        line_num += 1
    addRule(position, current_title, current_title_rules)


RULE_TYPES_SORTED = sorted(getGrammarStructure().keys(), key=lambda k: getGrammarStructure()[k]['position'])
COMMANDS = ["/{} {}".format(n,c) for n,c in enumerate(RULE_TYPES_SORTED, 1)]

GRAMMAR_INSTRUCTIONS = utility.unindent(
    """
    Queste sono le regole grammaticali di emojitaliano.
    Premi sul numero della regola che vuoi visualizzare.\n\n{}
    """.format('\n'.join(COMMANDS))
)

BULLET_POINT = '•'

def getGrammarRulesText(position):
    GR = getGrammarStructure()
    if position<1 or position > len(GR):
        return 'Regola non trovata'
    rule_type = RULE_TYPES_SORTED[position - 1]
    return '*{}*\n\n'.format(rule_type) + '\n\n'.join("{} {}".format(BULLET_POINT, r) for r in GR[rule_type]['rules'])
