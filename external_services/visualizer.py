import logging

import librosa
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

logger = logging.getLogger('default')


# TODO обрабатывать оригинальные файлы только один раз при запуске бота.
class PronunciationVisualizer:
    def __init__(self, original_audio, spoken_audio, sample_rate, file_name):
        self.original_audio = original_audio
        self.spoken_audio = spoken_audio
        self.sample_rate = sample_rate
        self.file_name = file_name

    async def preprocess_audio(self):
        # Удаление тишины и тихих шумов в начале файлов
        self.original_audio, _ = librosa.effects.trim(self.original_audio, top_db=20, frame_length=1024, hop_length=256)
        self.spoken_audio, _ = librosa.effects.trim(self.spoken_audio, top_db=20, frame_length=1024, hop_length=256)

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

        logger.debug('процессинг закончен')

    async def plot_waveform(self):
        logger.debug('начало рисования графика')
        fig, ax = plt.subplots()
        ax.plot(self.original_audio, label='Original')
        ax.plot(self.spoken_audio, label='Spoken', alpha=0.7)
        ax.legend()
        plt.savefig(f'temp/{self.file_name}.png')
        logger.debug('окончание рисования графика')


def plot_pitch(audio):
    y, sr = librosa.load(audio)

    silence = np.zeros(int(sr * 0.2))
    y = np.concatenate((silence, y))

    # Извлечение высоты тона
    y, _ = librosa.effects.trim(y, top_db=25, frame_length=1024, hop_length=256)
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr)

    # Получение высоты тона
    pitch_values = []
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()
        pitch = pitches[index, t]
        pitch_values.append(pitch)

    # Удаление нулевых значений
    pitch_values = [p for p in pitch_values if p > 0]

    # Сглаживание с помощью метода скользящего среднего
    window_size = 2  # Размер окна для сглаживания
    smoothed_pitch = np.convolve(pitch_values, np.ones(window_size)/window_size, mode='valid')

    # Дополнительное сглаживание с помощью фильтра Савицкого-Голея
    smoothed_pitch = savgol_filter(smoothed_pitch, window_length=31, polyorder=5)

    # Построение графика
    plt.figure(figsize=(12, 6))
    #plt.plot(pitch_values, label='Исходная высота тона', alpha=0.5)
    plt.plot(smoothed_pitch, label='Сглаженная высота тона', linewidth=2)
    plt.title('График высоты тона произнесенной фразы')
    plt.xlabel('Время (фреймы)')
    plt.ylabel('Частота (Гц)')
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == '__main__':
    audio = '../temp/audio_2024-08-07_21-18-03.ogg'

    plot_pitch(audio=audio)
