import pyaudio
import numpy as np
import json


class MorsePlayer:
    RATE = 44100
    LONG = 0.25
    SHORT = 0.05
    LONG_REST = 0.6
    SHORT_REST = 0.12
    REST_AFTER_LONG = 0.03
    FREQUENCY = 1000
    LANGUAGE = 'english'

    def __init__(self, filename):
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paFloat32,
                             channels=1,
                             rate=self.RATE,
                             frames_per_buffer=1024,
                             output=True)
        self.tones = {'long': np.hstack([self.generate(self.LONG, 1),
                                         self.generate(self.REST_AFTER_LONG, 0)]),
                      'short': np.hstack([self.generate(self.SHORT, 1),
                                          self.generate(self.SHORT_REST, 0)]),
                      'short_rest': self.generate(self.SHORT_REST, 0),
                      'long_rest': self.generate(self.LONG_REST, 0)}

        with open(filename, encoding='utf-8') as f:
            self.morse_dict = json.load(f)[self.LANGUAGE]

    def generate(self, length, gain):
        t = self.FREQUENCY * np.pi * 2 / self.RATE
        return np.sin(np.arange(length * self.RATE) * t) * gain

    def play(self, letter, is_end):
        for c in self.morse_dict[letter]:
            if c == '.':
                self.stream.write(self.tones['short'].astype(np.float32).tostring())
            else:
                self.stream.write(self.tones['long'].astype(np.float32).tostring())

        if is_end:
            self.stream.write(self.tones['long_rest'].astype(np.float32).tostring())
        else:
            self.stream.write(self.tones['short_rest'].astype(np.float32).tostring())

    def mainloop(self):
        while True:
            words = input('input:')
            self.stream.write(self.tones['long_rest'].astype(np.float32).tostring())
            for word in words.split(' '):
                for i, letter in enumerate(word):
                    is_end = (i == len(word) - 1)
                    self.play(str.lower(letter), is_end)


def main():
    player = MorsePlayer('morse.json')

    try:
        player.mainloop()
    except KeyboardInterrupt:
        print('bye')
        return


if __name__ == '__main__':
    main()
