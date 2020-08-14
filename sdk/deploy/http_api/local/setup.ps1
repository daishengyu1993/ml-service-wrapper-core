Push-Location $PSScriptRoot\..\..\..;
Try {
    pip install .\jnjjobwrapper

    python -m pip install -r ".\http_api\requirements.txt"
    
    pip install gunicorn
}
Finally {
    Pop-Location
}
