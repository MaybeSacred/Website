sudo nginx -s reload
pgrep dotnet | xargs kill -s 15
screen -d -m -S SERVER bash -c 'dotnet /var/nginx/core/Server.dll -- --port 8080 --homefolder /var/nginx/public'