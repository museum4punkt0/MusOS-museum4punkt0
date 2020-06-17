# MusOS

*MusOS* is an object database and network sensor and kiosk system
with a flexible storytelling engine.

Individual content (images, videos, text slides etc.)
can be delivered to clients flexibly from a server triggered by sensors
(like bluetooth beacons) or user interactions.

This package consists of a server and a client part plus some
sensor software. While the sensor software is deployed manually
(running on a Raspberry Pi), the client software is
delivered by the server as a web application.

*MusOS* is based on web technologies, but can be run on a local network
without difficulty, not requiring an internet connection.

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

*MusOS* was designed to run on **Linux** and **MacOS**.

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

That's all you need to run *MusOS* on a server
(plus the *MusOS* software of course).



### Installing

As a developer (and for building the *MusOS* software),
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

The *MusOS* and the *MongoDB* container should be running now.
You can check it by runing:

    sudo docker ps

Initialize the database including the customer types you defined before
in `define_db.sh` by running the script from the `scripts` folder:

    ./init_db.sh

Now you can populate the database with arbitrary objects
using the *MusOS* server API e.g.

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



## Authors

* **Jens Gruschel** - *client and server* - [contexagon](https://contexagon.com)
* **Sascha Lorenz** - *server* - [contexagon](https://contexagon.com)
* **Maurizio Tidei** - *client and server* - [contexagon](https://contexagon.com)



## License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details
