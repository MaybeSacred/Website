#!/bin/sh
sudo nginx -s reload
killall dotnet
killall aquila
# to overcome current limitation with dotnet core
screen -d -m -S SERVER bash -c 'dotnet /var/nginx/core/Server.dll -- --port 8080 --homefolder /var/nginx/public' 

# cd /var/nginx/aquila/
# aquila --port 3000