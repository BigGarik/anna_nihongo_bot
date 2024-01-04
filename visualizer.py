import matplotlib.pyplot as plt
import numpy as np


class PronunciationVisualizer:
    def __init__(self, original_audio, spoken_audio, sample_rate):
        self.original_audio = original_audio
        self.spoken_audio = spoken_audio
        self.sample_rate = sample_rate

    def plot_waveform(self):
        # Вычисляем длительность аудио в секундах
        duration = len(self.original_audio) / float(self.sample_rate)

        # Создаем массив временных меток для оси X
        time = np.linspace(0., duration, len(self.original_audio))

        # Построение графиков
        plt.figure(figsize=(10, 4))
        plt.plot(time, self.original_audio, label='Original')
        plt.plot(time, self.spoken_audio, label='Spoken')
        plt.xlabel('Time (s)')
        # plt.ylabel('Amplitude')
        # plt.title('Waveform Comparison')
        plt.set_ylim(-1.0, 1.0)
        plt.legend()
        plt.savefig('voice.png')
        plt.show()

    def plot_spectrogram(self):
        # Вычисляем спектрограмму оригинальной фразы
        original_spec, original_freqs, original_times, _ = plt.specgram(self.original_audio, Fs=self.sample_rate)

        # Вычисляем спектрограмму произнесенной фразы
        spoken_spec, spoken_freqs, spoken_times, _ = plt.specgram(self.spoken_audio, Fs=self.sample_rate)

        # Построение графиков
        plt.figure(figsize=(10, 4))
        plt.imshow(np.log(original_spec), origin='lower', aspect='auto', cmap='viridis')
        plt.title('Original Spectrogram')
        plt.colorbar()
        plt.figure(figsize=(10, 4))
        plt.imshow(np.log(spoken_spec), origin='lower', aspect='auto', cmap='viridis')
        plt.title('Spoken Spectrogram')
        plt.colorbar()
        plt.show()
