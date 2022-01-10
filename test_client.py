from time import sleep

from PbClientSocket import PbClientSocket


class MyClient(PbClientSocket):
    def processRecord(self, record):
        print(record)
        print('---'*30)
        sleep(1)
        self.sendRecord(record)


if __name__ == '__main__':
    myClient = MyClient(host="kubernetes.docker.internal", port=54802)
    myClient.startUp()