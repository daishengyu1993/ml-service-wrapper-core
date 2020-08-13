
Push-Location $PSScriptRoot\..\..;
Try {
    $imageName = "jnjhttpjob"
    
    $input_data = Import-Csv -Path "..\sample_data\input.csv"

    $bound = docker port $imageName 80

    $bound = $bound.Replace("0.0.0.0", "127.0.0.1")

    
    while ($True) {
        try {
            $status_resp = Invoke-WebRequest http://$bound/api/status

            $status_content = $status_resp.Content | ConvertFrom-Json

            if ($status_content.ready -eq $true) {
                break
            }

            $status_message = $status_content.status
        
            Write-Output "Status for $bound is ${status_message}"
        }
        catch {
            Write-Output "An error occurred while retrieving status"
        }

        Start-Sleep 1
    }

    $stopwatch =  New-Object System.Diagnostics.Stopwatch
    $complete = 0

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
            parameters = @{
                textField = "NARRATIVE_ADDL_INFO_ENGLISH"
            };
            records    = @(
                @{
                    id       = $record.COMPLAINT_ID;
                    document = $doc
                }
            )
        }

        $body_json = $body | ConvertTo-Json -Depth 100

        $stopwatch.Start()
        $predict_resp = Invoke-WebRequest `
            -Method "POST" `
            -ContentType "application/json; charset=utf-8" `
            -Body $body_json `
            http://$bound/api/process

        $stopwatch.Stop()
        $complete = $complete + 1
    }

    $avg = $stopwatch.ElapsedMilliseconds / $complete

    Write-Output $avg
}
Finally {
    Pop-Location
}
