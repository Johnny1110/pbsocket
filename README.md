# pbsocket（實現 protobuf 3 varint32RawHeader 協定的 python 資料傳輸 socket）

<br>

為了實現 Java 與 Python 之間做資料交換，所以這次使用 Google 推出的工具 __protobuf 3__。

Java 端有 __Netty__ 對 Protobuf 有良好的支援，所以就使用 Netty 來實作傳輸。具體細節就不放在本篇講解，Python 端目前有可以序列化 Protobuf 的工具，但是沒有支援封裝訊框（Frame）的功能。所以需要自己動手寫實現。 

本篇筆記就詳細說明手刻訊框協定的過程。

<br>

----

<br>
<br>

## 目錄

<br>

