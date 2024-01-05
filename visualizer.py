import matplotlib.pyplot as plt
import numpy as np
import librosa


class PronunciationVisualizer:
    def __init__(self, original_audio, spoken_audio, sample_rate):
        self.original_audio = original_audio
        self.spoken_audio = spoken_audio
        self.sample_rate = sample_rate

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

        print('процессинг закончен')

    async def plot_waveform(self):
        print('начало рисования графика')
        fig, ax = plt.subplots()
        ax.plot(self.original_audio, label='Original')
        ax.plot(self.spoken_audio, label='Spoken', alpha=0.7)
        # ax.set_xlabel('Time')
        # ax.set_ylabel('Amplitude')
        # ax.set_title('Waveform')
        ax.legend()
        plt.savefig('voice.png')
        print('окончание рисования графика')
