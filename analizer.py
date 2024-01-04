import librosa
import matplotlib.pyplot as plt
import librosa.display


async def analize_voice(voice):
    y, sr = librosa.load(voice)
    plt.figure(figsize=(12, 4))
    librosa.display.waveshow(y, sr=sr, color="blue")
    plt.savefig('voice.png')
