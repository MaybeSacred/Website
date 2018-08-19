param (
	$OutDir = "../var/nginx",
	$IsProd = $false
)
# output directory for aquila subsite
$aquilaDir = "$OutDir/aquila"

Set-Location ./core/
# TODO: have dotnet build normally, copy files manually
dotnet build ./Server/Server.fsproj -c Release -o "./bin/core" -f netcoreapp2.0
npm run release
Set-Location ../haskell/yesod/aquila/
stack build --copy-bins
$localPath = stack path --local-bin
Set-Location ../../../
# copy to destination
if ($IsProd) {
	
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./core/Server/bin/core/* "$OutDir/core/"
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./public/* "$OutDir/public/"
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./haskell/yesod/aquila/static/* $aquilaDir
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r $localPath/* $aquilaDir
	pscp -i C:\Users\jtyso\Downloads\main.ppk -batch -r ./nginx/* /etc/nginx/sites-available/
}
else {
	Remove-Item -Path "$OutDir/*" -Recurse
	Copy-Item -Path ./core/Server/bin/core/ -Destination "$OutDir/core/" -Force -Recurse -Container
	Copy-Item -Path ./public/ -Destination "$OutDir/public/" -Force -Recurse -Container
	Copy-Item -Path ./haskell/yesod/aquila/static/ -Destination $aquilaDir -Recurse -Force -Container
	Copy-Item -Path $localPath -Destination $aquilaDir -Force -Recurse -Container
	Copy-Item -Path ./nginx/ -Destination /etc/nginx/sites-available/ -Force -Recurse -Container
}