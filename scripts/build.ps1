param (
	$ServerPath = "",
	$IsProd = $false
)
# output directory for aquila subsite
$OutDir = "$ServerPath/var/nginx"
$aquilaDir = "$OutDir/aquila"

Set-Location ./core/
dotnet publish ./Server/Server.fsproj -c Release -o "./bin/publish"
npm ci
npm run release
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
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./nginx/* "$ServerPath/etc/nginx/sites-available/"
}
else {
	Remove-Item -Path "$OutDir/*" -Recurse
	Copy-Item -Path ./core/Server/bin/publish/ -Destination "$OutDir/core/" -Force -Recurse -Container
	Copy-Item -Path ./public/ -Destination "$OutDir/public/" -Force -Recurse -Container
	Copy-Item -Path ./haskell/yesod/aquila/static/ -Destination "$aquilaDir/static" -Recurse -Force -Container
	Copy-Item -Path $localPath -Destination $aquilaDir -Force -Recurse -Container
	Copy-Item -Path ./nginx/ -Destination "$ServerPath/etc/nginx/sites-available/" -Force -Recurse -Container
}