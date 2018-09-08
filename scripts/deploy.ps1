param(
	$IsProd = $false
)
$serverPath = if ($IsProd) {"ubuntu@ec2-18-222-225-56.us-east-2.compute.amazonaws.com:"} else {""}
. .\scripts\build.ps1 -ServerPath $serverPath -IsProd $IsProd
If ($IsProd) {
	. .\scripts\start.aws.ps1 -Server $serverPath
}
else {
	. .\scripts\start.local.ps1
}