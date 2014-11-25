sudo apt-get install python mongodb python-pip gearman git-core -y
sudo mkdir /data
sudo mkdir /data/db
mongod
sleep 30
mongo localhost:27017/olympus createMongoDatabase.js
sudo mkdir /OlympusNew
cd /OlympusNew
sudo git clone https://github.com/HAN-Olympus/Olympus.git /OlympusNew
sudo python setup.py install --force
gearmand -d
sudo bash startServer.sh
