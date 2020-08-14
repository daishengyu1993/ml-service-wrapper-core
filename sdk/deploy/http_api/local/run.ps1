
$configPath = $env:JOB_CONFIG_PATH

$configPath = [System.IO.Path]::GetFullPath($configPath)

$env:JOB_CONFIG_PATH = $configPath

Push-Location $PSScriptRoot\..\..\..\http_api;
Try {
    gunicorn main:app
}
Finally {
    Pop-Location
}
