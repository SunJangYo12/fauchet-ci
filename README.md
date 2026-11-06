# Saat boot dan modifikasi image siapkan ini:
```
1. Download chrome dan install (diperlukan login google di playwright)
2. Install depend
sudo apt install python3 python3-pip virtualenv git
git clone https://github.com/sunjangyo12/fauchet-ci

cd fauchet-ci
git checkout loop-xubuntu22
cd ~
virtualenv myenv
source myenv/bin/activate

pip install playwright
playwright install chromium

pip install seledroid
pip install telethon
pip install rich
pip install requests bs4
pip install janda
pip install pycryptodome
pip install pyrogram tgcrypto 
pip install pillow
pip install pypng
pip install pycurl
pip install curl_cffi
pip install httpx
pip install bas-http
pip install skipcha

```
