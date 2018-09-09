param (
	$Server = "ubuntu@ec2-18-222-225-56.us-east-2.compute.amazonaws.com"
)
# needs to be a unix path too
if ($IsLinux) {
	ssh -i C:\Users\jtyso\Downloads\main.pem $Server -m start.aws.sh
}
else {
	plink -i C:\Users\jtyso\Downloads\main.ppk $Server -m .\scripts\start.aws.sh
}

# ideal but broken
# $outDir = "/var/nginx"
# $dotnet = Start-Process "dotnet" "$outDir/core/Server.dll -- --port 8080" -PassThru
# Set-Location $aquilaDir
# $aquila = Start-Process "aquila" "--port 3000" -PassThru
# Start-Sleep -s 1
# if ($dotnet.HasExited -and $dotnet.ExitCode -ne 0) { Write-Verbose "dotnet failed to start and exited with code $($dotnet.ExitCode)" }
# if ($aquila.HasExited -and $aquila.ExitCode -ne 0) { Write-Verbose "aquila failed to start and exited with code $($aquila.ExitCode)" }
