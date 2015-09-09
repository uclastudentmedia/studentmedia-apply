#!/usr/bin/env bash

apt-get -y update

# git
apt-get -y install git

# Python
apt-get -y install python-pip
apt-get -y install python-dev

# Postgres   
apt-get -y install postgresql-9.3
apt-get -y install postgresql-server-dev-9.3

# Setup virtualenv
pip install virtualenv
virtualenv /home/vagrant/virtualenv_uclastudentmedia
source /home/vagrant/virtualenv_uclastudentmedia/bin/activate
pip install -r /home/vagrant/studentmedia-apply/requirements.txt

# Activate virtualenv on startup
echo "source /home/vagrant/virtualenv_uclastudentmedia/bin/activate" >> /home/vagrant/.bashrc

# Create the config.py and put in the password for the database
cp /home/vagrant/studentmedia-apply/uclastudentmedia/config.py.example /home/vagrant/studentmedia-apply/uclastudentmedia/config.py
sed -i "s/'PASSWORD': '<INSERT HERE>'/'PASSWORD': 'password'/g" /home/vagrant/studentmedia-apply/uclastudentmedia/config.py

# Setup the postgres database
sudo -u postgres createdb django
sudo -u postgres psql django --command "CREATE USER django WITH PASSWORD 'password';"
sudo -u postgres psql django --command "GRANT ALL PRIVILEGES ON DATABASE django to django;"
/home/vagrant/studentmedia-apply/manage.py syncdb --noinput
/home/vagrant/studentmedia-apply/manage.py migrate
/home/vagrant/studentmedia-apply/manage.py loaddata initial
