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
from pbsocket import PbClientSocket


class MyClient(PbClientSocket): ## 繼承 PbClientSocket，並實現 processRecord() 方法。
    def processRecord(self, record):
        if record.signal.__eq__(record.Signal.STOP):
            pass # 遇到 STOP record 不必處理，交給父類別的流程定義就好了。
        print(record)
        print('---'*30)
        sleep(3)
        self.sendRecord(record)


if __name__ == '__main__':
    myClient = MyClient()
    myClient.startUp()
```

<br>
<br>
<br>
<br>

## test_server.py

<br>

```py
from pbsocket import ProtoData_pb2, PbServerSocket

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
    # server.record_list.append(recordEnd)
    server.startUp()
```
