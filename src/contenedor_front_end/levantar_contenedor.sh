#!/bin/bash

var_env=""

for var in $(ccrypt -d -c settings.env.cpt); do
    var_env="$var_env -e $var"
done

docker run -d --rm -h mariadb -e MYSQL_ROOT_PASSWORD=test   --network prueba_crawler mariadb

sleep 

comando=$(echo docker run --network prueba_crawler  --rm -p 8000:8000 -v \"$PWD/front_end\":/code "$var_env" crawler_eminus_front_end)

bash -c "$comando"

