
$imageName = "mlhttpjob"

Push-Location $PSScriptRoot\..\..\..;
Try {
    docker build -t $imageName -f "$PSScriptRoot\Dockerfile" .
}
Finally {
    Pop-Location
}
