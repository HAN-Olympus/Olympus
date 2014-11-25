sudo apt-get install python python-dev mongodb python-pip gearman git-core -y
sudo mkdir /data
sudo mkdir /data/db
sudo chown -R vagrant /data/db 
sudo chown -R vagrant /var/log
mongod --smallfiles &
sleep 30
mongo localhost:27017/olympus createMongoDatabase.js
cd /OlympusNew
sudo git clone https://github.com/HAN-Olympus/Olympus.git /OlympusNew
sudo python setup.py install --force
gearmand -d
sudo bash startServer.sh
