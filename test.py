from visualizer import PronunciationVisualizer
import soundfile as sf
import numpy as np

# Загрузка оригинального и произнесенного аудио файлов в формате OGG
original_audio, original_sample_rate = sf.read('sumimasen.ogg')
spoken_audio, spoken_sample_rate = sf.read('AwACAgIAAxkBAANWZZQgNnuNymo_qRD6E73tMnu1H2wAAjBDAAIVT6hI39WPK0nnqjg0BA.ogg')

# Удаление тихих звуков в начале аудиофайлов
threshold = 0.01  # Задайте желаемый пороговый уровень для тихих звуков


def remove_silence(audio):
    non_silent_indices = np.where(np.abs(audio) > threshold)[0]
    return audio[non_silent_indices[0]:]


original_audio = remove_silence(original_audio)
spoken_audio = remove_silence(spoken_audio)

# Добавление тишины в начало аудиофайлов
silence_duration = 0.2  # Задайте желаемую длительность тишины в секундах
silence_samples = int(silence_duration * 48000)
original_audio = np.concatenate((np.zeros(silence_samples), original_audio))
spoken_audio = np.concatenate((np.zeros(silence_samples), spoken_audio))

# Приведение аудиофайлов к одной длине
min_length = min(len(original_audio), len(spoken_audio))
original_audio = original_audio[:min_length]
spoken_audio = spoken_audio[:min_length]

# Нормализация амплитуды аудиофайлов
max_amplitude = max(np.max(np.abs(original_audio)), np.max(np.abs(spoken_audio)))
original_audio /= max_amplitude
spoken_audio /= max_amplitude

# Создание экземпляра класса для визуализации
visualizer = PronunciationVisualizer(original_audio, spoken_audio, original_sample_rate)

# Визуализация графика звуковой волны
visualizer.plot_waveform()
