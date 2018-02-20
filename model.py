class Model():
    selected=''
    

    def __init__(self):
        with open("dnd-spells/spells.json") as jfile:
            self.spellbook=json.load(jfile)
        self.spelllist={spell['name']:spell for spell in self.spellbook}





    def search(self, terms):
        spells=[]
        if terms[0].startswith('^'):
            term=' '.join(terms)[1:]
            for spell in self.spellbook:
                if spell['name'].lower().startswith(term):
                    spells.append(spell)
        else:
            for spell in self.spellbook:
                if all(term in spell["name"].lower() for term in terms):
                    spells.append(spell)
        return spells
