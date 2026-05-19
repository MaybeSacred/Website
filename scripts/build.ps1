param (
	$ServerPath = "",
	$IsProd = $false
)
$OutDir = "$ServerPath/var/nginx"
# output directory for aquila subsite
$aquilaDir = "$OutDir/aquila"

# core F# server
Set-Location ./core/
dotnet publish ./Server/Server.fsproj -c Release -o "./bin/publish"
# random TS stuff hosted by that
npm ci
npm run release
# pi configuration frontend
Set-Location ./pi-configuration/pi-configuration-fe/
npm ci
npm run build
Set-Location ../../
# haskell link server ??
Set-Location ../haskell/yesod/aquila/
stack build --copy-bins
$localPath = stack path --local-bin
Set-Location ../../../

# copy to destination
if ($IsProd) {
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./core/Server/bin/publish/* "$OutDir/core/"
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./public/* "$OutDir/public/"
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./haskell/yesod/aquila/static/* $aquilaDir
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r $localPath/* $aquilaDir
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./nginx/* "$ServerPath/etc/nginx/sites-available"
}
else {
	Remove-Item -Path "$OutDir/*" -Recurse
	Copy-Item -Path ./core/Server/bin/publish/ -Destination "$OutDir/core/" -Force -Recurse -Container
	Copy-Item -Path ./public/ -Destination "$OutDir/public/" -Force -Recurse -Container
	Copy-Item -Path ./haskell/yesod/aquila/static/ -Destination "$aquilaDir/static" -Recurse -Force -Container
	Copy-Item -Path $localPath -Destination $aquilaDir -Force -Recurse -Container
	Copy-Item -Path ./nginx/ -Destination "$ServerPath/etc/nginx/sites-available/" -Force -Recurse -Container
	# fastapi data ingestion server
	Get-ChildItem ./python-pi/data-ingestion-server/ -Recurse -Include "*.py", "*.toml" "python-version" | 
	Where-Object { $_.FullName -notmatch '\\\.venv\\' } | 
	Copy-Item -Destination "$OutDir/data-ingestion-server/" -Force -Recurse -Container |
	cd "$OutDir/data-ingestion-server/"
	& "source .venv/bin/activate"
	& "pip install -r requirements.txt"
	deactivate
}
