from time import sleep

from pbsocket import PbClientSocket


class MyClient(PbClientSocket):
    def processRecord(self, record):
        if record.signal.__eq__(record.Signal.STOP):
            pass
        print(record)
        print('---'*30)
        sleep(3)
        self.sendRecord(record)


if __name__ == '__main__':
    myClient = MyClient()
    myClient.startUp()