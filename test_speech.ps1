
Add-Type -AssemblyName System.Speech
try {
    $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    $recognizer.SetInputToDefaultAudioDevice()
    $grammar = New-Object System.Speech.Recognition.DictationGrammar
    $recognizer.LoadGrammar($grammar)
    Write-Host "Listening..."
    $result = $recognizer.Recognize([System.TimeSpan]::FromSeconds(5))
    if ($result) {
        Write-Host "Text: $($result.Text)"
    } else {
        Write-Host "No speech detected"
    }
} catch {
    Write-Host "Error: $_"
}
