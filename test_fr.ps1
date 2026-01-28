
Add-Type -AssemblyName System.Speech
$recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine("fr-FR")
Write-Host "French Engine Created"
