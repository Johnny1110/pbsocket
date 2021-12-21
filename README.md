# pbsocket（實現 protobuf 3 varint32RawHeader 協定的 python 資料傳輸 socket）

<br>

----------------------------------------------------

<br>

## 簡介

<br>

為了實現 Java 與 Python 之間做資料交換，所以這次使用 Google 推出的工具 __protobuf 3__。

Java 端有 __Netty__ 對 Protobuf 有良好的支援，所以就使用 Netty 來實作傳輸。具體細節就不放在本篇講解，Python 端目前有可以序列化 Protobuf 的工具，但是沒有支援封裝訊框（Frame）的功能。所以需要自己動手寫實現。 

本篇筆記就詳細說明手刻訊框協定的過程。

<br>
<br>

## 概述

<br>

簡介有提到使用了 Google 的 protobuf 協定，所以在真正開始編寫之前，徹底了解 protobuf 是非常有必要的一件事，所以筆記第一個部分會著重介紹 protobuf 是甚麼以及延伸的一些操作。其中涉及到一些協定 ( varint32 ) 也會詳細拆解做說明。第二個部分則會介紹如何實現這些協定 ( 也就是 [ProtobufVarint32LengthFieldTools.py](ProtobufVarint32LengthFieldTools.py) 的細節 )。第三部分則是介紹整個 pbsocket 架構以及細節。最後一部分是實際示範。


<br>
<br>

## 目錄

<br>

* [protobuf 以及 varint32](doc/protobuf&varint32/README.md)

* [實現 varint32 encoder 與 decoder (python 實作)](doc/varint32Encoder&Decoder/README.md)

* [pbsocket 架構及細節](doc/pbsocketArchitecture&Details/README.md)

* [實際使用](doc/demo/README.md)

