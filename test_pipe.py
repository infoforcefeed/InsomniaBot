from socketproxy import Pipe, SocketPlumbing, main
from socketproxy import logging
import os


class TestProxy(SocketPlumbing):
    def __init__(self, *args):
        SocketPlumbing.__init__(self, *args)
        self.pipes.append(AudioPipe('horn', open('airhorn.mp3')))
        self.pipes.append(AudioPipe('trumpet', open('trumpet.mp3')))


class AudioPipe(Pipe):
    
    def __init__(self, name, mp3):
        self.mp3 = mp3.read()
        self.name = name
        self.buff = ''

    def recieve_inbound(self, data):

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
