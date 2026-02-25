Write-Host "Starting VM..."

docker run -d -p 8080:5001 --name mon_app ma-capsule