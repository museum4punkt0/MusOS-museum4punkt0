# MusOS-museum4punkt0

*MusOS-museum4punkt0* is an object database and network sensor and
kiosk system with a flexible storytelling engine.

Individual content (images, videos, text slides etc.)
can be delivered to clients flexibly from a server triggered by sensors
(like bluetooth beacons) or user interactions.

This package consists of a server and a client part plus some
sensor software. While the sensor software is deployed manually
(running on a Raspberry Pi), the client software is
delivered by the server as a web application.

*MusOS-museum4punkt0* is based on web technologies, but can be run
on a local network without difficulty, not requiring an internet connection.

(c) Copyright 2018-2020 contexagon GmbH

---

This software is part of the project museum4punkt0 -
Digital Strategies for the Museum of the Future, sub-project
Carnival – Intangible Cultural Heritage in Digital Environments.
Further information:
www.museum4punkt0.de/en/

The project museum4punkt0 is funded by the Federal Government Commissioner
for Culture and the Media in accordance with a resolution issued by the German
Bundestag (Parliament of the Federal Republic of Germany).

---

This software package was based on a more extensive software system
developed by contexagon GmbH before. During the project museum4punkt0
necessary extensions were made to this system.
These extensions and all base functionality required to run
the system are published in this package.



## Getting Started

*MusOS-museum4punkt0* was designed to run on **Linux** and **MacOS**.

This guide was made for *Ubuntu* (should work for similar Linux distributions
like *Debian* or *Linux Mint*, too).



### Prerequisites

Install `docker` and `docker-compose`:

    sudo apt install docker
    sudo apt install docker-compose

*Docker* usually is started automatically on server systems
(like *Ubuntu Server*).
If you are using a desktop OS
you might need to enable this manuelly:

    sudo systemctl enable docker

If you want to access *Docker* without `sudo`, you might want to
add the current user to the `docker` group:

    sudo groupadd docker
    sudo gpasswd -a $USER docker

That's all you need to run *MusOS-museum4punkt0* on a server
(plus the *MusOS-museum4punkt0* software of course).



### Installing

As a developer (and for building the *MusOS-museum4punkt0* software),
you also need `npm`, and `python3-pip`:

    sudo apt-get install npm
    sudo apt install python3-pip

Next create a customer configuration in the `customer` folder
just like `customer/example`
including a `define_env.sh` and `define_db.sh` file.

**Don't forget to define new secret keys**
for `webtokensecretkey` and `mongodbrootpassword` !!!

