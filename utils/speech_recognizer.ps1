
Add-Type -AssemblyName System.Speech
$ConsoleEncoding = [System.Console]::OutputEncoding
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

try {
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    $recognizer.SetInputToDefaultAudioDevice()
    $grammar = New-Object System.Speech.Recognition.DictationGrammar
    $recognizer.LoadGrammar($grammar)
    
    # Silence initial timeout = 5s, Babble timeout = 5s
    $recognizer.InitialSilenceTimeout = [System.TimeSpan]::FromSeconds(5)
    $recognizer.BabbleTimeout = [System.TimeSpan]::FromSeconds(5)

    $result = $recognizer.Recognize([System.TimeSpan]::FromSeconds(10))

    if ($result) {
        Write-Output "SUCCESS:$($result.Text)"
    } else {
        Write-Output "TIMEOUT"
    }
} catch {
    Write-Output "ERROR:$_"
}
