# Weather app

This simple application retrieves data from OpenWeatherAPI and returns it user with use of blob storage and database logging.

---
### 1. How to run the application

---
#### Local use

To run the application locally what you need to do is to clone to your pc, and have installed <https://docs.docker.com/get-started/> <b>Docker</b>.
After installation of docker toy need to have <b>docker-compose</b> <https://docs.docker.com/compose/install/>.
<b>.env</b> file must be filled via text editor.
For local use 
```
SERVICE_HANDLER_NAME - aws (currently the only one option)
STORAGE_BUCKET_NAME - bucket name of local blob storage (must be lowercase without symbols)
DB_TABLE_NAME - db table of local db for logging purpose (must be lowercase, snake case is ok)
WEATHER_API_KEY - openweatherpapi api key to have data requested
SERVICES_REGION - for local may be set as us-east-1
```
must be provided. 
Next step would be building and starting containers via docker-compose.yml.
To run docker-compose
```docker-compose -f docker-compose-local.yml up --build```


#### AWS use
To run application with AWS services you need to do is to clone to your pc, and have installed <https://docs.docker.com/get-started/> <b>Docker</b>.
After installation of docker yoy need to have <b>docker-compose</b> <https://docs.docker.com/compose/install/>.
<b>.env</b> file must be filled.
For remote use 
```
SERVICE_ACCESS_KEY - aws_access_key_id (from aws security settings)
SERVICE_ACCESS_KEY_SECRET - aws_access_secret_key (from aws security settings)
SERVICE_HANDLER_NAME - "aws" (currently the only one option)
STORAGE_BUCKET_NAME - bucket name of blob storage service (must be lowercase without symbols)
DB_TABLE_NAME - db table for logging purpose (must be lowercase, snake case is ok)
WEATHER_API_KEY - openweatherapi api key to have data requested
SERVICE_REGION - region of aws services
```
Next step would be
```docker-compose up --build
or
ocker-compose -f docker-compose.yml up --build
``` 
to start API for weather app with usage of remote AWS services.
Node: after first build ```--build``` can be mitigated

---
### 2. Run on remote server

--
----
* AWS registration and run EC2 instance
* When instance running it is needed to create KEY PAIR file for instance access and store it to machine
* Add rules to instances to have access (Port range 80 for HTTP; source 0.0.0.0/0 or Anywhere as Example)
* Save rules
#### Access Ubuntu
* To connect to remote machine use ssh with key pair file stored before(<filename>.pem).
* Can move it to ~/.ssh/<filename>.pem (better to change rights to 0400)
* Connection: ```ssh -i ~/.ssh/<filename>.pem```
#### Run
Clone repository to instance.
Install docker and docker-compose on remote machine (recommended to set password on remote machine ```sudo passwd ubuntu```).
##### Docker installation

```
sudo apt update -y
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" -y
sudo apt update -y
apt-cache policy docker-ce
sudo apt install docker-ce -y
sudo usermod -aG docker ${USER}
su - ${USER}
id -nG
sudo usermod -aG docker ubuntu
```

##### Docker-compose installation

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
##### .env setup and run
Setup env as per 1 of this readme.
Run application as per 1 of this readme.