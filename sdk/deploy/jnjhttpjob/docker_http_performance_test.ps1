
Push-Location $PSScriptRoot\..\..;
Try {
    $imageName = "jnjhttpjob"
    
    docker stop $imageName
    docker rm $imageName
    
    docker run -d `
        -p 80 `
        -p 443 `
        --name $imageName `
        $imageName

    $input_data = Import-Csv -Path ".\sample_data\input.csv" | Format-Table
    
    $results = @()
    
    $bound = docker port $imageName 80

    $bound = $bound.Replace("0.0.0.0", "127.0.0.1")

    $status_resp = Invoke-WebRequest http://$bound/api/status

    $status_content = $status_resp.Content | ConvertFrom-Json

    if ($status_content.ready -ne $true) {
        Write-Output "Status for $configName is ${status_content.status}"
    
        continue
    }

    ForEach ($record in $input_data) {
        $doc = @{
            NARRATIVE_ADDL_INFO_ENGLISH = $record.NARRATIVE_ADDL_INFO_ENGLISH
        }

        if ($level -gt 1) {
            $doc.DEFECT_CATEGORY_1 = $record.DEFECT_CATEGORY_1
        
            if ($level -gt 2) {
                $doc.DEFECT_CATEGORY_2 = $record.DEFECT_CATEGORY_2
            }
        }

        $body = @{
            records = @(
                @{
                    id       = $record.COMPLAINT_ID;
                    document = $doc
                }
            )
        }

        $body_json = $body | ConvertTo-Json

        #-Headers @{ "Content-Type" = "application/json"; } `
        $predict_resp = Invoke-WebRequest `
            -Method "POST" `
            -Body $body_json `
            http://$bound/api/process

        Write-Output $predict_resp

        return 0
    }
}
Finally {
    Pop-Location
}
