
Push-Location $PSScriptRoot;
Try {
    if (!$env:JOB_CONFIG_PATH) {
        $env:JOB_CONFIG_PATH="../../../sample_job/config.json"
    }

    .\setup.ps1
    .\run.ps1
}
Finally {
    Pop-Location
}
