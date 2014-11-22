sudo apt-get install python mongodb python-pip gearman git-core -y
mongod
sleep 10
mongo localhost:27017/olympus createMongoDatabase.js
sudo mkdir /OlympusNew
cd /OlympusNew
sudo git clone https://github.com/HAN-Olympus/Olympus.git /OlympusNew
sudo python setup.py install --force
gearmand -d
cd Olympus
sudo sphinx-apidoc -f -o docs/ . ; cd docs/ ; make html ; cd ..