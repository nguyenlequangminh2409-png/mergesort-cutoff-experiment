param(
    [ValidateRange(3, 100)]
    [int]$Rounds = 7
)

$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
Push-Location $project
try {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
    $run = Join-Path $project "runs\run-$stamp"
    $classes = Join-Path $run 'classes'
    New-Item -ItemType Directory -Path $classes -Force | Out-Null

    & javac -d $classes .\src\SortAlgorithm.java .\src\StudentMergeSort.java .\src\CheckStudent.java .\src\GenerateData.java .\src\Benchmark.java
    if ($LASTEXITCODE -ne 0) { throw 'javac failed' }

    $checkLog = Join-Path $run 'check.log'
    & java -cp $classes CheckStudent | Tee-Object -FilePath $checkLog
    if ($LASTEXITCODE -ne 0) { throw 'Correctness check failed; benchmark was not started' }

    $sourceCopy = Join-Path $run 'StudentMergeSort.java'
    Copy-Item .\src\StudentMergeSort.java $sourceCopy
    $envFile = Join-Path $run 'environment.txt'
    $cpuName = (Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)
    @(
        "date_local=$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')"
        "os=$([Environment]::OSVersion.VersionString)"
        "cpu=$cpuName"
        "rounds=$Rounds"
        'cutoffs=0,4,6,7,8,9,10,11,12,14,16,20'
        "source_sha256=$((Get-FileHash $sourceCopy -Algorithm SHA256).Hash)"
        "java_version=$((& cmd.exe /c 'java -version 2>&1' | Out-String).Trim())"
        "javac_version=$((& javac -version 2>&1 | Out-String).Trim())"
    ) | Set-Content -Encoding UTF8 $envFile

    $hashes = Join-Path $run 'data_sha256.csv'
    'dataset,sha256' | Set-Content -Encoding UTF8 $hashes
    Get-ChildItem .\data -Filter '*.txt' | Sort-Object Name | ForEach-Object {
        "$($_.Name),$((Get-FileHash $_.FullName -Algorithm SHA256).Hash)"
    } | Add-Content -Encoding UTF8 $hashes

    $csv = Join-Path $run 'measurements.csv'
    $log = Join-Path $run 'console.log'
    & java -cp $classes Benchmark .\data $csv StudentMergeSort $Rounds '0,4,6,7,8,9,10,11,12,14,16,20' 2>&1 | Tee-Object -FilePath $log
    if ($LASTEXITCODE -ne 0) { throw "Benchmark failed; inspect $log" }

    $bundle = Join-Path $project "runs\run-$stamp-UPLOAD_TO_CHAT.zip"
    Compress-Archive -LiteralPath @($csv, $log, $checkLog, $envFile, $hashes, $sourceCopy) -DestinationPath $bundle
    Write-Host "Completed. Send this ZIP in chat: $bundle"
} finally {
    Pop-Location
}
