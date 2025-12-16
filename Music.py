import RPi.GPIO as GPIO
import time
from EtatAlerte import pwm


BUZZER_PIN = 16

pwm_started = False

class Note:
    def __init__(self, name: str, freq: float, duration: float):
        """
        name     : nom de la note (ex: "C4", "D4", "silence")
        freq     : fréquence en Hz (0 pour un silence)
        duration : durée en secondes
        """
        self.name = name
        self.freq = freq
        self.duration = duration

    def __repr__(self):
        return f"Note(name={self.name}, freq={self.freq}, duration={self.duration})"


class Notes:
    """
    Banque de notes prêtes à l'emploi.
    """

    NOTES = {
        "C4": 261.63,
        "D4": 293.66,
        "E4": 329.63,
        "F4": 349.23,
        "G4": 392.00,
        "A4": 440.00,
        "B4": 493.88,
        "C5": 523.25,
        "REST": 0,  # silence
    }

    @classmethod
    def get(cls, name: str, duration: float):
        """
        Retourne un objet Note pour le nom donné et la durée voulue.
        Si la note n'existe pas, ça lève une erreur.
        """
        name = name.upper()
        if name not in cls.NOTES:
            raise ValueError(f"Note inconnue: {name}")
        freq = cls.NOTES[name]
        return Note(name, freq, duration)


class Music:
    def __init__(self, tempo_bpm: int = 120):
        """
        tempo_bpm : tempo en battements par minute
        On va utiliser des durées relatives (1 temps, 0.5 temps, etc.) basées là-dessus.
        """
        self.tempo_bpm = tempo_bpm
        self.notes = []

    @property
    def beat_duration(self) -> float:
        """Durée d'un temps (noire) en secondes."""
        return 60.0 / self.tempo_bpm

    def add_note_name(self, note_name: str, beats: float = 1.0):
        """
        Ajoute une note à partir de son nom dans Notes.NOTES.
        beats : nombre de temps (1.0 = noire, 0.5 = croche, 2.0 = blanche, etc.)
        """
        duration = self.beat_duration * beats
        note = Notes.get(note_name, duration)
        self.notes.append(note)

    def add_note(self, note: Note):
        """Ajoute directement un objet Note """
        self.notes.append(note)

    def clear(self):
        """Efface la mélodie courante."""
        self.notes = []

    def play(self):
        """
        Joue toutes les notes sur le buzzer.
        """
        global pwm_started

        for note in self.notes:
            if note.freq <= 0:
                # Silence
                if pwm_started:
                    pwm.stop()
                    pwm_started = False
                time.sleep(note.duration)
            else:
                # Note audible
                if not pwm_started:
                    pwm.start(6)  # duty cycle à 6% pour avoir un son correct
                    pwm_started = True
                pwm.ChangeFrequency(note.freq)
                time.sleep(note.duration)

        # On coupe le son à la fin
        if pwm_started:
            pwm.stop()
            pwm_started = False


music = Music(tempo_bpm=120)

music.add_note_name("C4", beats=0.25)
music.add_note_name("D4", beats=0.25)
music.add_note_name("F4", beats=0.25)
music.add_note_name("D4", beats=0.25)
music.add_note_name("A4", beats=1.5)
music.add_note_name("G4", beats=1.5)

music.add_note_name("REST", beats=0.2)

music.add_note_name("C4", beats=0.25)
music.add_note_name("D4", beats=0.25)
music.add_note_name("F4", beats=0.25)
music.add_note_name("D4", beats=0.25)
music.add_note_name("G4", beats=1.5)
music.add_note_name("F4", beats=1.5)

music.play() # lance l'introduction en attendant que le serveur se lance


"""
music.add_note_name("REST", beats=0.2)

music.add_note_name("C4", beats=0.25)
music.add_note_name("D4", beats=0.25)
music.add_note_name("F4", beats=0.25)
music.add_note_name("D4", beats=0.25)
music.add_note_name("F4", beats=1)
music.add_note_name("G4", beats=0.5)
music.add_note_name("E4", beats=0.5)
music.add_note_name("D4", beats=0.25)
music.add_note_name("C4", beats=0.25)

music.add_note_name("REST", beats=0.25)

music.add_note_name("C4", beats=0.5)
music.add_note_name("G4", beats=1)
music.add_note_name("F4", beats=1)
"""
