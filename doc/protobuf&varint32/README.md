# protobuf 以及 varint32

<br>

---

<br>

protobuf 是 Google 推出了一種資料格式，可以理解成 JSON XML 的一種。他的優勢是更小、更快，而且更簡潔，能夠節省網路與硬體資源，且你只需要定義一次資料結構，接著就會自動生成符合你程式語言的檔案，讓你能夠直接在你的程式上使用。

<br>

protobuf 3 的官方文件：https://developers.google.com/protocol-buffers/docs/proto3

<br>
<br>
<br>
<br>

## 大綱

<br>

* [下載編譯器](#1)

* [Protobuf 編寫&編譯](#2)

* [pbsocket 使用到的資料格式](#3)

* [在 Python 中使用](#4)

* [編碼與解碼 (varint32)](#5)

<br>
<br>
<br>
<br>

<div id="1">

## 下載編譯器

<br>

當然，protobuf 編譯工具是需要 download 的，官方釋出版放在 github 上：https://github.com/protocolbuffers/protobuf/releases

找最新版 download 下來並設定環境變數。像是我在編寫這份文件時是 2021/12/21，此時最新版本是 3.19.1，開發平台是 windows。所以可以下載這個：

<br>

![1](imgs/1.jpg)

<br>

環境變數設定就不演示了，一切設定好後就可以測試看看版號：

<br>

![2](imgs/2.jpg)

<br>
<br>
<br>
<br>

<div id="2">

## Protobuf 編寫&編譯

<br>

接下來簡單介紹一下 protobuf 編寫規範。__這邊只會挑出重點的說，如果要完全精通 protobuf 設計理念還是需要完整看過官方文件。__

<br>

以下是一段簡單的 `.proto` 文件：

```protobuf
syntax = "proto3";

/* SearchRequest represents a search query, with pagination options to
 * indicate which results to include in the response. */

message SearchRequest {
  string query = 1;
  int32 page_number = 2;  // Which page number do we want?
  int32 result_per_page = 3;  // Number of results to return per page.
}
```

<br>

* 第一行指定正在使用 `proto3` 語法。如果不寫明事 `proto3` 則默認使用 `proto2` 版。

* 隨後就事定義一個名為 `SearchRequest` 的 proto 消息，裡面有 `query` `page_number` `result_per_page` 三個 Field，型態分別是一個 string 與兩個 int32。

* Field 定義後面需要分配 Field Numbers，`query` 是 1 ，`page_number` 是 2，`result_per_page` 是 3。每一個 Field 都有一個唯一（unique）的編號。這用於再二進為位格式中標示出 Field。1 ~ 15 以內的數字占用 1 byte， 16 ~ 2047 需要占用到 2 個 bytes。

<br>

當我們像這樣定義好一個 `.proto` 文件之後就可以使用 protoc 工具來編譯成我們所需要的語言版本了。舉賴來說就是指定 java 的話就會編成 `.java` 文件，指定成 python 的話就會編成 `.py` 文件。

<br>

protobuf 支援以下幾種語言：

<br>

![3](imgs/3.jpg)

<br>

這邊示範一下編譯上面寫好的 SearchRequest，我們編譯 java 與 python 兩個版本：

<br>

```
$> protoc --python_out=. SearchRequest.proto

$> protoc --java_out=. SearchRequest.proto
```

<br>

![4](imgs/4.jpg)

<br>

編譯好後就可以在相同目錄中得到兩份文件：

* SearchRequest_pb2.py

* SearchRequestOuterClass.java

<br>

![5](imgs/5.jpg)

<br>
<br>
<br>
<br>

<div id="3">

## pbsocket 使用到的資料格式

<br>

其實 protobuf 的格式還有很多種，這邊一一列舉的話就像是在翻譯 copy 官方文件而已，所以我直接用這個工具專案使用到的資料格式進行講解，如果想更加深入知道所有資料格式的話可以去看看官方文件，上面都有很詳細的解釋。

<br>

先解釋一下為了滿足 pbsocket 的核心功能，我們需要用到怎樣的資料結構。

<br>

* 首先我們傳送資料要以一筆 `Record` 為一個單位，且這個 `Record` 需要標是出自己是一筆 `NODE`（節點） 資料還是一筆 `STOP`（終止）資料。因為需要讓接收端與發送端知道資料傳輸的結束 `Record` 才能關閉 socket 進行下一步工作，所以 `Record` 需要帶有一個 `Signal` 的標示來說明這個節點是否就是結束點。

* 一筆 `Record` 中可有多個資料欄位也就是 `cloumn`，所以需要用一個 `map` 來表示，會有點像這樣：

    ```java
    column = {
        '欄位一': 'A資料', // STRING
        '欄位二': '123', // INT
        '欄位三': `\0xFF\0xF0\0x0F\0x11...` //FILE
    }
    ```

* 上面提到的 column 需要存各種型態的資料，所以 map 中存放的值就需要特別設計，於是我們需要再多寫一個 `PbData` 資料格式。這個資料格式藥可以表達不同種資料型態 ( e.g: STRING, FLOAT, INT, FILE ... )

<br>

已知上面的幾點要求，所以就按照計畫設計 proto 資料結構：

<br>

### [`ProtoData.proto`](../../ProtoData.proto)

<br>

```protobuf
syntax = "proto3";

package com.frizo.lab.network;
option optimize_for = SPEED; // 編譯器將生成用於序列化、解析和對消息類型執行其他常見操作的代碼。這段代碼是高度優化的。(快速)
option java_outer_classname="ProtoData"; //指定輸出 java 格式的檔名

message Record {
    enum Signal { // 宣告枚舉 Singal 內有 NODE 與 STOP 兩種訊號
        NODE = 0;
        STOP = 1;
    };
    Signal signal = 1; // 宣告枚舉
    map<string, PbData> column = 2; // 宣告 map
}

message PbData{
    enum DataType { // 宣告枚舉  DataType 內有 4 種格式
        STRING = 0;
        FLOAT = 1;
        INT = 2;
        FILE = 3;
     };
    DataType dataType = 1; // 宣告枚舉
    bytes binaryData = 2; // 宣告 bytes
}
```

<br>

__為什麼 PbData 存放資料的格式要用到 bytes 呢 ? 因為當初設計時想到要設計一個連 file 都可以傳輸的應用，所以資料傳輸統一使用 btyes 格式。__


<br>
<br>
<br>
<br>

<div id="4">

## 在 Python 中使用

<br>


先把 `ProtoData.proto` 文件編譯成 .py 文件，接下來就要開始介紹如何在 python 中使用這個 proto 文件了。

<br>

在此之前要先安裝一下 protobuf 套件：

<br>

```sh
$> pip install protobuf
```

<br>

```py
import ProtoData_pb2

######################## 建立一筆 Record ##############################

record = ProtoData_pb2.Record()
record.signal = record.Signal.NODE # 宣告這是一個 NODE(非最後一節資料)

# 第一個 PbData
data1 = ProtoData_pb2.PbData()
data1.dataType = data1.DataType.STRING
data1.binaryData = "Hello Wolrd!".encode('utf-8')

# 第二個 PbData
data2 = ProtoData_pb2.PbData()
data2.dataType = data2.DataType.INT
data2.binaryData = int(21).to_bytes(4, byteorder='big')

# 將以上 2 個 PbData 放入 record 中
record.column['msg'].CopyFrom(data1)
record.column['age'].CopyFrom(data2)

######################################################################

######################## 讀取一筆 Record ##############################

msgBinaryData = record.column['msg'].binaryData
ageBinaryData = record.column['age'].binaryData

print(record)
print('-'*40)

# 將 bytes 轉成對應格式資料
print(msgBinaryData.decode("utf-8"))  # bytes > string
print(int.from_bytes(ageBinaryData, byteorder='big'))  # bytes > int

######################################################################
```

<br>

console：

<br>

```
column {
  key: "age"
  value {
    dataType: INT
    binaryData: "\000\000\000\025"
  }
}
column {
  key: "msg"
  value {
    binaryData: "Hello Wolrd!"
  }
}

----------------------------------------
Hello Wolrd!
21

Process finished with exit code 0
```

<br>
<br>
<br>
<br>

<div id="5">

## 編碼與解碼 (varint32)

<br>

來到最關鍵的一個部份了，關於 protobuf 的編碼。protubuf 使用 varint32 的編碼規範，google 的官方文件：

https://developers.google.com/protocol-buffers/docs/encoding

<br>

這邊我會盡力解釋 varint32 的原裡。

<br>

在研究 varint32 之前，首先需要具備基本的 2 與 16 進制理解計算能力（高中數學），接下來就稍微熱身一下進行兩組簡單的運算。

<br>

1. 十進制 129 轉 二進制

2. 十進制 300 轉  二進制

<br>

第 1 題答案：　129 = 1000 0001

第 2 題答案：　300 = 0001 0010 1100

<br>

熱身完畢，接下來簡單解釋一下 varint32 到底是甚麼。

<br>

---

<br>

### Tips : 關於 int 是 4 bytes 這件事

<br>

在我們的認知中，一個 `int` 需要占用 4 個 bytes，至於為甚麼是 4 bytes，解釋起來可以大致裡結為 32 位元處裡器一次可以處裡 4 個 bytes 資料所以 int 是 4 bytes，64 位元 CPU 可以處裡 8 bytes 資料，所以 int 可以是 8 bytes。或許是因為語言需要統一 int 的占用位元數，所以部分語言統一 int 必須是 32 位元，java 就是這樣的。

<br>

---

<br>

varint32 講白話就是可以動態改變大小的 int，不必所有數值都占用到 4 bytes，最少使用到 1 bytes 就可以了。具體如何做到呢？我們就拿 129 舉例。

如果要使用 int 表示 129，在轉換成 bit 資料後會是這樣：

```
0000 0000 0000 0000 0000 0000 1000 0001
```

varint32 的表達法以 1 個 bytes 為單位一共有 8 bit 可以用於表達。但是這 8 個 bit 中需要讓最左邊的 1 個 bit 用來表達是否是結尾。也就是說 8 個 bit 裡面只有 7 個 bit 可以存放資料，要留一個 bit 來表達後面是否還有資料。

試著把數字 129(`1000 0001`) 用 varint32 表達會像是這樣：

```
_000 0001   第一個 bytes 取 129 的 1~7 位，最左邊留出一位用於表達是否有後續資料。
_000 0001   第二個 bytes 取 129 的 8~14 位，最左邊留出一位用於表達是否有後續資料。
```

<br>

每個 bytes 最左邊那個位元用於表達是否有接續資料，有就填 1 沒有就是 0，所以補齊上面的 `_`，結果如下：

<br>

```
_000 0001 => 1000 0001   第一個 bytes 之後有接續資料，所以左邊位元補 1。
_000 0001 => 0000 0001   第二個 bytes 之後沒有接續資料，所以左邊位元補 0。
```

<br>

最終結果 129 轉 varint32 = `1000 0001 0000 0001`。使用 2 bytes 表達。

<br>
<br>
<br>
<br>

如果要使用 int 表示 300，在轉換成 bit 資料後會是這樣：

```
0000 0000 0000 0000 0000 0001 0010 1100
```

試著把數字 300(`0001 0010 1100`) 用 varint32 表達會像是這樣：

```
_010 1100  第一個 bytes 取 1~7 位，左邊留空用來表達後續是否有資料。
_000 0010  第二個 bytes 取 8~14 位，左邊留空用來表達後續是否有資料。
```

補上最左邊的位元：

```
_010 1100 => 1010 1100  第一個 byte
_000 0010 => 0000 0010  第二個 byte
```

最終結果 300 轉 varint32 = `1010 1100 0000 0010`。

<br>
<br>
<br>
<br>

理解上面的理論之後，可以試著把 varint32 手動還原回數字試試。

`1010 1100 0000 0010` 轉成 int 數字：

```
1010 1100 -> 010 1100
0000 0010 -> 000 0010
```

拼接這兩個 7 bits：

```
010 1100 ++ 000 0010 => 000 0010 010 1100 => 0001 0010 1100 =>  256 + 32 + 8 + 4 => 300
```

<br>

