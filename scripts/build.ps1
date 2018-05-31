$outDir = "../var/nginx"
# output directory for aquila subsite
$aquilaDir = "$outDir/aquila"

New-Item -ItemType Directory $aquilaDir -Force
Set-Location ./core/
dotnet build ./Server/Server.fsproj -c Release -o "../../../$outDir/core" -f netcoreapp2.0
npm run magic
Set-Location ../haskell/yesod/aquila/
stack build --copy-bins
$localPath = stack path --local-bin
Set-Location ../../../
Copy-Item -Path ./public/ -Destination "$($outDir)/public/" -Force -Recurse -Container
Copy-Item -Path ./haskell/yesod/aquila/static/ -Destination $aquilaDir -Recurse -Force -Container
Copy-Item -Path $localPath -Destination $aquilaDir -Force -Recurse -Container
Copy-Item -Path ./nginx/ -Destination /etc/nginx/sites-available/ -Force -Recurse -Container
# start server programs
if ($IsLinux) {
    nginx -s reload
}
$dotnet = Start-Process "dotnet" "$outDir/core/Server.dll -- --port 8080" -PassThru
Set-Location $aquilaDir
$aquila = Start-Process "aquila" "--port 3000" -PassThru
Start-Sleep -s 1
if ($dotnet.HasExited -and $dotnet.ExitCode -ne 0) { Write-Verbose "dotnet failed to start and exited with code $($dotnet.ExitCode)" }
if ($aquila.HasExited -and $aquila.ExitCode -ne 0) { Write-Verbose "aquila failed to start and exited with code $($aquila.ExitCode)" }
