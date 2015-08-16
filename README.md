# studentmedia-apply
Application website for UCLA Student Media.

## Setting up locally

Requirements
* [Python](https://www.python.org/) 2.6.5 or later
* [pip](https://pip.pypa.io/en/stable/installing.html)
* [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
* [PostgreSQL](http://www.postgresql.org/download/)

Open postgres shell with `psql` command. In sql shell, create a database for the site and user

	CREATE DATABASE django;
	CREATE ROLE django SUPERUSER LOGIN PASSWORD 'django';

Then quit the shell (`\q`)

Follow same instructions below from cloning the repository to the running `./manage.py loaddata initial`

Then to run the site locally (by default will be at localhost:8000)
	
	./manage.py runserver
	
## Deploying on [digitalocean](https://www.digitalocean.com/)
Select the premade image of Django on Ubuntu.  After logging in as 'root', you will see the credentials for the 'django' for you to use from now on.

Go to the `/home/django/` directory and git clone this repository.
Set up the virtualenv:
* `virtualenv virtualenv_uclastudentmedia`
* `source virtualenv_uclastudentmedia/bin/activate`
* `pip install -r studentmedia-apply/requirements.txt`

Configure the django project. In `uclastudentmedia/` copy `config.py.example` and name it `config.py`.  Make the appropriate changes such as changing the database password to what was displayed when you logged in.

Initialize the database.  `cd studentmedia-apply`
* `./manage.py syncdb`
* `./manage.py migrate`
* `./manage.py loaddata initial`

Copy the configuration files for nginx and gunicorn.  Restart them after: 
* `sudo cp docs/nginx/django /etc/nginx/sites-available/django`
* `sudo cp docs/gunicorn/gunicorn.conf /etc/init/gunicorn.conf`
* `sudo nginx -s reload`
* `sudo service gunicorn restart`

[django-mailer](https://github.com/pinax/django-mailer) is used to queue emails to be sent because they were done synchronously by default.  Create a cronjob so that emails (password resets) are sent:
```bash
crontab -e
*       * * * * /home/django/virtualenv_uclastudentmedia/bin/python /home/django/django_project/manage.py send_mail >> /home/django/logs/cron_mail.log 2>&1
0,20,40 * * * * /home/django/virtualenv_uclastudentmedia/bin/python /home/django/django_project/manage.py retry_deferred >> /home/django/logs/cron_mail_deferred.log 2>&1
```
