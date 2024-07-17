import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout,  QLineEdit, QLabel, QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import QTimer, Qt, QDateTime
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ppk2_api.ppk2_api import PPK2_API
from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory
import paho.mqtt.client as mqtt
import json
import requests
import subprocess

# pigpiod komutunu çalıştır
result = subprocess.run(['sudo', 'pigpiod'], capture_output=True, text=True)

# Çıktıyı yazdır
print(result.stdout)
print(result.stderr)

# Database initialization
url = 'https://pedotestapi.antag.com.tr/PedometerTest/AddCurrentValues'
headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
}




# Servo initialization
factory = PiGPIOFactory()

servo = Servo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)



# Mqtt initialization
# MQTT broker bilgileri
broker_address = "192.168.0.194"
broker_port = 1883  # Varsayılan MQTT portu
# Mesajları saklamak için bir liste
received_messages = []

# Bağlantı durumu callback fonksiyonu
def on_connect(client, userdata, flags, rc):
    print("Bağlandı. Bağlantı kodu:", rc)
    # Abone olunacak konu (topic) burada belirtilir
    client.subscribe("/join")
# Mesaj alma callback fonksiyonu
def on_message(client, userdata, message):
    received_messages.append(json.loads(message.payload.decode())['deviceName'])
    print(received_messages[-1])

