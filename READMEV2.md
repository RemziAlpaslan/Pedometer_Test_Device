# Raspberry pi ye framevareri yükleme

RASPIBERRY PI OS (64-BIT)

username: antagpc

password: 123

# Gerekli olan pakateleri yükleme

sudo apt-get install libatlas-base-dev

pip3 install matplotlib --break-system-packages

pip3 install ppk2_api --break-system-packages

sudo apt-get install python3-pyqt5

sudo apt-get install pyqt5-dev-tools

sudo apt-get install qttools5-dev-tools

sudo pip install paho-mqtt --break-system-packages

pip install gpiozero  --break-system-packages

sudo pip install pigpio --break-system-packages

sudo pigpiod

pip install pynput --break-system-packages

# VNC yi düzeltmek için 

---------- VNC Server

sudo rpi-updatey

sudo raspi-config

	Advanced
 
		Wayland
  
			X11 selected

# Otomatik başlatma için

## Bash dosyası oluşturma

nano pedo_test.sh

### Dosyanın içine bunları yazın

#!/bin/bash 

sleep 45

sudo pip install pigpio --break-system-packages

sudo pigpiod

### Kaydettikten sonra bash dosyasına izin ver ve dosyanın yerini bul

chmod +x proje.sh

realpath proje.sh

## Otomatik başlatma

sudo nano /etc/xdg/lxsession/LXDE-pi/autostart

### Açılan yerin en altına

@lxterminal -e bash /home/antagpc/pedo_test.sh

# Netbird ün kurulumu

curl -fsSL https://pkgs.netbird.io/install.sh | sh

sudo apt-get update

sudo apt-get install ca-certificates curl gnupg -y

curl -sSL https://pkgs.netbird.io/debian/public.key | sudo gpg --dearmor --output /usr/share/keyrings/netbird-archive-keyring.gpg

echo 'deb [signed-by=/usr/share/keyrings/netbird-archive-keyring.gpg] https://pkgs.netbird.io/debian stable main' | sudo tee /etc/apt/sources.list.d/netbird.list

sudo apt-get update

## for CLI only

sudo apt-get install netbird

## for GUI package

sudo apt-get install netbird-ui

### Normal başlatma için

netbird up

### Anahtar ile başlamak için

sudo netbird up --setup-key <SETUP KEY>


## NoMachine ın kurulumu

### nomachine_8.14.2_1_arm64.deb dosyasınını NoMachinin sitesinden indirdim. Bu dosya raspberry pi 4 için özel bir dosyadır.

### Terminalden Downlands a girdim ve nomachine_8.14.2_1_arm64.deb dosyasını yükledim.

cd Downloands

sudo dpkg -i nomachine_8.14.2_1_arm64.de
















