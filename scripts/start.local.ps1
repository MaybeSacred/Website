if ($IsLinux) {
    sudo nginx -s reload
}
$dotnet = Start-Process "dotnet" "$outDir/core/Server.dll -- --port 8080 --homefolder $outDir/public" -PassThru
Set-Location $aquilaDir
$aquila = Start-Process "aquila" "--port 3000" -PassThru
Start-Sleep -s 1
if ($dotnet.HasExited -and $dotnet.ExitCode -ne 0) { Write-Verbose "dotnet failed to start and exited with code $($dotnet.ExitCode)" }
if ($aquila.HasExited -and $aquila.ExitCode -ne 0) { Write-Verbose "aquila failed to start and exited with code $($aquila.ExitCode)" }