# MQTT istemci oluşturma
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Broker'a bağlanma
client.connect(broker_address, broker_port)




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
        
        
        self.join = 0
        self.dikKonum1 = []
        self.yatayKonum1 = []
        self.dikKonum2 = []
        self.yatayKonum2 = []
        self.dikKonum3 = []
        self.yatayKonum3 = []
        self.dikKonumOrt = []
        self.yatayKonumOrt = []
        self.maxValue = 0
        self.minValue = 0
        self.avgValue = 0
        
        self.x_data = [0]
        self.y_data = [0]
        self.x_dataMini = []
        self.y_dataMini = []
        self.start_time = time.time()
        self.testing = False
        
        self.setWindowTitle("PPK2 Live Plot Example")
        # Pencere açmayı sağlar
    
        
        
        hBoxMain = QHBoxLayout()
        vBox1 = QVBoxLayout()
        hBoxLogoId = QHBoxLayout()
        hBoxMaxMinAvg = QHBoxLayout()
        vBox2 = QVBoxLayout()
        hBoxJoinAkım  = QHBoxLayout()
        hBoxDikKonum1  = QHBoxLayout()
        hBoxYatayKonum1  = QHBoxLayout()
        hBoxDikKonum2  = QHBoxLayout()
        hBoxYatayKonum2  = QHBoxLayout()
        hBoxDikKonum3  = QHBoxLayout()
        hBoxYatayKonum3  = QHBoxLayout()
        hBoxDikKonumOrt  = QHBoxLayout()
        hBoxYatayKonumOrt  = QHBoxLayout()
        hBoxTestBaşarılı  = QHBoxLayout()
        
        
        
        self.logo = QLabel()
        antagPicture = QPixmap(r"/home/antagpc/Desktop/antag.png")
        antagPicture = antagPicture.scaled(386,103)
        self.logo.setPixmap(antagPicture)
        hBoxLogoId.addWidget(self.logo)
        # logoyu ekledim
        
        
        
        hBoxLogoId.addStretch()
        self.productionTimeIdValue = QLineEdit()
        self.productionTimeIdValue.setText("????????")
        self.productionTimeIdValue.setReadOnly(True)
        self.productionTimeIdValue.setAlignment(Qt.AlignCenter)
        Font = QFont()
        Font.setPointSize(25)  # Yazı boyutunu 20 yap
        self.productionTimeIdValue.setFont(Font)
        hBoxLogoId.addWidget(self.productionTimeIdValue)
        vBox1.addLayout(hBoxLogoId)
        hBoxLogoId.addStretch()
        
        self.canvas = MplCanvas(self, width=15, height=20, dpi=100)
        self.canvas.setFixedWidth(1400)
        vBox1.addWidget(self.canvas)
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
        vBox1.addLayout(hBoxMaxMinAvg)
        
        
        
        
        
        self.butonStartTest = QPushButton("Start/Stop Test", self)
        self.butonStartTest.clicked.connect(self.startTest)
        self.butonStartTest.setFixedHeight(100) 
        vBox1.addWidget(self.butonStartTest)
        
        
        
        Font.setPointSize(15)
        
        self.timeValue = QLineEdit()
        self.timeValue.setText("???")
        self.timeValue.setReadOnly(True)
        self.timeValue.setFont(Font)
        vBox2.addWidget(self.timeValue)
        
        self.dateValue = QLineEdit()
        self.dateValue.setText("???")
        self.dateValue.setReadOnly(True)
        self.dateValue.setFont(Font)
        vBox2.addWidget(self.dateValue)
        
        self.testWorkTime = QLineEdit()
        self.testWorkTime.setText("???")
        self.testWorkTime.setReadOnly(True)
        self.testWorkTime.setFont(Font)
        vBox2.addWidget(self.testWorkTime)
        
        self.situationValue = QLineEdit()
        self.situationValue.setText("???")
        self.situationValue.setReadOnly(True)
        self.situationValue.setFont(Font)
        vBox2.addWidget(self.situationValue)
        vBox2.addStretch()
        
        
        
        self.joinAkımText = QLineEdit()
        self.joinAkımText.setText("Join Akımı:")
        self.joinAkımText.setReadOnly(True)
        self.joinAkımText.setFont(Font)
        hBoxJoinAkım.addWidget(self.joinAkımText)
        
        self.joinAkımValue = QLineEdit()
        self.joinAkımValue.setText("???")
        self.joinAkımValue.setReadOnly(True)
        hBoxJoinAkım.addWidget(self.joinAkımValue)
        self.joinAkımValue.setFont(Font)
        vBox2.addLayout(hBoxJoinAkım)
        vBox2.addStretch()
        
        
        self.dikKonum1Text = QLineEdit()
        self.dikKonum1Text.setText("Dik Konum 1:")
        self.dikKonum1Text.setReadOnly(True)
        self.dikKonum1Text.setFont(Font)
        hBoxDikKonum1.addWidget(self.dikKonum1Text)
        
        self.dikKonum1Value = QLineEdit()
        self.dikKonum1Value.setText("???")
        self.dikKonum1Value.setReadOnly(True)
        self.dikKonum1Value.setFont(Font)
        hBoxDikKonum1.addWidget(self.dikKonum1Value)
        vBox2.addLayout(hBoxDikKonum1)
        vBox2.addStretch()
        
        self.yatayKonum1Text = QLineEdit()
        self.yatayKonum1Text.setText("Yatay Konum 1:")
        self.yatayKonum1Text.setReadOnly(True)
        self.yatayKonum1Text.setFont(Font)
        hBoxYatayKonum1.addWidget(self.yatayKonum1Text)
        
        self.yatayKonum1Value = QLineEdit()
        self.yatayKonum1Value.setText("???")
        self.yatayKonum1Value.setReadOnly(True)
        self.yatayKonum1Value.setFont(Font)
        hBoxYatayKonum1.addWidget(self.yatayKonum1Value)
        vBox2.addLayout(hBoxYatayKonum1)
        vBox2.addStretch()
        
        self.dikKonum2Text = QLineEdit()
        self.dikKonum2Text.setText("Dik Konum 2:")
        self.dikKonum2Text.setReadOnly(True)
        self.dikKonum2Text.setFont(Font)
        hBoxDikKonum2.addWidget(self.dikKonum2Text)
        
        self.dikKonum2Value = QLineEdit()
        self.dikKonum2Value.setText("???")
        self.dikKonum2Value.setReadOnly(True)
        self.dikKonum2Value.setFont(Font)
        hBoxDikKonum2.addWidget(self.dikKonum2Value)
        vBox2.addLayout(hBoxDikKonum2)
        vBox2.addStretch()
        
        self.yatayKonum2Text = QLineEdit()
        self.yatayKonum2Text.setText("Yatay Konum 2:")
        self.yatayKonum2Text.setReadOnly(True)
        self.yatayKonum2Text.setFont(Font)
        hBoxYatayKonum2.addWidget(self.yatayKonum2Text)
        
        self.yatayKonum2Value = QLineEdit()
        self.yatayKonum2Value.setText("???")
        self.yatayKonum2Value.setReadOnly(True)
        self.yatayKonum2Value.setFont(Font)
        hBoxYatayKonum2.addWidget(self.yatayKonum2Value)
        vBox2.addLayout(hBoxYatayKonum2)
        vBox2.addStretch()
        
        self.dikKonum3Text = QLineEdit()
        self.dikKonum3Text.setText("Dik Konum 3:")
        self.dikKonum3Text.setReadOnly(True)
        self.dikKonum3Text.setFont(Font)
        hBoxDikKonum3.addWidget(self.dikKonum3Text)
        
        self.dikKonum3Value = QLineEdit()
        self.dikKonum3Value.setText("???")
        self.dikKonum3Value.setReadOnly(True)
        self.dikKonum3Value.setFont(Font)
        hBoxDikKonum3.addWidget(self.dikKonum3Value)
        vBox2.addLayout(hBoxDikKonum3)
        vBox2.addStretch()
        
        self.yatayKonum3Text = QLineEdit()
        self.yatayKonum3Text.setText("Yatay Konum 3:")
        self.yatayKonum3Text.setReadOnly(True)
        self.yatayKonum3Text.setFont(Font)
        hBoxYatayKonum3.addWidget(self.yatayKonum3Text)
        
        self.yatayKonum3Value = QLineEdit()
        self.yatayKonum3Value.setText("???")
        self.yatayKonum3Value.setReadOnly(True)
        self.yatayKonum3Value.setFont(Font)
        hBoxYatayKonum3.addWidget(self.yatayKonum3Value)
        vBox2.addLayout(hBoxYatayKonum3)
        vBox2.addStretch()
        
        self.dikKonumOrtText = QLineEdit()
        self.dikKonumOrtText.setText("Dik Konum Ort:")
        self.dikKonumOrtText.setReadOnly(True)
        self.dikKonumOrtText.setFont(Font)
        hBoxDikKonumOrt.addWidget(self.dikKonumOrtText)
        
        self.dikKonumOrtValue = QLineEdit()
        self.dikKonumOrtValue.setText("???")
        self.dikKonumOrtValue.setReadOnly(True)
        self.dikKonumOrtValue.setFont(Font)
        hBoxDikKonumOrt.addWidget(self.dikKonumOrtValue)
        vBox2.addLayout(hBoxDikKonumOrt)
        vBox2.addStretch()
        
        self.yatayKonumOrtText = QLineEdit()
        self.yatayKonumOrtText.setText("Yatay Konum Ort:")
        self.yatayKonumOrtText.setReadOnly(True)
        self.yatayKonumOrtText.setFont(Font)
        hBoxYatayKonumOrt.addWidget(self.yatayKonumOrtText)
        
        self.yatayKonumOrtValue = QLineEdit()
        self.yatayKonumOrtValue.setText("???")
        self.yatayKonumOrtValue.setReadOnly(True)
        self.yatayKonumOrtValue.setFont(Font)
        hBoxYatayKonumOrt.addWidget(self.yatayKonumOrtValue)
        vBox2.addLayout(hBoxYatayKonumOrt)
        vBox2.addStretch()
        
        
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
        vBox2.addLayout(hBoxTestBaşarılı)
        vBox2.addStretch()
        
        
        self.buttonTestSituation = QPushButton("Test Başarılı Onaylıyorum", self)
        self.buttonTestSituation.clicked.connect(self.sendData)
        self.buttonTestSituation.setFixedHeight(100) 
        vBox2.addWidget(self.buttonTestSituation)
        
        
        
        hBoxMain.addLayout(vBox1)
        hBoxMain.addLayout(vBox2)
        

        
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(hBoxMain)
        
        
        
        
        
        
        
        # PPK2 initialization
        ppk2s_connected = PPK2_API.list_devices()
        if len(ppk2s_connected) == 1:
            self.ppk2_port = ppk2s_connected[0]
            print(f'Found PPK2 at {self.ppk2_port}')
        else:
            print(f'Too many connected PPK2\'s: {ppk2s_connected}')
            exit()

        self.ppk2_test = PPK2_API(self.ppk2_port, timeout=1, write_timeout=1, exclusive=True)
        self.ppk2_test.get_modifiers()
        self.ppk2_test.set_source_voltage(3300)
        self.ppk2_test.use_ampere_meter()  # set ampere meter mode
        self.ppk2_test.toggle_DUT_power("OFF")  # enable DUT power
        
        
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
        
        self.showFullScreen() # showFullScreen e sonra çevirilecek
        self.workTime=0
        
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
        self.mqttDataSize=len(received_messages)
        self.mqttTest=None
        client.loop_start()
        self.x_data=[0]
        self.y_data=[0]
        self.x_dataMini=[0]
        self.y_dataMini=[0]
        
        
        self.join = 0
        self.dikKonum1 = []
        self.yatayKonum1 = []
        self.dikKonum2 = []
        self.yatayKonum2 = []
        self.dikKonum3 = []
        self.yatayKonum3 = []
        self.dikKonumOrt = []
        self.yatayKonumOrt = []
        self.maxValue = 0
        self.minValue = 0
        self.avgValue = 0

        palette = QPalette()
        palette.setColor(QPalette.Base, QColor('white'))  # Arka plan rengi
        palette.setColor(QPalette.Text, QColor('black'))  # Metin rengi
        
        self.joinAkımText.setPalette(palette)
        self.dikKonum1Text.setPalette(palette)
        self.yatayKonum1Text.setPalette(palette)
        self.dikKonum2Text.setPalette(palette)
        self.yatayKonum2Text.setPalette(palette)
        self.dikKonum3Text.setPalette(palette)
        self.yatayKonum3Text.setPalette(palette)
        self.dikKonumOrtText.setPalette(palette)
        self.yatayKonumOrtText.setPalette(palette)
        self.testBaşarılıText.setPalette(palette)
        self.productionTimeIdValue.setPalette(palette)
        self.situationValue.setPalette(palette)
        
        
        self.joinAkımValue.setText("???")
        self.timeValue.setText("???")
        self.dateValue.setText("???")
        self.testWorkTime.setText("???")
        self.situationValue.setText("Test Başladı")
        self.joinAkımValue.setText("???")
        self.dikKonum1Value.setText("???")
        self.yatayKonum1Value.setText("???")
        self.dikKonum2Value.setText("???")
        self.yatayKonum2Value.setText("???")
        self.dikKonum3Value.setText("???")
        self.yatayKonum3Value.setText("???")
        self.dikKonumOrtValue.setText("???")
        self.yatayKonumOrtValue.setText("???")
        self.productionTimeIdValue.setText("????????")
        
        
        
        
        self.testing = True
        self.ppk2_test.start_measuring()  # start measuring
        self.start_time = time.time()
        self.ppk2_test.toggle_DUT_power("ON")  # diable DUT power
        self.plotTimer.start()
        self.textTimer.start()
        
        
        self.secondTime=0
        self.Time=time.time()
        self.isTestStarted=False
        self.stopper=True
        
        
        self.canvas.axes.cla()  # Clear the canvas.

    
    def stop_test(self):
        self.situationValue.setText("Test Durdu" )
        self.testing = False
        self.ppk2_test.toggle_DUT_power("OFF")  # disable DUT power
        self.ppk2_test.stop_measuring()
        self.plotTimer.stop()
        self.textTimer.stop()
        servo.mid()
        sleep(1)
    
    def update_plot(self):
        one_time=time.time()
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
                if time.time()-one_time>=1:
                    break
                
                if self.stopper:
                    time.sleep(0.01)
                else:
                    time.sleep(0.001)
                    
                
                
        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.x_data, self.y_data, 'r')
        self.canvas.draw()
        
        self.maxValue = round(max(self.y_dataMini),2)
        self.minValue = round(min(self.y_dataMini),2)
        self.avgValue = round(sum(self.y_dataMini)/len(self.x_dataMini),2)
        
        if time.time() - self.start_time < 6:
            self.join = max(self.y_data)
        
        if self.stopper:
            self.situationValue.setText("Join akımı test ediliyor")
        else:
            self.situationValue.setText("Deepsleep akımı test ediliyor")
        
        
        
        
        
        
        if self.join>30000 and self.avgValue<4:
            if len(received_messages)> self.mqttDataSize:
                self.productionTimeIdValue.setText(str(received_messages[-1]))
                self.mqttTest=True
            else:
                self.mqttTest=False
                
                
            client.loop_stop()
            
            self.situation = "DeepSleep akımı test ediliyor"
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
            if self.stopper:
                self.stoppertime=self.x_data[-1]
                self.x_data=[self.x_data[-1]]
                self.y_data=[self.y_data[-1]]
                self.stopper=False
        
        
        
        
        self.y_dataMini=[]
        self.x_dataMini=[]
        
        self.Time=time.time()
            
            
                    
        
        
            
            
                
            

            
                    
                 
        

    
    def update_text(self):
        self.testWorkTime.setText(str(round(time.time()-self.start_time,2))+" s")
        
        self.maxText.setText("Max: "+str(self.maxValue)+" uA")
        self.minText.setText("Min: "+str(self.minValue)+" uA")      
        self.avgText.setText("Avg: "+str(self.avgValue)+" uA")
        
        paletteGood = QPalette()
        paletteGood.setColor(QPalette.Base, QColor('lightgreen'))  # Arka plan rengi
        paletteGood.setColor(QPalette.Text, QColor('black'))  # Metin rengi
        
        paletteBad = QPalette()
        paletteBad.setColor(QPalette.Base, QColor('red'))  # Arka plan rengi
        paletteBad.setColor(QPalette.Text, QColor('black'))  # Metin rengi
        
        
        self.joinAkımValue.setText(str(round(self.join/1000),)+" mA")
        if self.join>=30000:
            self.joinAkımText.setPalette(paletteGood)
            joinTest = True
        else:
            self.joinAkımText.setPalette(paletteBad)
            joinTest = False
            
        if self.isTestStarted:
            if self.mqttTest:
                self.productionTimeIdValue.setPalette(paletteGood)
            else:
                self.productionTimeIdValue.setPalette(paletteBad)
                
            if len(self.dikKonum1) > 1:
                self.dikKonum1Value.setText(str(self.dikKonum1[-1])+" uA")
                if 4 > self.dikKonum1[-1] > 1.5:
                    self.dikKonum1Text.setPalette(paletteGood)
                    dikKonum1Test = True
                else:
                    self.dikKonum1Text.setPalette(paletteBad)
                    dikKonum1Test = False
            
            if len(self.yatayKonum1) > 1:
                self.yatayKonum1Value.setText(str(self.yatayKonum1[-1])+" uA")
                if 4 > self.yatayKonum1[-1] > 1.5 and self.yatayKonum1[-1] - self.dikKonum1[-1] >= 0.3:
                    self.yatayKonum1Text.setPalette(paletteGood)
                    yatayKonum1Test = True
                else:
                    self.yatayKonum1Text.setPalette(paletteBad)
                    yatayKonum1Test = False
            
            if len(self.dikKonum2) > 1:
                self.dikKonum2Value.setText(str(self.dikKonum2[-1])+" uA")
                if 4 > self.dikKonum2[-1] > 1.5 and self.yatayKonum1[-1] - self.dikKonum2[-1] >= 0.3:
                    self.dikKonum2Text.setPalette(paletteGood)
                    dikKonum2Test = True
                else:
                    self.dikKonum2Text.setPalette(paletteBad)
                    dikKonum2Test = False
            
            if len(self.yatayKonum2) > 1:
                self.yatayKonum2Value.setText(str(self.yatayKonum2[-1])+" uA")
                if 4 > self.yatayKonum2[-1] > 1.5 and self.yatayKonum2[-1] - self.dikKonum2[-1] >= 0.3:
                    self.yatayKonum2Text.setPalette(paletteGood)
                    yatayKonum2Test = True
                else:
                    self.yatayKonum2Text.setPalette(paletteBad)
                    yatayKonum2Test = False
            
            if len(self.dikKonum3) > 1:
                self.dikKonum3Value.setText(str(self.dikKonum3[-1])+" uA")
                if 4 > self.dikKonum3[-1] > 1.5 and self.yatayKonum2[-1] - self.dikKonum3[-1] >= 0.3:
                    self.dikKonum3Text.setPalette(paletteGood)
                    dikKonum3Test = True
                else:
                    self.dikKonum3Text.setPalette(paletteBad)
                    dikKonum3Test = False
            
            if len(self.yatayKonum3) > 1:
                self.yatayKonum3Value.setText(str(self.yatayKonum3[-1])+" uA")
                if 4 > self.yatayKonum3[-1] > 1.5 and self.yatayKonum3[-1] - self.dikKonum3[-1] >= 0.3:
                    self.yatayKonum3Text.setPalette(paletteGood)
                    yatayKonum3Test = True
                else:
                    self.yatayKonum3Text.setPalette(paletteBad)
                    yatayKonum3Test = False
            
            if len(self.dikKonumOrt) != 0:
                dikKonumOrtValue = round(sum(self.dikKonumOrt) / len(self.dikKonumOrt),2)
                self.dikKonumOrtValue.setText(str(dikKonumOrtValue)+" uA")
                if 4 > dikKonumOrtValue > 1.5:
                    self.dikKonumOrtText.setPalette(paletteGood)
                    dikKonumOrtTest = True
                else:
                    self.dikKonumOrtText.setPalette(paletteBad)
                    dikKonumOrtTest = False
            
            if len(self.yatayKonumOrt) != 0:
                yatayKonumOrtValue = round(sum(self.yatayKonumOrt) / len(self.yatayKonumOrt),2)
                self.yatayKonumOrtValue.setText(str(yatayKonumOrtValue)+" uA")
                if 4 > yatayKonumOrtValue > 1.5 and yatayKonumOrtValue - dikKonumOrtValue >= 0.3:
                    self.yatayKonumOrtText.setPalette(paletteGood)
                    yatayKonumOrtTest = True
                else:
                    self.yatayKonumOrtText.setPalette(paletteBad)
                    yatayKonumOrtTest = False
                    
            if len(self.yatayKonumOrt) != 0:
                if joinTest and self.mqttTest and dikKonum1Test and yatayKonum1Test and dikKonum2Test and yatayKonum2Test and dikKonum3Test and yatayKonum3Test and dikKonumOrtTest and yatayKonumOrtTest:
                    self.testBaşarılıText.setPalette(paletteGood)
                    self.testBaşarılıValue.setText("Test Başarılı")
                else:
                    self.testBaşarılıText.setPalette(paletteBad)
                    self.testBaşarılıValue.setText("!!! Test Sıkıntılı !!!")

                self.situationValue.setText("Test bitti")   
                self.testing = False
                self.ppk2_test.toggle_DUT_power("OFF")  # disable DUT power
                self.ppk2_test.stop_measuring()
                self.plotTimer.stop()
                self.textTimer.stop()
                servo.mid()
                sleep(1)
                
    def sendData(self):
        paletteGood = QPalette()
        paletteGood.setColor(QPalette.Base, QColor('lightgreen'))  # Arka plan rengi
        paletteGood.setColor(QPalette.Text, QColor('black'))  # Metin rengi
        
        paletteBad = QPalette()
        paletteBad.setColor(QPalette.Base, QColor('red'))  # Arka plan rengi
        paletteBad.setColor(QPalette.Text, QColor('black'))  # Metin rengi
        
        if self.mqttTest and len(self.dikKonumOrt)==3 and len(self.yatayKonumOrt)==3:
            data = {
            "deviceId": int(received_messages[-1]),
            "verticalCurrent": round(sum(self.dikKonumOrt) / len(self.dikKonumOrt),2) ,
            "horizantalCurrent": round(sum(self.yatayKonumOrt) / len(self.yatayKonumOrt),2)
            }

            response = requests.post(url, headers=headers, json=data)
            self.situationValue.setText(json.loads(response.text)['result'])
            if json.loads(response.text)['success']:
                self.situationValue.setPalette(paletteGood)
            else:
                self.situationValue.setPalette(paletteBad)
                
                    
                
                
            
            
        
        
        
        
        
        

    def closeEvent(self, event):
        if self.testing:
            self.stop_test()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())





