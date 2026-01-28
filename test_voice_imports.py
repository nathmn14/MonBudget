
try:
    import speech_recognition as sr
    print("SpeechRecognition: OK")
    print(f"Version: {sr.__version__}")
except ImportError as e:
    print(f"SpeechRecognition: ERROR - {e}")
except Exception as e:
    print(f"SpeechRecognition: ERROR (Other) - {e}")

try:
    import pyaudio
    print("PyAudio: OK")
    p = pyaudio.PyAudio()
    print(f"Peripheriques: {p.get_device_count()}")
except ImportError as e:
    print(f"PyAudio: ERROR - {e}")
except Exception as e:
    print(f"PyAudio: ERROR (Other) - {e}")
