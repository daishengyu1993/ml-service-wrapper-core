
# $env:JOB_CONFIG_PATH = "C:\Source\JNJ\Repos\pqv_triage\sdk\test\config.json"
# $env:JNJ_JOB_modBy = "3"

Push-Location $PSScriptRoot\..;
Try {
    docker build --no-cache -t jnjhttpjob-test -f Dockerfiles/Dockerfile.http .
}
Finally {
    Pop-Location
}

docker stop jnjhttpjob-test
docker rm jnjhttpjob-test
docker run -d --name jnjhttpjob-test -p 80:80 jnjhttpjob-test

# uwsgi --socket 127.0.0.1:3031 --wsgi-file jnjhttpjob\jnjhttpjob\main.py --callable app


