
Push-Location $PSScriptRoot;
Try {
    uvicorn main:app
}
Finally {
    Pop-Location
}
