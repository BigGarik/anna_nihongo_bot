import numpy as np
import matplotlib.pyplot as plt
import librosa


class PronunciationVisualizer:
    def __init__(self, original_audio, spoken_audio, sample_rate):
        self.original_audio = original_audio
        self.spoken_audio = spoken_audio
        self.sample_rate = sample_rate

    def preprocess_audio(self):
        # Удаление тишины и тихих шумов в начале файлов
        self.original_audio, _ = librosa.effects.trim(self.original_audio, top_db=40, frame_length=1024, hop_length=256)
        self.spoken_audio, _ = librosa.effects.trim(self.spoken_audio, top_db=40, frame_length=1024, hop_length=256)

        # Добавление 0.2 секунды тишины в начало обоих файлов
        silence = np.zeros(int(self.sample_rate * 0.2))
        self.original_audio = np.concatenate((silence, self.original_audio))
        self.spoken_audio = np.concatenate((silence, self.spoken_audio))

        # Уравнивание длины двух файлов
        max_length = max(len(self.original_audio), len(self.spoken_audio))
        self.original_audio = librosa.util.fix_length(self.original_audio, size=max_length)
        self.spoken_audio = librosa.util.fix_length(self.spoken_audio, size=max_length)

        # Нормализация по максимальному значению амплитуды
        self.original_audio = librosa.util.normalize(self.original_audio)
        self.spoken_audio = librosa.util.normalize(self.spoken_audio)

    def plot_waveform(self):
        fig, ax = plt.subplots()
        ax.plot(self.original_audio, label='Original')
        ax.plot(self.spoken_audio, label='Spoken', alpha=0.5)
        ax.set_xlabel('Time')
        ax.set_ylabel('Amplitude')
        ax.set_title('Waveform')
        ax.legend()
        plt.show()


# Пример использования класса PronunciationVisualizer с реальными аудиофайлами
original_file = 'original_files/sumimasen.ogg'  # Замените на путь к оригинальному аудиофайлу
spoken_file = 'AwACAgIAAxkBAAOIZZcha6RHprQAAbzXLgIl4R8_X-NpAAKUOgACNIy4SFwGuh6uGmHGNAQ.ogg' # Замените на путь к аудиофайлу произнесения

# Загрузка аудиофайлов
original_audio, sample_rate = librosa.load(original_file)
spoken_audio, _ = librosa.load(spoken_file, sr=sample_rate)

visualizer = PronunciationVisualizer(original_audio, spoken_audio, sample_rate)

# Предварительная обработка аудио (удаление тишины, добавление тишины в начало, уравнивание длины)
visualizer.preprocess_audio()

# Визуализация графика звуковой волны
visualizer.plot_waveform()
