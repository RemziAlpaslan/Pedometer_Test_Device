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

## Netbird ü kurdum

curl -fsSL https://pkgs.netbird.io/install.sh | sh

sudo apt-get update

sudo apt-get install ca-certificates curl gnupg -y

curl -sSL https://pkgs.netbird.io/debian/public.key | sudo gpg --dearmor --output /usr/share/keyrings/netbird-archive-keyring.gpg

echo 'deb [signed-by=/usr/share/keyrings/netbird-archive-keyring.gpg] https://pkgs.netbird.io/debian stable main' | sudo tee /etc/apt/sources.list.d/netbird.list

sudo apt-get update

# for CLI only
sudo apt-get install netbird

# for GUI package
sudo apt-get install netbird-ui

netbird up

## NoMachine ı kurdum

nomachine_8.14.2_1_arm64.deb dosyasınını NoMachinin sitesinden indirdim. Bu dosya raspberry pi 5 için özel bir dosyadır.

Terminalden Downlands a girdim ve nomachine_8.14.2_1_arm64.deb dosyasını yükledim.

cs Downlands

sudo dpkg -i nomachine_8.14.2_1_arm64.deb





