
$imageName = "jnjhttpjob"

Push-Location $PSScriptRoot\..\..;
Try {
    docker build --no-cache -t $imageName -f "$PSScriptRoot\Dockerfile" .
}
Finally {
    Pop-Location
}

docker stop $imageName
docker rm $imageName
    
docker run -d `
    -p 80 `
    -p 443 `
    --name $imageName `
    $imageName
