#!/usr/bin/env bash

customer="$1"
webserver="$2"


. source/select_customer.sh # if not given
. source/set_selected_customer_db.sh
. source/select_webserver.sh # if not given


# post all files to server
for file in ${jsonfiles[@]}
do
    echo "$file.json"
    curl -d "@../$file.json" -X PUT "$webserver/init/object" --header "Content-Type: application/json"
done


# create fulltext index
curl -X POST "$webserver/dbadmin/initdb"