## Raspberry pi ye framevareri yükledim

RASPIBERRY PI OS (64-BIT)

username: antagpc

password: 123

## Güncellemelerini yaptım

sudo apt-get update

sudo apt-get upgrade

## Pip i güncelledim

sudo apt-get install python3-pip

## Pythonu güncelledim 

sudo apt-get install python3-full

## Gerekli olan pakateleri yükledim

sudo apt-get install libatlas-base-dev

pip3 install matplotlib --break-system-packages

pip3 install ppk2_api --break-system-packages

## ppk2 test kodunu çalıştırdım bir sıkıntı çıkmadı


## PyQt5 kütüphanelerinin yükledim

sudo apt-get install python3-pyqt5

sudo apt-get install pyqt5-dev-tools

sudo apt-get install qttools5-dev-tools


## Pyqt5 test kodunu çalıştırdım bir sıkıntı çıkmadı

## Pyqt5 ile ppk2 kodlarınını birleştirdim bir sıkıntı çıkmadı

## Mqtt kütüphanesini yükledim

sudo pip install paho-mqtt --break-system-packages

## Virsual studiyoyu ekledim.

sudo apt install software-properties-common apt-transport-https wget

wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | sudo apt-key add -

sudo add-apt-repository "deb [arch=armhf] https://packages.microsoft.com/repos/code stable main"

sudo apt update

sudo apt install code


## VNC yi düzeltmek için uğraştım

---------- VNC Server

sudo rpi-updatey

sudo raspi-config

	Advanced
 
		Wayland
  
			X11 selected

## Otomatik başlatma için

sudo nano /etc/xdg/lxsession/LXDE-pi/autostart

## açılan pencerenin en altına

@lxterminal -e python3 /home/antagpc/Desktop/pedo_test.py 0

@lxterminal -e python3 /home/antagpc/Desktop/pedo_test.py 1

## bu iki kod yazılacak. bu kod terminalden bir kod başlatmak için kullanılır.












