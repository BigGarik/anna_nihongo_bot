import numpy as np
import matplotlib.pyplot as plt
import librosa


class PronunciationVisualizer:
    def __init__(self, original_audio, spoken_audio, sample_rate):
        original_audio, sample_rate = librosa.load(original_file)
        spoken_audio, _ = librosa.load(spoken_file, sr=sample_rate)
        self.original_audio = original_audio
        self.spoken_audio = spoken_audio
        self.sample_rate = sample_rate

    def normalize_audio(self, audio):
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            normalized_audio = audio / max_amplitude
        else:
            normalized_audio = audio
        return normalized_audio

    def plot_waveform(self, normalize=False):
        if normalize:
            original_normalized = self.normalize_audio(self.original_audio)
            spoken_normalized = self.normalize_audio(self.spoken_audio)
        else:
            original_normalized = self.original_audio
            spoken_normalized = self.spoken_audio

        fig, ax = plt.subplots()
        ax.plot(original_normalized, label='Original')
        ax.plot(spoken_normalized, label='Spoken')
        ax.set_xlabel('Time')
        ax.set_ylabel('Amplitude')
        ax.set_title('Waveform')
        ax.legend()
        plt.show()


# Пример использования класса PronunciationVisualizer с реальными аудиофайлами
original_file = 'sumimasen.ogg'  # Замените на путь к оригинальному аудиофайлу
spoken_file = 'AwACAgIAAxkBAANWZZQgNnuNymo_qRD6E73tMnu1H2wAAjBDAAIVT6hI39WPK0nnqjg0BA.ogg' # Замените на путь к аудиофайлу произнесения

# Загрузка аудиофайлов


visualizer = PronunciationVisualizer(original_audio, spoken_audio, sample_rate)

# Визуализация графика звуковой волны
visualizer.plot_waveform(normalize=True)
