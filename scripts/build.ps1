dotnet build .\core\Server\Server.fsproj -c Release -o ..\..\..\var\nginx\core -f netcoreapp2.0
stack build 
dotnet ..\var\nginx\core\Server.dll