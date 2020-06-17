#!/usr/bin/env bash

customer="$1"


. source/select_customer.sh # if not given
. source/set_selected_customer_env.sh


# create docker-compose file
cat ../server/docker-compose-template.yml | sed \
    -e "s/<customerid>/$customerid/g" \
    -e "s/<productid>/$productid/g" \
    -e "s/<environment>/$environment/g" \
    -e "s/<webserverport>/$webserverport/g" \
    -e "s/<databasename>/$databasename/g" \
    -e "s/<databaseport>/$databaseport/g" \
    -e "s/<restart>/$restart/g" \
    -e "s/<webtokensecretkey>/$webtokensecretkey/g" \
    -e "s/<mongodbrootpassword>/$mongodbrootpassword/g" \
  > ../server/docker-compose.yml


# copy environment file
cp -p "../customer/$customer/define_env.sh" ../server/
