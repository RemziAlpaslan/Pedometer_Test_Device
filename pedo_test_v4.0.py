import sys
import os
import time
from time import sleep
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout,  QLineEdit, QLabel, QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import QTimer, Qt, QDateTime
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ppk2_api.ppk2_api import PPK2_API
import subprocess

# pigpiod komutunu çalıştır
result = subprocess.run(['sudo', 'pigpiod'], capture_output=True, text=True)
# Çıktıyı yazdır
print(result.stdout)
print(result.stderr)

from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import paho.mqtt.client as mqtt
import json
import requests





if sys.argv[1]=="1":
    servoPın=19
    setRight=0
    deviceId="D4D521ADF13C"
    
else:
    servoPın=18
    setRight=1
    deviceId="E64B4CE7D38B"
    
    




# Database initialization

url = 'https://pedotestapi.antag.com.tr/PedometerTest/AddCurrentValues'
headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
}


# Servo initialization


factory = PiGPIOFactory()
servo = Servo(servoPın, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)



# Mqtt initialization

# MQTT broker bilgileri
broker_address = "192.168.0.199"
broker_port = 1883  # Varsayılan MQTT portu
# Mesajları saklamak için bir liste
received_messages = 0
messages_sending = False

# Bağlantı durumu callback fonksiyonu
def on_connect(client, userdata, flags, rc):
    print("Bağlandı. Bağlantı kodu:", rc)
    # Abone olunacak konu (topic) burada belirtilir
    client.subscribe("/join")
# Mesaj alma callback fonksiyonu
def on_message(client, userdata, message):
    global received_messages
    global messages_sending
    received_messages=json.loads(message.payload.decode())['deviceName']
    messages_sending = True
    print("on_mesages",sys.argv[1],message.payload.decode())
    
# Bağlantı kesilme callback fonksiyonu
def on_disconnect(client, userdata, rc):
    print("Bağlantı kesildi. Kod:", rc)

# MQTT istemci oluşturma
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect


# Bu class nordicten veri almak için kullanılır.
class MyPPK2_API(PPK2_API):
    @staticmethod
    def list_devices(serialnumber):
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        #print(ports)
        if os.name == 'nt':
            devices = [port.device for port in ports if port.description.startswith("nRF Connect USB CDC ACM") and port.serial_number==serialnumber]
        else:
            devices = [port.device for port in ports if port.product == 'PPK2' and port.serial_number==serialnumber]
        return devices



# Bu class canlı grafiğin çizdirilmesinde kullanılır.
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        
        
