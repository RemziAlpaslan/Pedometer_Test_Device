import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout,  QLineEdit, QLabel, QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt, QDateTime
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from ppk2_api.ppk2_api import PPK2_API


class MyPPK2_API(PPK2_API):
    def get_data(self,quantity):
        """Return readings of one sampling period"""
        sampling_data = self.ser.read(quantity*4)
        return sampling_data
    
    def get_samples(self, buf):
        """
        Returns list of samples read in one sampling period.
        The number of sampled values depends on the delay between serial reads.
        Manipulation of samples is left to the user.
        See example for more info.
        """

        sample_size = 4  # one analog value is 4 bytes in size
        offset = self.remainder["len"]
        samples = []

        first_reading = (
            self.remainder["sequence"] + buf[0:sample_size-offset])[:4]
        adc_val = self._digital_to_analog(first_reading)
        measurement, bits = self._handle_raw_data(adc_val)
        if measurement is not None:
            samples.append(measurement)

        offset = sample_size - offset

        while offset <= len(buf) - sample_size:
            next_val = buf[offset:offset + sample_size]
            offset += sample_size
            adc_val = self._digital_to_analog(next_val)
            measurement, bits = self._handle_raw_data(adc_val)
            if measurement is not None:
                samples.append(measurement)

        self.remainder["sequence"] = buf[offset:len(buf)]
        self.remainder["len"] = len(buf)-offset

        # return list of samples and raw digital outputs
        # handle those lists in PPK2 API wrapper
        return samples




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
        
        self.setWindowTitle("PPK2 Live Plot Example")
        # Pencere açmayı sağlar
    
        
        
        hBoxMain = QHBoxLayout()
        vBox1 = QVBoxLayout()
        hBoxLogoId = QHBoxLayout()
        hBoxMaxMinAvg = QHBoxLayout()
        vBox2 = QVBoxLayout()
        hBoxJoinAkım  = QHBoxLayout()
        hBoxJoinBaşlama  = QHBoxLayout()
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
        antagPicture = QPixmap(r"C:\Users\remzi alpaslan\Desktop\Python Kodları\Nordic_gui\antag.png")
        antagPicture = antagPicture.scaled(386,103)
        self.logo.setPixmap(antagPicture)
        hBoxLogoId.addWidget(self.logo)
        # logoyu ekledim
        
        
        
        hBoxLogoId.addStretch()
        self.productionTimeValue = QLineEdit()
        self.productionTimeValue.setText("????????")
        self.productionTimeValue.setReadOnly(True)
        self.productionTimeValue.setAlignment(Qt.AlignCenter)
        Font = QFont()
        Font.setPointSize(20)  # Yazı boyutunu 20 yap
        self.productionTimeValue.setFont(Font)
        hBoxLogoId.addWidget(self.productionTimeValue)
        vBox1.addLayout(hBoxLogoId)
        hBoxLogoId.addStretch()
        
        self.canvas = MplCanvas(self, width=15, height=20, dpi=100)
        vBox1.addWidget(self.canvas)
        # Pencerede canlı grafiği gösterir
        
        self.maxValue = QLineEdit()
        self.maxValue.setText("???")
        self.maxValue.setReadOnly(True)
        self.maxValue.setFont(Font)
        hBoxMaxMinAvg.addWidget(self.maxValue)
        
        self.minValue = QLineEdit()
        self.minValue.setText("???")
        self.minValue.setReadOnly(True)
        self.minValue.setFont(Font)
        hBoxMaxMinAvg.addWidget(self.minValue)
        
        
        self.AvgValue = QLineEdit()
        self.AvgValue.setText("???")
        self.AvgValue.setReadOnly(True)
        self.AvgValue.setFont(Font)
        hBoxMaxMinAvg.addWidget(self.AvgValue)
        vBox1.addLayout(hBoxMaxMinAvg)
        
        
        
        self.butonStartTest = QPushButton("Start/Stop Test", self)
        self.butonStartTest.clicked.connect(self.startTest)
        vBox1.addWidget(self.butonStartTest)

        
        
        Font.setPointSize(10)
        
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
        
        
        
        self.situationValue = QLineEdit()
        self.situationValue.setText("???")
        self.situationValue.setReadOnly(True)
        self.situationValue.setFont(Font)
        vBox2.addWidget(self.situationValue)
        
        
        
        self.workingTime = QLineEdit()
        self.workingTime.setText("???")
        self.workingTime.setReadOnly(True)
        self.workingTime.setFont(Font)
        vBox2.addWidget(self.workingTime)
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
        
        self.canvasMini = MplCanvas(self, width=6, height=3, dpi=100)
        vBox2.addWidget(self.canvasMini)
        
        self.buttonTestSituation = QPushButton("Test Başarılı Onaylıyorum", self)
        self.buttonTestSituation.clicked.connect(self.startTest)
        vBox2.addWidget(self.buttonTestSituation)
        
        
        
        hBoxMain.addLayout(vBox1)
        hBoxMain.addLayout(vBox2)
        

        
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(hBoxMain)
        
        
        
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # 1000 milisaniyede bir (1 saniye)

        # İlk güncelleme için tarih ve saati ayarla
        self.update_datetime()
        print("remzi")
        
        
        
        self.x_data = [0]
        self.y_data = [0]
        self.x_dataMini = [0]
        self.y_dataMini = [0]
        self.start_time = time.time()
        self.testing = False
        
        
        # PPK2 initialization
        ppk2s_connected = MyPPK2_API.list_devices()
        if len(ppk2s_connected) == 1:
            self.ppk2_port = ppk2s_connected[0]
            print(f'Found PPK2 at {self.ppk2_port}')
        else:
            print(f'Too many connected PPK2\'s: {ppk2s_connected}')
            exit()

        self.ppk2_test = MyPPK2_API(self.ppk2_port, timeout=1, write_timeout=1, exclusive=True)
        self.ppk2_test.get_modifiers()
        self.ppk2_test.set_source_voltage(3300)
        self.ppk2_test.use_ampere_meter()  # set ampere meter mode
        self.ppk2_test.toggle_DUT_power("OFF")  # enable DUT power
        time.sleep(1)
        
        
        self.pltTimer = QTimer()
        self.pltTimer.setInterval(10)  # Update every 100 ms
        self.pltTimer.timeout.connect(self.update_plot)
        
        self.showMaximized() # showFullScreen e sonra çevirilecek
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
        self.testing = True
        self.ppk2_test.start_measuring()  # start measuring
        self.start_time = time.time()
        self.ppk2_test.toggle_DUT_power("ON")  # diable DUT power
        self.pltTimer.start()
        self.x_data=[0]
        self.y_data=[0]
        self.x_dataMini=[0]
        self.y_dataMini=[0]
        self.secondTime=0
        self.Time=time.time()
        

    
    def stop_test(self):
        print((len(self.y_data)/(time.time()-self.start_time)))
        self.testing = False
        self.pltTimer.stop()
        self.ppk2_test.toggle_DUT_power("OFF")  # disable DUT power
        self.ppk2_test.stop_measuring()
    
    def update_plot(self):
        worktime=time.time()-self.Time
        self.Time=time.time()
        sample_size = round(worktime/0.01)
        #print(sample_size)
        read_data = self.ppk2_test.get_data(sample_size)
        if read_data != b'':
            samples = self.ppk2_test.get_samples(read_data)
            for i in range(sample_size):
                self.y_data.append(samples[i])
                self.x_data.append(self.x_data[-1]+(worktime)/sample_size)
                
                if self.secondTime==int(self.x_data[-1]+(worktime)/sample_size):
                    self.y_dataMini.append(samples[i])
                    self.x_dataMini.append((self.x_data[-1]+(worktime)/sample_size)-self.secondTime)
                else:
                    print(max(self.y_dataMini))
                    self.AvgValue.setText("Avg: "+str(round(sum(self.y_dataMini)/len(self.x_dataMini),2))+" uA")
                    self.canvasMini.axes.cla()  # Clear the canvas.
                    self.canvasMini.axes.plot(self.x_dataMini, self.y_dataMini, 'r')
                    self.canvasMini.draw()
                    self.secondTime+=1
                    self.y_dataMini=[samples[i]]
                    self.x_dataMini=[(self.x_data[-1]+(worktime)/sample_size)-self.secondTime]
            
                
        self.maxValue.setText("Max: "+str(round(max(self.y_data),2))+" uA")
        self.minValue.setText("Min: "+str(round(min(self.y_data),2))+" uA")                     
        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.x_data, self.y_data, 'r')
        self.canvas.draw()

    def closeEvent(self, event):
        if self.testing:
            self.stop_test()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())

