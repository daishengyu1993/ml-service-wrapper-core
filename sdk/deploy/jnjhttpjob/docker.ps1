
Push-Location $PSScriptRoot\..\..;
Try {
    docker build --no-cache -t jnjhttpjob -f "$PSScriptRoot\Dockerfile" .
}
Finally {
    Pop-Location
}
