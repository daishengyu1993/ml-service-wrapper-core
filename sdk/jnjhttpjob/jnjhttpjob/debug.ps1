
Push-Location $PSScriptRoot;
Try {
    pip install ..\..\jnjjobwrapper
    $env:JOB_CONFIG_PATH="../../sample_job/config.json"
    uvicorn main:app
}
Finally {
    Pop-Location
}
