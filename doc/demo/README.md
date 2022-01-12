# 實際使用

<br>

---

<br>

這邊就是筆記的最後了，示範一下如何使用這個套件。

<br>

在 pbsocket 裡面有 2 個示範文件：

* [test_client.py](../../test_client.py)

* [test_server.py](../../test_server.py)

<br>
<br>
<br>
<br>


## test_client.py

```py
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
```

<br>
<br>
<br>
<br>

## test_server.py

<br>

```py
import time

import ProtoData_pb2
from PbServerSocket import PbServerSocket

if __name__ == '__main__':
    data1 = ProtoData_pb2.PbData()
    data1.dataType = data1.DataType.STRING
    data1.binaryData = "Hello Wolrd!".encode('utf-8')
    data2 = ProtoData_pb2.PbData()
    data2.dataType = data2.DataType.INT
    data2.binaryData = int(21).to_bytes(4, byteorder='big')
    record = ProtoData_pb2.Record()
    record.signal = record.Signal.NODE
    record.column['msg'].CopyFrom(data1)
    record.column['age'].CopyFrom(data2)

    recordEnd = ProtoData_pb2.Record()
    recordEnd.signal = record.Signal.STOP

    server = PbServerSocket()
    server.record_list.append(record)
    server.record_list.append(recordEnd)
    server.startUp()

    # 關閉 Server Socket 時使用
    # time.sleep(10)
    # server.close()
```
