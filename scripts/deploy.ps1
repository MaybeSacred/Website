param(
	$IsProd = $false
)
$outPath = if ($IsProd) {"ubuntu@ec2-18-222-225-56.us-east-2.compute.amazonaws.com:"} else {""}
. .\scripts\build.ps1 -ServerPath $outPath -IsProd $IsProd
If ($IsProd) {
	start.aws.ps1
}
else {
	start.local.ps1
}