[random.org](https://www.random.org/passwords/?num=1&len=24&format=plain&rnd=new)
is a good place to generate new random keys.

From the `scripts` folder run (which creates a `docker-compose.yml`
in the `server` folder according to the settings of your customer
`define_env.sh` file):

    ./init_docker.sh

Next create the client application by executing following script
from the `client` folder:

    ./build_and_deploy.sh

After the client application was built the resulting files are automatically
put into the `server/data/public` folder.

Make sure the *MongoDB* user has write access to the folder `server/data/dblog`.

Now build and run the server software executing following command
in the `server` folder (you can detach the process
by adding the `-d` command line switch):

    sudo docker-compose up --build

The *MusOS-museum4punkt0* and the *MongoDB* container should be running now.
You can check it by runing:

    sudo docker ps

Initialize the database including the customer types you defined before
in `define_db.sh` by running the script from the `scripts` folder:

    ./init_db.sh

Now you can populate the database with arbitrary objects
using the *MusOS-museum4punkt0* server API e.g.

    GET /object/<id>
    PUT /object

Most API calls require an access token though, which can be obtained by:

    POST /login

Test the application with your browser (currently *Firefox* and *Chrome*
are supported) by entering the URL with the port defined in `define_env.sh`:

    http://localhost:4000?cbox=testbox



## Deployment

On a live system you need to deploy all files of your `server` folder
including the file `docker-compose.yml` you generated before
and build and run the software like this:

    sudo docker-compose up --build -d



## Built With

* [Docker](https://www.docker.com/) - OS-level virtualization to deliver software in packages (containers)
* [Flask](https://palletsprojects.com/p/flask/) - Python web server framework
* [mongoDB](https://www.mongodb.com/) - document-based database
* [React](https://reactjs.org/) - JavaScript web application framework

plus a number of Python libraries you can find in `server/modules/requirements.txt`
and a number of JavaScript / React libraries you can find in `client/package.json`.

## Changes for Project "5 Units" in 2021/2022

## Extensions for the integration of the "mask scanner" station into the MusOS platform:

The project required preparation for the integration of the "mask scanner" station, since the stations of the "5 units" were developed at physically different locations and therefore a test with the station running was not possible. The integration is carried out during installation in the then completed museum. This means that in a summary station, visitors can have the image created by the mask scanner displayed again.

The mask scanner station has been expanded so that a prefix to be obtained via a URL can be added to the file name of the image to be saved. It was also implemented that all created images are physically deleted from the computer after one day.

A Raspberry Pi (similar to the stations of the first iteration of the project module) was integrated into the mask scanner, which is configured using the Python and shell scripts in this directory as a beacon sensor and as a simple rest server. If a visitor approaches the station, this is registered using the beacon that is carried along. If the station is now started with the buzzer, the station can get the current UUID of the visitor beacon via the rest service on the Raspberry Pi and add this to the file name of the image as a prefix when saving.

A rest server with an API is also started on the mask scanner station itself, which the central server can use to load the image belonging to the respective visitor beacon from the station. This can then be used at other stations in the exhibition. For the Fasnachtsmuseum Schloss Langenstein, the picture is shown again at the "Visit summary" station. In terms of data protection, there are no concerns about storage, as only a masked image is shown (with a rendered overlay). The images on the mask station will be permanently deleted after one day. The server itself does not persist the image, but merely displays it on demand via the rest call.


### Application:

A Raspberry Pi 3 or 4 with Raspberry Pi OS or Ubuntu Mate must be integrated into the "mask scanner" station. Ideally in the front area of the housing and not hidden or shielded by other electronics (the radio signals (BLE) must be able to be received unhindered).

The ".../sensors/beacons" directory must be copied from this repository to this Raspberry.

Now start the scripts "setup\_mask\_sensor.sh" and "start\_rest\_server.sh".

The scripts start the beacon sensor, a lightweight rest server, establish server communication to receive the beacon data and respond to visitor actions, and allow the mask scanner to determine the identity of the beacon being carried.

The "getImageAPI.sh" and "start\_rest\_server.sh" scripts must be copied from the ".../sensors/beacons" directory to the mask scanner's computer.

Then start the script "start\_rest\_server.sh" here as well.

The URL of the mask scanner must be given on the server. This can be created as a MusOS object in the database.
For this purpose, a database connection to MongoDB can be established and an object of the type "REST Gateway" can be created.

The definition can be found under ".../data/types/typerestgateway.json":

  ``"definition": {
             "fieldsets": [
                 {
                     "id": "general",
                     "name": "General",
                     "fields": [
                         {
                             "id": "name",
                             "name": "name",
                             "type": "text",
                             "mandatory": true
                         },
                         {
                             "id": "url",
                             "name": "URL",
                             "type": "text",
                             "mandatory": true
                         },
                         {
                             "id": "protocol",
                             "name": "Protocol",
                             "type": "select",
                             "options": ["http", "https"]
                         },
                         {
                             "id": "gatewayuser",
                             "name": "user",
                             "type": "text"
                         },
                         {
                             "id": "gateway password",
                             "name": "Password",
                             "type": "password"
                         }
                     ]
                 }``

The response to this REST call, i.e. the image received, can finally be integrated into the individual stations.


## Extension for the integration of the "Wooden Wall" station of the FNM Langenstein into the MusOS platform

The "Interactive Wooden Wall" station from the first part of the project module combines the technologies of projection mapping and conductive ink into a quiz station in which visitors are presented with a few simple questions about what they have learned in the exhibition. The station consists primarily of a large wooden panel on which the design was applied using conductive and prints.
Another goal of the project extension in the "5 Units" was to integrate this station into the MusOS platform. This integration was prepared here by installing a Raspberry Pi at the station, which in turn acts as a beacon sensor and rest server. When approaching, the visitor is registered. Since there is a finite number of choices and questions (both are physically connected to the wooden wall), only the question number and whether the question was answered correctly the first time is transmitted to the MusOS server. These answers can also be displayed on a summary station when integrated into the museum.

## Authors

* **Jens Gruschel** - *client and server* - [contexagon](https://contexagon.com)
* **Sascha Lorenz** - *server* - [contexagon](https://contexagon.com)
* **Maurizio Tidei** - *client and server* - [contexagon](https://contexagon.com)



## License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details
