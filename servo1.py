import subprocess
import sys
from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory


# pigpio kütüphanesini yükle
install_command = ['sudo', 'pip', 'install', 'pigpio', '--break-system-packages']
result = subprocess.run(install_command, capture_output=True, text=True)

# Hata varsa çıktı ver
if result.returncode != 0:
    print("Pigpio kurulumu başarısız:")
    print(result.stderr)
    sys.exit(1)  # Hata durumunda betiği sonlandır
else:
    print("Pigpio başarıyla yüklendi!")

# Diğer Python kodları burada başlar
# Örneğin pigpio ile GPIO pinlerini kullanmak gibi işlemler




factory = PiGPIOFactory()

servo = Servo(19, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)

print("Start in the middle")
servo.mid()
sleep(1)
print("Go to min")
servo.min()
sleep(1)
print("Go to max")
servo.max()
sleep(1)
print("And back to middle")
servo.mid()
sleep(1)
servo.value = None;
