import time
import can
import threading


# todo增加总线日志记录功能

class CANChannel:
    def __init__(self, interface, deviceChannel, receive_own_messages, bitrate, app_name, fd, data_bitrate):
        self.configDict = {"interface": interface, "deviceChannel": deviceChannel, "app_name": app_name,
                           "receive_own_messages": receive_own_messages, "fd": fd, "bitrate": bitrate,
                           "data_bitrate": data_bitrate}
        self.bus = can.ThreadSafeBus(interface=self.configDict["interface"], channel=self.configDict["deviceChannel"],
                                     app_name=self.configDict["app_name"],
                                     receive_own_messages=self.configDict["receive_own_messages"],
                                     fd=self.configDict["fd"], bitrate=self.configDict["bitrate"],
                                     data_bitrate=self.configDict["data_bitrate"])
        self.messageDict = {}
        self.messageMonitorFlag = threading.Event()
        self.messageMonitorFlag.clear()
        threading.Thread(target=self._onMessageReceived).start()

    def _stopMessageReceived(self):
        self.messageMonitorFlag.set()

    def _onMessageReceived(self):
        while not self.messageMonitorFlag.is_set():
            recvMessage = self.bus.recv(1)
            self.messageDict[recvMessage.arbitration_id] = recvMessage

    def sendMessage(self, msg: can.Message, cycleTime):
        if msg.arbitration_id not in self.sendMessageTask:
            self.sendMessageTask[msg.arbitration_id] = self.bus.send_periodic(msg, cycleTime, store_task=False)
            # self.messageDict[msg.arbitration_id] = msg
        else:
            self.updateMessage(msg)

    def updateMessage(self, msg: can.Message):
        if msg.arbitration_id in self.sendMessageTask:
            self.sendMessageTask[msg.arbitration_id].modify_data(msg)
            # self.messageDict[msg.arbitration_id] = msg
        else:
            raise RuntimeError("Please make sure the message(id: {}) is enabled for sending".format(msg.arbitration_id))

    def stopMessage(self, msg):
        id = msg.arbitration_id if isinstance(msg, can.Message) else int(msg)
        if id in self.sendMessageTask:
            self.sendMessageTask[id].stop()
            del self.sendMessageTask[id]
            self.bus.flush_tx_buffer()

    def stopAllMessage(self):
        self.bus.stop_all_periodic_tasks()
        self.sendMessageTask = {}
        self.bus.flush_tx_buffer()

    def getMessage(self, id):
        if id in self.messageDict:
            return self.messageDict[id]
        else:
            print(self.messageDict)
            raise ValueError("No message with id {} is received".format(id))

    def exit(self):
        self.stopAllMessage()
        self._stopMessageReceived()
        self.messageDict = {}

    def __del__(self):
        self.exit()


class Signal:
    def __init__(self, name, startBit, length, defaultValue, byteOrder):
        self.name = name
        self.startBit = startBit
        self.length = length
        self.defaultValue = defaultValue
        self.byteOrder = byteOrder
        self.rawValue = defaultValue
        self.valueParse = dict()

    def getValue(self):
        return self.rawValue

    def setValue(self, value):
        self.rawValue = value

class Frame:
    def __init__(self):
        self.messageDict = dict()   #Message.arbitration_id:Message
        self.signalDict = dict()    #Signal.name:Signal
        self.shortName = shortName
        self.frameLength = frameLength
        self.pduToFrameMap = pduToFrameMap

        #Frame中的信息与DBC文件的对应关系如表：
        # ARXML	                        DBC
        # PACKING-BYTE-ORDER	        Byte Order
        # MOST-SIGNIFICANT-BYTE-LAST	Intel
        # MOST-SIGNIFICANT-BYTE-FIRST	Motorola
        # FRAME-LENGTH	                Length

class Pdu:
    def __init__(self):
        self.signalDict = dict()



if __name__ == "__main__":
    # the example of how to send the message
    # ch0 = CANChannel(interface='vector', deviceChannel=0, app_name="Stark", receive_own_messages=False, fd=False,
    #               bitrate=500 * 1000, data_bitrate=None)
    #
    # # ch1 = CANChannel(interface='vector', deviceChannel=1, app_name="Stark", receive_own_messages=False, fd=True,
    # #               bitrate=500 * 1000, data_bitrate=2000 * 1000)
    #
    # message0 = can.Message(arbitration_id=0x12, dlc=8, is_extended_id=False, is_fd=False,
    #                        data=[0x1, 0x2, 0x3, 0x4, 0x5, 0, 0, 0])
    #
    # # message1 = can.Message(arbitration_id=0x22, dlc=8, is_extended_id=False, is_fd=True,
    # #                        data=[0x11, 0x22, 0x33, 0, 0, 0, 0, 0x99])
    #
    # # ch0.sendMessage(message0, cycleTime=0.2, timeout=0.2)
    # # ch1.sendMessage(message1, cycleTime=0.1, timeout=0.2)
    #
    # message3 = can.Message(arbitration_id=0x32, dlc=8, is_extended_id=False, is_fd=False,
    #                        data=[0x1, 0x2, 0x3, 0x4, 0x5, 0, 0, 0])
    # ch0.sendMessage(message0, 0.10)
    # # send_periodic(msg, period, duration=None, store_task=True)
    # ch0.sendMessage(message3, 0.20)
    # time.sleep(10)
    # print("start modify")
    # message0.data = [0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8]
    # ch0.updateMessage(message0)
    # message3.data = [0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8]
    # ch0.updateMessage(message3)
    # time.sleep(10)
    # print("start stop")
    # ch0.stopMessage(message3)
    # time.sleep(10)
    #
    # the example of how to get the message
    ch0 = CANChannel(interface='vector', deviceChannel=0, app_name="Stark", receive_own_messages=True, fd=False,
                     bitrate=500 * 1000, data_bitrate=500 * 1000)

    ch1 = CANChannel(interface='vector', deviceChannel=1, app_name="Stark", receive_own_messages=True, fd=True,
                     bitrate=500 * 1000, data_bitrate=2000 * 1000)

    # for i in ch0.bus:
    #     print(i)
    #     print(type(i))
    time.sleep(1)
    while True:
        message = ch0.getMessage(0xE5)
        # print(message)
    ch0.exit()
    ch1.exit()
