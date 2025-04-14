from mido import MidiFile
from lexer import tokenizer


def main():
    beat_tick = 0
    midi = MidiFile("programs/forrest_gump.sae")
    beat_acc = []

    last_beat: set[int] = set()
    curr_beat: set[int] = set()
    to_delete: set[int] = set()

    for msg in midi.merged_track:

        beat_tick += msg.time
        if beat_tick >= midi.ticks_per_beat:
            last_beat = curr_beat
            beat_acc.append(tuple(curr_beat))
            curr_beat = curr_beat.copy()
            curr_beat = curr_beat - to_delete
            to_delete = set()

        if msg.type == "note_on":
            curr_beat.add(msg.note)
        elif msg.type == "note_off":
            if msg.note in last_beat and msg.note in curr_beat:
                curr_beat.remove(msg.note)
                last_beat.remove(msg.note)
            else:
                to_delete.add(msg.note)

    tokenize(beat_acc)

        

         

    

if __name__ == "__main__":
    main()