# Bu class pencere açma ve pencere işlemlerinde kullanılır
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Tanımlamaları yaptım
        self.testing = False
        self.ppk2İnitStoper = True
        
        screen = QApplication.primaryScreen().availableGeometry()
        print(screen.width(),screen.height())
        self.setGeometry((screen.width()// 2)*setRight, 0, screen.width() // 2, screen.height())
        self.setWindowTitle("PPK2 Live Plot Example")
        # Pencere açmayı sağlar
        
        self.palette = QPalette()
        self.palette.setColor(QPalette.Base, QColor('white'))  # Arka plan rengi
        self.palette.setColor(QPalette.Text, QColor('black'))  # Metin rengi
        
        self.paletteGreen = QPalette()
        self.paletteGreen.setColor(QPalette.Base, QColor('lightgreen'))  # Arka plan rengi
        self.paletteGreen.setColor(QPalette.Text, QColor('black'))  # Metin rengi
        
        self.paletteRed = QPalette()
        self.paletteRed.setColor(QPalette.Base, QColor('red'))  # Arka plan rengi
        self.paletteRed.setColor(QPalette.Text, QColor('black'))  # Metin rengi
    
        
        vBoxMain = QVBoxLayout()
        vBoxIdArg = QVBoxLayout()
        hBoxIdtimeSituation=QHBoxLayout()
        vBoxDatetime=QVBoxLayout()
        vBoxworktimeSituation=QVBoxLayout()
        hBoxMaxMinAvg=QHBoxLayout()
        hBoxJoin=QHBoxLayout()
        hBoxDK1=QHBoxLayout()
        hBoxYK1=QHBoxLayout()
        hBoxDK2=QHBoxLayout()
        hBoxYK2=QHBoxLayout()
        hBoxDK3=QHBoxLayout()
        hBoxYK3=QHBoxLayout()
        hBoxDKOrt=QHBoxLayout()
        hBoxYKOrt=QHBoxLayout()
        hBoxTestBaşarılı=QHBoxLayout()
        hBoxButton=QHBoxLayout()
        
        
        
        Font = QFont()
        #Font.setPointSize(25)  # Yazı boyutunu 20 yap
        
        self.devicesArg = QLineEdit()
        self.devicesArg.setText("Cihaz: "+sys.argv[1])
        self.devicesArg.setReadOnly(True)
        self.devicesArg.setAlignment(Qt.AlignCenter)
        self.devicesArg.setFont(Font)
        vBoxIdArg.addWidget(self.devicesArg)
        
        
        self.productionTimeIdValue = QLineEdit()
        self.productionTimeIdValue.setText("????????")
        self.productionTimeIdValue.setReadOnly(True)
        self.productionTimeIdValue.setAlignment(Qt.AlignCenter)
        self.productionTimeIdValue.setFont(Font)
        vBoxIdArg.addWidget(self.productionTimeIdValue)
        hBoxIdtimeSituation.addLayout(vBoxIdArg)
        
        
        
        #Font.setPointSize(20)
        
        self.timeValue = QLineEdit()
        self.timeValue.setText("???")
        self.timeValue.setReadOnly(True)
        self.timeValue.setFont(Font)
        vBoxDatetime.addWidget(self.timeValue)
        
        
        self.dateValue = QLineEdit()
        self.dateValue.setText("???")
        self.dateValue.setReadOnly(True)
        self.dateValue.setFont(Font)
        vBoxDatetime.addWidget(self.dateValue)
        hBoxIdtimeSituation.addLayout(vBoxDatetime)
        vBoxMain.addLayout(hBoxIdtimeSituation)
        
        
        self.testWorkTime = QLineEdit()
        self.testWorkTime.setText("???")
        self.testWorkTime.setReadOnly(True)
        self.testWorkTime.setFont(Font)
        vBoxworktimeSituation.addWidget(self.testWorkTime)
        
        
        self.situationValue = QLineEdit()
        self.situationValue.setText("???")
        self.situationValue.setReadOnly(True)
        self.situationValue.setFont(Font)
        vBoxworktimeSituation.addWidget(self.situationValue)
        hBoxIdtimeSituation.addLayout(vBoxworktimeSituation)
        
        
        
        self.canvas = MplCanvas(self, width=15, height=20, dpi=100)
        #self.canvas.setFixedWidth(1400) # sonra açılacak
        vBoxMain.addWidget(self.canvas)
        # Pencerede canlı grafiği gösterir
        
        
        self.maxText = QLineEdit()
        self.maxText.setText("???")
        self.maxText.setReadOnly(True)
        self.maxText.setFont(Font)
        hBoxMaxMinAvg.addWidget(self.maxText)
        
        
        self.minText = QLineEdit()
        self.minText.setText("???")
        self.minText.setReadOnly(True)
        self.minText.setFont(Font)
        hBoxMaxMinAvg.addWidget(self.minText)
        
        
        self.avgText = QLineEdit()
        self.avgText.setText("???")
        self.avgText.setReadOnly(True)
        self.avgText.setFont(Font)
        hBoxMaxMinAvg.addWidget(self.avgText)
        vBoxMain.addLayout(hBoxMaxMinAvg)
    
        
        
        self.joinAkımText = QLineEdit()
        self.joinAkımText.setText("Join Akımı:")
        self.joinAkımText.setReadOnly(True)
        self.joinAkımText.setFont(Font)
        hBoxJoin.addWidget(self.joinAkımText)
        
        
        self.joinAkımValue = QLineEdit()
        self.joinAkımValue.setText("???")
        self.joinAkımValue.setReadOnly(True)
        self.joinAkımValue.setFont(Font)
        hBoxJoin.addWidget(self.joinAkımValue)
        vBoxMain.addLayout(hBoxJoin)
        
        
        self.dikKonum1Text = QLineEdit()
        self.dikKonum1Text.setText("Dik Konum 1:")
        self.dikKonum1Text.setReadOnly(True)
        self.dikKonum1Text.setFont(Font)
        hBoxDK1.addWidget(self.dikKonum1Text)
        
        self.dikKonum1Value = QLineEdit()
        self.dikKonum1Value.setText("???")
        self.dikKonum1Value.setReadOnly(True)
        self.dikKonum1Value.setFont(Font)
        hBoxDK1.addWidget(self.dikKonum1Value)
        vBoxMain.addLayout(hBoxDK1)
        
        self.yatayKonum1Text = QLineEdit()
        self.yatayKonum1Text.setText("Yatay Konum 1:")
        self.yatayKonum1Text.setReadOnly(True)
        self.yatayKonum1Text.setFont(Font)
        hBoxYK1.addWidget(self.yatayKonum1Text)
       
        
        self.yatayKonum1Value = QLineEdit()
        self.yatayKonum1Value.setText("???")
        self.yatayKonum1Value.setReadOnly(True)
        self.yatayKonum1Value.setFont(Font)
        hBoxYK1.addWidget(self.yatayKonum1Value)
        vBoxMain.addLayout(hBoxYK1)
        
        self.dikKonum2Text = QLineEdit()
        self.dikKonum2Text.setText("Dik Konum 2:")
        self.dikKonum2Text.setReadOnly(True)
        self.dikKonum2Text.setFont(Font)
        hBoxDK2.addWidget(self.dikKonum2Text)
        
        self.dikKonum2Value = QLineEdit()
        self.dikKonum2Value.setText("???")
        self.dikKonum2Value.setReadOnly(True)
        self.dikKonum2Value.setFont(Font)
        hBoxDK2.addWidget(self.dikKonum2Value)
        vBoxMain.addLayout(hBoxDK2)
        
        self.yatayKonum2Text = QLineEdit()
        self.yatayKonum2Text.setText("Yatay Konum 2:")
        self.yatayKonum2Text.setReadOnly(True)
        self.yatayKonum2Text.setFont(Font)
        hBoxYK2.addWidget(self.yatayKonum2Text)
 
        
        self.yatayKonum2Value = QLineEdit()
        self.yatayKonum2Value.setText("???")
        self.yatayKonum2Value.setReadOnly(True)
        self.yatayKonum2Value.setFont(Font)
        hBoxYK2.addWidget(self.yatayKonum2Value)
        vBoxMain.addLayout(hBoxYK2)
        
        self.dikKonum3Text = QLineEdit()
        self.dikKonum3Text.setText("Dik Konum 3:")
        self.dikKonum3Text.setReadOnly(True)
        self.dikKonum3Text.setFont(Font)
        hBoxDK3.addWidget(self.dikKonum3Text)
        
        
        self.dikKonum3Value = QLineEdit()
        self.dikKonum3Value.setText("???")
        self.dikKonum3Value.setReadOnly(True)
        self.dikKonum3Value.setFont(Font)
        hBoxDK3.addWidget(self.dikKonum3Value)
        vBoxMain.addLayout(hBoxDK3)
        
        self.yatayKonum3Text = QLineEdit()
        self.yatayKonum3Text.setText("Yatay Konum 3:")
        self.yatayKonum3Text.setReadOnly(True)
        self.yatayKonum3Text.setFont(Font)
        hBoxYK3.addWidget(self.yatayKonum3Text)
        
        
        
        self.yatayKonum3Value = QLineEdit()
        self.yatayKonum3Value.setText("???")
        self.yatayKonum3Value.setReadOnly(True)
        self.yatayKonum3Value.setFont(Font)
        hBoxYK3.addWidget(self.yatayKonum3Value)
        vBoxMain.addLayout(hBoxYK3)
        
        #Font.setPointSize(35)
        
        self.dikKonumOrtText = QLineEdit()
        self.dikKonumOrtText.setText("Dik Konum Ort:")
        self.dikKonumOrtText.setReadOnly(True)
        self.dikKonumOrtText.setFont(Font)
        hBoxDKOrt.addWidget(self.dikKonumOrtText)
        
        
        self.dikKonumOrtValue = QLineEdit()
        self.dikKonumOrtValue.setText("???")
        self.dikKonumOrtValue.setReadOnly(True)
        self.dikKonumOrtValue.setFont(Font)
        hBoxDKOrt.addWidget(self.dikKonumOrtValue)
        vBoxMain.addLayout(hBoxDKOrt)
        
        self.yatayKonumOrtText = QLineEdit()
        self.yatayKonumOrtText.setText("Yatay Konum Ort:")
        self.yatayKonumOrtText.setReadOnly(True)
        self.yatayKonumOrtText.setFont(Font)
        hBoxYKOrt.addWidget(self.yatayKonumOrtText)
        
        self.yatayKonumOrtValue = QLineEdit()
        self.yatayKonumOrtValue.setText("???")
        self.yatayKonumOrtValue.setReadOnly(True)
        self.yatayKonumOrtValue.setFont(Font)
        hBoxYKOrt.addWidget(self.yatayKonumOrtValue)
        vBoxMain.addLayout(hBoxYKOrt)
        
        #Font.setPointSize(20)
        
        self.testBaşarılıText = QLineEdit()
        self.testBaşarılıText.setText("Test Durumu:")
        self.testBaşarılıText.setReadOnly(True)
        self.testBaşarılıText.setFont(Font)
        hBoxTestBaşarılı.addWidget(self.testBaşarılıText)
        
        self.testBaşarılıValue = QLineEdit()
        self.testBaşarılıValue.setText("???")
        self.testBaşarılıValue.setReadOnly(True)
        self.testBaşarılıValue.setFont(Font)
        hBoxTestBaşarılı.addWidget(self.testBaşarılıValue)
        vBoxMain.addLayout(hBoxTestBaşarılı)
        
        
        #Font.setPointSize(30)
        self.butonStartTest = QPushButton("Start/Stop Test", self)
        self.butonStartTest.clicked.connect(self.startTest)
        self.butonStartTest.setFixedHeight(screen.height()//7)
        self.butonStartTest.setFont(Font)
        self.butonStartTest.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; /* Beyaz */
                color: #000000; /* Siyah  */
                border: 2px solid #000000; /* Siyah sınır */
                border-radius: 10px; /* Köşeleri yuvarla */
            }
        """)
        hBoxButton.addWidget(self.butonStartTest) 
        
        self.buttonTestSituation = QPushButton("Test Başarılı Onaylıyorum", self)
        self.buttonTestSituation.clicked.connect(self.sendData)
        self.buttonTestSituation.setFixedHeight(screen.height()//7)
        self.buttonTestSituation.setFont(Font)
        self.buttonTestSituation.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; /* Beyaz */
                color: #000000; /* Siyah  */
                border: 2px solid #000000; /* Siyah sınır */
                border-radius: 10px; /* Köşeleri yuvarla */
            }
        """)
        hBoxButton.addWidget(self.buttonTestSituation) 
        vBoxMain.addLayout(hBoxButton)
        
        #Font.setPointSize(20)
        
        
        
        # Nordik' e Bağlanma
        self.ppk2s_connected = MyPPK2_API.list_devices(deviceId)
        print(self.ppk2s_connected)
        if len(self.ppk2s_connected) == 1:
            self.ppk2_port = self.ppk2s_connected[0]
            print(f'Found PPK2 at {self.ppk2_port}')
            try:
                self.ppk2_test = MyPPK2_API(self.ppk2_port, timeout=1, write_timeout=1, exclusive=True)
                self.ppk2_test.get_modifiers()
                self.ppk2_test.set_source_voltage(3300)
                self.ppk2_test.use_ampere_meter()  # set ampere meter mode
                self.ppk2_test.toggle_DUT_power("OFF")  # enable DUT power
                self.ppk2İnitStoper = False
            except Exception as e :
                return e    
        else:
            print(f'Too many connected PPK2\'s: {self.ppk2s_connected}')
            self.situationValue.setText("PPK2 hatası")
            self.situationValue.setPalette(self.paletteRed)
            
        # Broker' a bağlanma
        try:
            client.connect(broker_address, broker_port,30)
        except Exception as e:
                print(f"Bağlantı kurulamadı: {e}")
                self.situationValue.setText("MQTT hatası")
                self.situationValue.setPalette(self.paletteRed)
        client.loop_start()
        
        
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(vBoxMain)
        
        self.plotTimer = QTimer()
        self.plotTimer.setInterval(1000)  # Update every 10 ms
        self.plotTimer.timeout.connect(self.update_plot)
        
        
        self.textTimer = QTimer()
        self.textTimer.setInterval(1000)  # Update every 1000 ms
        self.textTimer.timeout.connect(self.update_text)
        
        
        self.timeTimer = QTimer(self)
        self.timeTimer.timeout.connect(self.update_datetime)
        self.timeTimer.start(1000)  # 1000 milisaniyede bir (1 saniye)
        # İlk güncelleme için tarih ve saati ayarla
        self.update_datetime()
        
        self.show() # showFullScreen e sonra çevirilecek
        self.workTime=0
        self.join = 0
        self.maxValue = 0
        self.minValue = 0
        self.avgValue = 0
        self.dikKonum1 = []
        self.yatayKonum1 = []
        self.dikKonum2 = []
        self.yatayKonum2 = []
        self.dikKonum3 = []
        self.yatayKonum3 = []
        self.dikKonumOrt = []
        self.yatayKonumOrt = []
        
        self.mqttTest=False
        
        
    def update_datetime(self):
        current_datetime = QDateTime.currentDateTime()

        # Saat ve tarih formatlarını belirle
        time_format = 'hh:mm:ss'
        date_format = 'dd.MM.yyyy'

        # Formatları kullanarak saat ve tarihi al
        display_time = current_datetime.toString(time_format)
        display_date = current_datetime.toString(date_format)

        # QLineEdit'lere yazdır
        self.timeValue.setText(display_time)
        self.dateValue.setText(display_date)
    
    def startTest(self):
        if self.testing:
            self.stop_test()
        else:
            self.start_test()
    
        
        
    def start_test(self):
        try:
            self.ppk2s_connected = MyPPK2_API.list_devices(deviceId)
            print(self.ppk2s_connected)
            if len(self.ppk2s_connected) == 1:
                self.ppk2_port = self.ppk2s_connected[0]
                print(f'Found PPK2 at {self.ppk2_port}')
                try:
                    self.ppk2_test = MyPPK2_API(self.ppk2_port, timeout=1, write_timeout=1, exclusive=True)
                    self.ppk2_test.get_modifiers()
                    self.ppk2_test.set_source_voltage(3300)
                    self.ppk2_test.use_ampere_meter()  # set ampere meter mode
                    self.ppk2_test.toggle_DUT_power("OFF")  # enable DUT power
                    self.ppk2İnitStoper = False
                except Exception as e :
                    print(e)
            else:
                print(f'Too many connected PPK2\'s: {self.ppk2s_connected}')
                self.situationValue.setText("PPK2 hatası")
                self.situationValue.setPalette(self.paletteRed)
            
            if not client.is_connected():
                print("Bağlantı kayboldu, yeniden bağlanılıyor...")
                try:
                    client.reconnect()
                except Exception as e:
                    print(f"Bağlantı yeniden kurulamadı: {e}")
                    self.situationValue.setText("MQTT hatası")
                    self.situationValue.setPalette(self.paletteRed)
                
                
            
            
            if len(self.ppk2s_connected) == 1 and client.is_connected():
                self.ppk2_test.toggle_DUT_power("ON")  # enable DUT power
                self.ppk2_test.start_measuring()  # start measuring
                self.start_time = time.time()
                self.situationValue.setText("Test Başladı")
                self.Time=time.time()
                self.plotTimer.start()
                self.textTimer.start()
            
                self.x_data=[]
                self.y_data=[]
                self.x_dataMini=[]
                self.y_dataMini=[]
                
                self.join = 0
                self.maxValue = 0
                self.minValue = 0
                self.avgValue = 0
                self.dikKonum1 = []
                self.yatayKonum1 = []
                self.dikKonum2 = []
                self.yatayKonum2 = []
                self.dikKonum3 = []
                self.yatayKonum3 = []
                self.dikKonumOrt = []
                self.yatayKonumOrt = []

                self.joinAkımText.setPalette(self.palette)
                self.dikKonum1Text.setPalette(self.palette)
                self.yatayKonum1Text.setPalette(self.palette)
                self.dikKonum2Text.setPalette(self.palette)
                self.yatayKonum2Text.setPalette(self.palette)
                self.dikKonum3Text.setPalette(self.palette)
                self.yatayKonum3Text.setPalette(self.palette)
                self.dikKonumOrtText.setPalette(self.palette)
                self.yatayKonumOrtText.setPalette(self.palette)
                self.testBaşarılıText.setPalette(self.palette)
                self.productionTimeIdValue.setPalette(self.palette)
                self.situationValue.setPalette(self.palette)
                self.dikKonumOrtValue.setPalette(self.palette)
                self.yatayKonumOrtValue.setPalette(self.palette)
                self.buttonTestSituation.setStyleSheet("""
                    QPushButton {
                        background-color: #FFFFFF; /* Beyaz */
                        color: #000000; /* Siyah  */
                        border: 2px solid #000000; /* Siyah sınır */
                        border-radius: 10px; /* Köşeleri yuvarla */
                    }
                """)
                self.butonStartTest.setStyleSheet("""
                    QPushButton {
                        background-color: #FFFFFF; /* Beyaz */
                        color: #000000; /* Siyah  */
                        border: 2px solid #000000; /* Siyah sınır */
                        border-radius: 10px; /* Köşeleri yuvarla */
                    }
                """)
                
                self.joinAkımValue.setText("???")
                self.timeValue.setText("???")
                self.dateValue.setText("???")
                self.testWorkTime.setText("???")
                self.joinAkımValue.setText("???")
                self.dikKonum1Value.setText("???")
                self.yatayKonum1Value.setText("???")
                self.dikKonum2Value.setText("???")
                self.yatayKonum2Value.setText("???")
                self.dikKonum3Value.setText("???")
                self.yatayKonum3Value.setText("???")
                self.dikKonumOrtValue.setText("???")
                self.yatayKonumOrtValue.setText("???")
                self.testBaşarılıValue.setText("???")
                self.productionTimeIdValue.setText("????????")
                
                self.mqttTest=False
                self.isTestStarted=False
                self.deletstopper=True
                self.mqttstopper=True
                self.pedometreID=None
                self.testing = True
                global messages_sending
                messages_sending = False
                
                self.canvas.axes.cla()  # Clear the canvas.
                
        except Exception as e :
            return e

    
    def stop_test(self):
        try:
            self.ppk2_test.toggle_DUT_power("OFF")  # disable DUT power
            self.situationValue.setText("Test Durdu" )
            self.testing = False
            self.plotTimer.stop()
            self.textTimer.stop()
            servo.mid()
            sleep(1)

        except Exception as e :
            return e
    
    def update_plot(self):
        try: 
            oneSecondtime=time.time()
            for i in range(100):
                read_data = self.ppk2_test.get_data()
                if read_data != b'':
                    samples, raw_digital = self.ppk2_test.get_samples(read_data)
                    avg_sample = sum(samples) / len(samples)
                    current_time = self.Time - self.start_time
                    self.x_data.append(current_time)
                    self.Time = time.time()
                    self.y_data.append(avg_sample)
                    self.y_dataMini.append(self.y_data[-1])
                    self.x_dataMini.append(self.x_data[-1])

                    #print(f"Average of {len(samples)} samples is: {avg_sample}uA")
                    #print()
                    if time.time()-oneSecondtime>=1:
                        break
                    
                    if self.isTestStarted:
                        time.sleep(0.001)
                    else:
                        time.sleep(0.01)
                    
                    #print("########################################################")
                    global messages_sending
                    #print(self.mqttstopper,messages_sending,self.join>30000)
                    if self.mqttstopper and messages_sending and self.join>30000:
                        self.pedometreID=received_messages
                        self.productionTimeIdValue.setText(str(self.pedometreID))
                        self.productionTimeIdValue.setPalette(self.paletteGreen)
                        self.mqttTest=True
                        self.mqttstopper=False
                    else:
                        messages_sending = False
                    #print(received_messages)
                    #print("########################################################")
            
           
                        
                        
            self.canvas.axes.cla()  # Clear the canvas.
            self.canvas.axes.plot(self.x_data, self.y_data, 'r')
            self.canvas.draw()
            
            self.maxValue = round(max(self.y_dataMini),2)
            self.minValue = round(min(self.y_dataMini),2)
            self.avgValue = round(sum(self.y_dataMini)/len(self.x_dataMini),2)
            
            self.y_dataMini=[]
            self.x_dataMini=[]
            
            if time.time() - self.start_time < 6:
                self.join = max(self.y_data)
            
            if self.isTestStarted:
                self.situationValue.setText("Deepsleep Testi")
            else:
                self.situationValue.setText("Join Testi")
            
            if self.join<30000 and time.time()-self.start_time>10:
                self.situationValue.setText("Join bulunamadı")
                self.situationValue.setPalette(self.paletteRed)
                
            if self.avgValue>4 and time.time()-self.start_time>10:
                self.situationValue.setText("Deepsleep bulunamadı")
                self.situationValue.setPalette(self.paletteRed)
                
                
            
            
            if self.join>30000 and self.avgValue<4:
                self.isTestStarted = True
                if len(self.dikKonum1)<2:
                    self.dikKonum1.append(self.avgValue)
                    
                elif len(self.yatayKonum1)<2:
                    if len(self.yatayKonum1)==0:
                        servo.min()
                        sleep(1)
                    self.yatayKonum1.append(self.avgValue)
                
                elif len(self.dikKonum2)<2:
                    if len(self.dikKonum2)==0:
                        servo.mid()
                        sleep(1)
                    self.dikKonum2.append(self.avgValue)
                    
                elif len(self.yatayKonum2)<2:
                    if len(self.yatayKonum2)==0:
                        servo.max()
                        sleep(1)
                    self.yatayKonum2.append(self.avgValue)
                    
                elif len(self.dikKonum3)<2:
                    if len(self.dikKonum3)==0:
                        servo.mid()
                        sleep(1)
                    self.dikKonum3.append(self.avgValue)
                    
                elif len(self.yatayKonum3)<2:
                    if len(self.yatayKonum3)==0:
                        servo.min()
                        sleep(1)
                    self.yatayKonum3.append(self.avgValue)
                
                
                    
                if len(self.yatayKonum3)==2 and len(self.dikKonumOrt)==0:
                    self.dikKonumOrt.append(self.dikKonum1[-1])
                    self.dikKonumOrt.append(self.dikKonum2[-1])
                    self.dikKonumOrt.append(self.dikKonum3[-1])
                    
                if len(self.yatayKonum3)==2 and len(self.yatayKonumOrt)==0:
                    self.yatayKonumOrt.append(self.yatayKonum1[-1])
                    self.yatayKonumOrt.append(self.yatayKonum2[-1])
                    self.yatayKonumOrt.append(self.yatayKonum3[-1])

            
            if self.isTestStarted:
                if self.deletstopper:
                    self.deletstoppertime=self.x_data[-1]
                    self.x_data=[self.x_data[-1]]
                    self.y_data=[self.y_data[-1]]
                    self.deletstopper=False
            
            self.Time=time.time()
        
        except Exception as e:
            return e
            
        
        
        
            
            
                    
        
        
            
            
                
            

            
                    
                 
        

    
    def update_text(self):
        try:
            self.testWorkTime.setText(str(round(time.time()-self.start_time,2))+" s")
            
            self.maxText.setText("Max: "+str(self.maxValue)+" uA")
            self.minText.setText("Min: "+str(self.minValue)+" uA")      
            self.avgText.setText("Avg: "+str(self.avgValue)+" uA")
            
            
            
            self.joinAkımValue.setText(str(round(self.join/1000),)+" mA")
            if self.join>=30000:
                self.joinAkımText.setPalette(self.paletteGreen)
                joinTest = True
            else:
                self.joinAkımText.setPalette(self.paletteRed)
                joinTest = False
                
            if self.isTestStarted:
                if self.mqttTest:
                    self.productionTimeIdValue.setPalette(self.paletteGreen)
                else:
                    self.productionTimeIdValue.setPalette(self.paletteRed)
                  
                if len(self.dikKonum1) > 1:
                    self.dikKonum1Value.setText(str(self.dikKonum1[-1])+" uA")
                    if 4 > self.dikKonum1[-1] > 1.5:
                        self.dikKonum1Text.setPalette(self.paletteGreen)
                        dikKonum1Test = True
                    else:
                        self.dikKonum1Text.setPalette(self.paletteRed)
                        dikKonum1Test = False
                
                if len(self.yatayKonum1) > 1:
                    self.yatayKonum1Value.setText(str(self.yatayKonum1[-1])+" uA")
                    if 4 > self.yatayKonum1[-1] > abs(1.5 and self.yatayKonum1[-1] - self.dikKonum1[-1]) >= 0.3:
                        self.yatayKonum1Text.setPalette(self.paletteGreen)
                        yatayKonum1Test = True
                    else:
                        self.yatayKonum1Text.setPalette(self.paletteRed)
                        yatayKonum1Test = False
                
                if len(self.dikKonum2) > 1:
                    self.dikKonum2Value.setText(str(self.dikKonum2[-1])+" uA")
                    if 4 > self.dikKonum2[-1] > 1.5 and abs(self.yatayKonum1[-1] - self.dikKonum2[-1]) >= 0.3:
                        self.dikKonum2Text.setPalette(self.paletteGreen)
                        dikKonum2Test = True
                    else:
                        self.dikKonum2Text.setPalette(self.paletteRed)
                        dikKonum2Test = False
                
                if len(self.yatayKonum2) > 1:
                    self.yatayKonum2Value.setText(str(self.yatayKonum2[-1])+" uA")
                    if 4 > self.yatayKonum2[-1] > 1.5 and abs(self.yatayKonum2[-1] - self.dikKonum2[-1]) >= 0.3:
                        self.yatayKonum2Text.setPalette(self.paletteGreen)
                        yatayKonum2Test = True
                    else:
                        self.yatayKonum2Text.setPalette(self.paletteRed)
                        yatayKonum2Test = False
                
                if len(self.dikKonum3) > 1:
                    self.dikKonum3Value.setText(str(self.dikKonum3[-1])+" uA")
                    if 4 > self.dikKonum3[-1] > 1.5 and abs(self.yatayKonum2[-1] - self.dikKonum3[-1]) >= 0.3:
                        self.dikKonum3Text.setPalette(self.paletteGreen)
                        dikKonum3Test = True
                    else:
                        self.dikKonum3Text.setPalette(self.paletteRed)
                        dikKonum3Test = False
                
                if len(self.yatayKonum3) > 1:
                    self.yatayKonum3Value.setText(str(self.yatayKonum3[-1])+" uA")
                    if 4 > self.yatayKonum3[-1] > 1.5 and abs(self.yatayKonum3[-1] - self.dikKonum3[-1]) >= 0.3:
                        self.yatayKonum3Text.setPalette(self.paletteGreen)
                        yatayKonum3Test = True
                    else:
                        self.yatayKonum3Text.setPalette(self.paletteRed)
                        yatayKonum3Test = False
                
                if len(self.dikKonumOrt) != 0:
                    dikKonumOrtValue = round(sum(self.dikKonumOrt) / len(self.dikKonumOrt),2)
                    self.dikKonumOrtValue.setText(str(dikKonumOrtValue)+" uA")
                    if 4 > dikKonumOrtValue > 1.5:
                        self.dikKonumOrtText.setPalette(self.paletteGreen)
                        self.dikKonumOrtValue.setPalette(self.paletteGreen)
                        dikKonumOrtTest = True
                    else:
                        self.dikKonumOrtText.setPalette(self.paletteRed)
                        self.dikKonumOrtValue.setPalette(self.paletteRed)
                        dikKonumOrtTest = False
                
                if len(self.yatayKonumOrt) != 0:
                    yatayKonumOrtValue = round(sum(self.yatayKonumOrt) / len(self.yatayKonumOrt),2)
                    self.yatayKonumOrtValue.setText(str(yatayKonumOrtValue)+" uA")
                    if 4 > yatayKonumOrtValue > 1.5 and abs(yatayKonumOrtValue - dikKonumOrtValue) >= 0.3:
                        self.yatayKonumOrtText.setPalette(self.paletteGreen)
                        self.yatayKonumOrtValue.setPalette(self.paletteGreen)
                        yatayKonumOrtTest = True
                    else:
                        self.yatayKonumOrtText.setPalette(self.paletteRed)
                        self.yatayKonumOrtValue.setPalette(self.paletteRed)
                        yatayKonumOrtTest = False
                        
                if len(self.yatayKonumOrt) != 0:
                    if joinTest and self.mqttTest and dikKonum1Test and yatayKonum1Test and dikKonum2Test and yatayKonum2Test and dikKonum3Test and yatayKonum3Test and dikKonumOrtTest and yatayKonumOrtTest:
                        self.testBaşarılıText.setPalette(self.paletteGreen)
                        self.testBaşarılıValue.setText("Test Başarılı")
                        self.butonStartTest.setStyleSheet("""
                        QPushButton {
                        background-color: #90EE90; /* Beyaz */
                        color: #000000; /* Siyah  */
                        border: 2px solid #000000; /* Siyah sınır */
                        border-radius: 10px; /* Köşeleri yuvarla */
                        }
                        """)
                    else:
                        self.testBaşarılıText.setPalette(self.paletteRed)
                        self.testBaşarılıValue.setText("!!! Test Sıkıntılı !!!")
                        self.butonStartTest.setStyleSheet("""
                        QPushButton {
                        background-color: #FF3333; /* Beyaz */
                        color: #000000; /* Siyah  */
                        border: 2px solid #000000; /* Siyah sınır */
                        border-radius: 10px; /* Köşeleri yuvarla */
                        }
                        """)

                    self.situationValue.setText("Test bitti")   
                    self.testing = False
                    self.ppk2_test.toggle_DUT_power("OFF")  # disable DUT power
                    self.plotTimer.stop()
                    self.textTimer.stop()
                    
                    servo.mid()
                    sleep(1)
        except Exception as e:
            return e
                
                
                
    def sendData(self):
        try:
            if self.mqttTest and len(self.dikKonumOrt)==3 and len(self.yatayKonumOrt)==3:
                data = {
                "deviceId": int(self.pedometreID),
                "verticalCurrent": round(sum(self.dikKonumOrt) / len(self.dikKonumOrt),2) ,
                "horizantalCurrent": round(sum(self.yatayKonumOrt) / len(self.yatayKonumOrt),2)
                }

                response = requests.post(url, headers=headers, json=data)
                self.situationValue.setText(json.loads(response.text)['result'])
                if json.loads(response.text)['success']:
                    self.situationValue.setPalette(self.paletteGreen)
                    self.buttonTestSituation.setStyleSheet("""
                    QPushButton {
                    background-color: #90EE90; /* Yeşil */
                    color: #000000; /* Siyah  */
                    border: 2px solid #000000; /* Siyah sınır */
                    border-radius: 10px; /* Köşeleri yuvarla */
                                }
                                                            """)
                else:
                    self.situationValue.setPalette(self.paletteRed)
                    self.buttonTestSituation.setStyleSheet("""
                    QPushButton {
                    background-color: #FF3333; /* Kırmızı */
                    color: #000000; /* Siyah  */
                    border: 2px solid #000000; /* Siyah */
                    border-radius: 10px; /* Köşeleri yuvarla */
                                }
                                                            """)

        except Exception as e :
            self.situationValue.setText("DATABASE hatası")
            self.situationValue.setPalette(self.paletteRed)
            return e
                
                    
                
                
            
            
        
        
        
        
        
        

    def closeEvent(self, event):
        if self.testing:
            self.stop_test()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())








