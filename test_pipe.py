from socketproxy import Pipe, PlumbingServer, main
import os
from mutagen.mp3 import MP3


class TestProxy(PlumbingServer):
    def __init__(self, *args, **kwargs):
        PlumbingServer.__init__(self, *args, **kwargs)
        self.pipes.append(AudioPipe('horn', open('airhorn.mp3')))
        self.pipes.append(AudioPipe('trumpet', open('trumpet.mp3')))


class AudioPipe(Pipe):
    
    def __init__(self, name, mp3):
        self.mp3 = mp3.read()
        self.name = name
        self.buff = ''

    def to_client(self, data):

        # Add mp3 to buffer
        if (os.path.isfile(self.name)):
            os.remove(self.name)
            self.buff += self.mp3

        if self.buff:
            if len(self.buff) >= len(data):
               data = self.buff[:len(data)]
               self.buff = self.buff[len(data):]
            else:
                data = self.buff + data[:-len(self.buff)]
                self.buff = ''

        return data


if __name__ == '__main__':
    main(TestProxy)
