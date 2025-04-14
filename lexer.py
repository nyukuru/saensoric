class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"

# Range from E1 - G7: 76 keys
def tokenize(beat_list: list[tuple[int, ...]]):
    keychords = {
        (60, 52, 73): "BOOLEAN"
    }
    state = 0
    for beat in beat_list:
        if state == 0:
            if beat == ():
                continue
            if beat in keychords:
                yield Token(keychords[beat], beat)
        elif state == 1:
            
        elif state == 2:
        elif state == 3:
