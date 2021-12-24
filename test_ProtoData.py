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