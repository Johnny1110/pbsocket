# pbsocket 架構及細節

<br>

---

<br>

前面兩個章節已經把最重要的部分講完了，剩下的部分其實就沒有什麼技術難度，純粹就是寫 socket 傳資料而已。

<br>

pbsocket 有 __client__ 與 __server__ 兩個部分，可以提供接收與發送 2 種功能，其中 client 端是抽象類別，因為有一個重要方法需要根據實際情況不同更改實現：

<br>

* [`PbClientSocket`](#1)

<br>

* [`PbServerSocket`](#2)

<br>
<br>

需要使用 pbsocket 時就 client 需要自行建立實作抽象的類別來完成， server 則不需要。下面會分別介紹一下 `PbClientSocket` 與 `PbServerSocket`。

<br>
<br>
<br>
<br>

<div id="1">


## `PbClientSocket`

<br>

其實內容沒有特別多，所以就直接把完整 code 貼上來解釋：

<br>

```py
import sys
from abc import abstractmethod
from socket import *

from pbsocket import ProtoData_pb2
from pbsocket.ProtobufVarint32LengthFieldTools import frameDecoder, frameEncoder


class PbClientSocket:

    def __init__(self, host='127.0.0.1', port=8080):
        self.ADDR = (host, port)
        self.tcpCliSocket = socket(AF_INET, SOCK_STREAM)  # AF_INET 是使用 IPv4 協定，SOCK_STREAM 是使用 TCP 協定


    @abstractmethod
    def processRecord(self, record):
        pass


    def sendRecord(self, record):
        try:
            record_node = record.SerializeToString()
            frame = frameEncoder(record_node)
            self.tcpCliSocket.send(frame)
        except ConnectionAbortedError:
            print('Connection has been terminated by DMServer on your host.')
            sys.exit(0)

    def processEnd(self):
        try:
            ending_signal = ProtoData_pb2.Record()
            ending_signal.signal = ending_signal.Signal.STOP
            self.sendRecord(ending_signal)
        except ConnectionAbortedError:
            print('Connection has been terminated by DMServer on your host.')
            sys.exit(0)

    def startUp(self):
        try:
            self.tcpCliSocket.connect(self.ADDR)
            while True:
                protobufdata = frameDecoder(self.tcpCliSocket)
                record = ProtoData_pb2.Record()
                record.ParseFromString(protobufdata)
                self.processRecord(record)
                if record.signal.__eq__(record.Signal.STOP):
                    self.processEnd()
                    break
            self.tcpCliSocket.close()
        except ConnectionAbortedError:
            print('Connection has been terminated by DMServer on your host.')
            sys.exit(0)
```

<br>

加上建構式一共有五個方法，下面會按照初始化，啟動，處理資料的流程來照順序說明：

<br>



<br>

* `__init__(self, host='127.0.0.1', port=8080):` 建構式：

  初始化方法主要是綁定 `host` 與 `port` 資訊在這個類別上。同時建立：socket `self.tcpCliSocket = socket(AF_INET, SOCK_STREAM)`， AF_INET 是使用 IPv4 協定，SOCK_STREAM 是使用 TCP 協定。

  <br>

* `startUp(self):` 啟動方法：

  啟動 socket 向目標 ip:port 連線，由於這邊是 Client，所以連線到 Server 之後，我們就開始接收資料。解碼需要調用到 `frameDecoder()`，解出的 bytes 資料再透供 protobuf 工具轉成 Record：`record.ParseFromString(protobufdata)`。最後再把 Record 交給由使用者實現的 `processRecord()` 抽象方法處理可用資料。

  <br>

* `sendRecord(self, record):` 寄送消息方法：

  因為設計時考慮資料處理完畢後，要回傳到 Server 端，所以也設計了 `sendRecord()` 方法。首先把 Record 序列化成 bytes：`record_node = record.SerializeToString()`，透過上一章節介紹的 `frameEncoder()` 方法為封包打上標頭：`frame = frameEncoder(record_node)`。最後由 socket 送出。

  <br>

* `processEnd(self):` 處理最後一筆消息方法：

  如果 Client 端收到 Server 傳來最後一筆 Record（滿足 `record.signal.__eq__(record.Signal.STOP)` 條件），就會執行這個方法。這個方法其實就是把這個 STOP signal 丟回去給 Server 而已。

  <br>

* `processRecord(self, record):` 抽象方法：

  這個方法要由繼承 PbClientSocket 的類別實現，自訂處理 Record 的商業邏輯，之後在下一個章節會示範如何實際使用繼承。

<br>
<br>
<br>
<br>

<div id="2">

## `PbServerSocket`

<br>

`PbServerSocket` 內容也不算多，加上建構式一供有 6 個方法，像上面 `PbClientSocket` 一樣，這邊也會分別講解每一個方法，整體 code 如下：

<br>

```py
import threading

from socket import *
from pbsocket import ProtoData_pb2
from pbsocket.ProtobufVarint32LengthFieldTools import frameEncoder, frameDecoder


class PbServerSocket:

    def __init__(self, record_list=[], host='127.0.0.1', port=8080):
        self.alive = False
        self.output_list = []
        self.record_list = record_list
        self.ADDR = (host, port)
        self.tcpServSocket = socket(AF_INET, SOCK_STREAM) # AF_INET 是使用 IPv4 協定，SOCK_STREAM 是使用 TCP 協定

    def sendRecord(self, conn):
        for record in self.record_list:
            binData = record.SerializeToString()  # 把 record 序列化成 bytes
            binData = frameEncoder(binData)  # 把 bytes_record 轉化為 varint32 訊框
            conn.send(binData)

    def recvRecord(self, conn, addr):
        while True:
            protobufdata = frameDecoder(conn)  # 解碼第一筆資料
            record = ProtoData_pb2.Record()
            record.ParseFromString(protobufdata)  # bytes 轉碼變 ProtoBuf 物件
            if record.signal.__eq__(record.Signal.NODE):
                self.output_list.append(record)
                print(record)
                continue
            if record.signal.__eq__(record.Signal.STOP):
                print('data transfrom already finished, close the connection : ', addr)
                conn.close()
                break

    def processConn(self, conn, addr):
        recordSender = threading.Thread(target=self.sendRecord, args=(conn,))
        recordRecver = threading.Thread(target=self.recvRecord, args=(conn, addr,))
        recordSender.start()
        recordRecver.start()

    def close(self):
        self.alive = False

    def startUp(self):
        self.alive = True
        self.tcpServSocket.bind(self.ADDR)
        self.tcpServSocket.listen(5)
        print('tcpServSocket start up successfully, server info : ', self.ADDR)
        while self.alive:
            conn, addr = self.tcpServSocket.accept()
            print('accepted connection from : ', addr)
            self.processConn(conn, addr)
```

<br>

以下列出 6 個方法，並分鱉講解。

<br>

* `__init__(self, record_list=[], host='127.0.0.1', port=8080):` 建構式：

  初始化建構式，宣告一些需要使用到的類別，尤其是 socket。

<br>

* `startUp(self):` 啟動方法：

  啟動方法，`self.tcpServSocket.listen(5)` 意為同時最多可以連線 5 個 Client。只要 Server 沒有關閉，就會一直接受 Connect 請求。有 connection 進連就丟給 `processConn(conn, addr)` 處理。

<br>

* `processConn(self, conn, addr):` 處理連線方法：

  處理連線請求的方法，當有連線時會啟動 2 個 socket，分別處裡 `sendRecord` 與 `recvRecord` 兩個事件，這兩個事件分別開 2 個 Thread 處理。

<br>

* `sendRecord(self, conn):` 寄送方法：

  分別將 record 做序列化（使用 protobuf 工具），並加入訊框頭。然後送出。

<br>

* `recvRecord(self, conn, addr):` 接收方法：

  接收資料後解碼訊框頭取的 protobufdata 資訊，將 bytes 資料轉換成 PbData（透過 protobuf 工具），判斷 Signal 是 `NODE` 或 `STOP` 來處理資料。

<br>

* `close(self):` 關閉方法：

  關閉 connection 的方法。通常情況下搭配偵測 Signal 為 `STOP` 使用。

<br>
<br>
<br>
<br>