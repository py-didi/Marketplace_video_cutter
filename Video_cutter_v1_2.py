import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import logging
from datetime import datetime
import json

class VideoProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработчик видео")
        self.root.geometry("600x450")

        # Настройка логирования
        log_file = f"video_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        logging.info("Программа запущена")

        # Путь к ffmpeg.exe и ffprobe.exe
        self.FFMPEG_PATH = os.path.join("ffmpeg", "bin", "ffmpeg.exe")
        self.FFPROBE_PATH = os.path.join("ffmpeg", "bin", "ffprobe.exe")
        logging.debug(f"Установлен путь к FFmpeg: {self.FFMPEG_PATH}, FFprobe: {self.FFPROBE_PATH}")

        # Переменные для прогресса
        self.video_files_count = 0
        self.current_file_index = 0

        # Создаем и размещаем элементы интерфейса
        self.create_widgets()

    def create_widgets(self):
        logging.debug("Создание элементов интерфейса")
        tk.Label(self.root, text="Входная папка:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_folder_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.input_folder_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Обзор", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.root, text="Выходная папка:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.output_folder_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Обзор", command=self.browse_output).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(self.root, text="Обрезать с начала (сек):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.start_time_var = tk.StringVar(value="0")
        tk.Entry(self.root, textvariable=self.start_time_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.root, text="Итоговая длительность (сек):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.duration_var = tk.StringVar(value="20")
        tk.Entry(self.root, textvariable=self.duration_var, width=10).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.root, text="Ширина видео (пиксели):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.target_width_var = tk.StringVar(value="1200")
        tk.Entry(self.root, textvariable=self.target_width_var, width=10).grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.root, text="Высота видео (пиксели):").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.target_height_var = tk.StringVar(value="1600")
        tk.Entry(self.root, textvariable=self.target_height_var, width=10).grid(row=5, column=1, padx=5, pady=5, sticky="w")

        self.files_count_var = tk.StringVar(value="Найдено файлов: 0")
        tk.Label(self.root, textvariable=self.files_count_var).grid(row=6, column=0, columnspan=3, padx=5, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        tk.Button(self.root, text="Обработать видео", command=self.process_videos).grid(row=8, column=1, pady=10)

        self.status_var = tk.StringVar(value="Готово")
        tk.Label(self.root, textvariable=self.status_var, wraplength=500).grid(row=9, column=0, columnspan=3, padx=5, pady=5)
        logging.debug("Элементы интерфейса созданы")

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder_var.set(folder)
            self.update_files_count()
            logging.info(f"Выбрана входная папка: {folder}")

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder_var.set(folder)
            logging.info(f"Выбрана выходная папка: {folder}")

    def update_files_count(self):
        input_folder = self.input_folder_var.get()
        if os.path.exists(input_folder):
            video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
            self.video_files_count = len(video_files)
            self.files_count_var.set(f"Найдено файлов: {self.video_files_count}")
            logging.info(f"Найдено {self.video_files_count} видеофайлов в {input_folder}: {video_files}")
        else:
            self.video_files_count = 0
            self.files_count_var.set("Найдено файлов: 0")
            logging.warning(f"Входная папка {input_folder} не существует")

    def get_video_info(self, input_path):
        """Получает информацию о видео с помощью ffprobe."""
        try:
            ffprobe_command = [
                self.FFPROBE_PATH,
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration:stream_tags=rotate:side_data",
                "-of", "json",
                input_path
            ]
            logging.debug(f"Команда ffprobe: {' '.join(ffprobe_command)}")
            probe_result = subprocess.run(ffprobe_command, capture_output=True, text=True)
            probe_data = json.loads(probe_result.stdout)

            stream = probe_data["streams"][0]
            width = stream["width"]
            height = stream["height"]
            duration = float(stream.get("duration", 0))

            # Проверка поворота
            rotation = 0
            if "tags" in stream and "rotate" in stream["tags"]:
                rotation = int(stream["tags"]["rotate"])
            elif "side_data_list" in stream:
                for side_data in stream["side_data_list"]:
                    if side_data.get("side_data_type") == "Display Matrix":
                        rotation_value = side_data.get("rotation", 0)
                        rotation = int(rotation_value / 1000)  # Преобразование в градусы
                        break

            logging.info(f"Видео: {input_path}, разрешение: {width}x{height}, длительность: {duration} сек, поворот: {rotation} градусов")
            return width, height, duration, rotation
        except Exception as e:
            logging.error(f"Ошибка ffprobe для {input_path}: {str(e)}")
            self.status_var.set(f"Ошибка получения информации о видео: {str(e)}")
            return None, None, None, None

    def process_videos(self):
        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()
        logging.info(f"Начало обработки. Входная папка: {input_folder}, Выходная папка: {output_folder}")

        try:
            start_time = float(self.start_time_var.get())
            logging.debug(f"Время обрезки с начала: {start_time} сек")
            if start_time < 0:
                messagebox.showerror("Ошибка", "Время обрезки с начала не может быть отрицательным!")
                logging.error("Отрицательное время обрезки")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Неверное значение времени обрезки с начала!")
            logging.error("Неверное значение времени обрезки")
            return

        try:
            end_time = float(self.duration_var.get())
            logging.debug(f"Итоговая длительность: {end_time} сек")
            if end_time <= 0:
                messagebox.showerror("Ошибка", "Итоговая длительность должна быть положительным числом!")
                logging.error("Отрицательная или нулевая длительность")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Неверное значение итоговой длительности!")
            logging.error("Неверное значение длительности")
            return

        try:
            target_width = int(self.target_width_var.get())
            logging.debug(f"Целевая ширина: {target_width} пикс")
            if target_width <= 0:
                messagebox.showerror("Ошибка", "Ширина видео должна быть положительным числом!")
                logging.error("Отрицательная или нулевая ширина")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Неверное значение ширины видео!")
            logging.error("Неверное значение ширины")
            return

        try:
            target_height = int(self.target_height_var.get())
            logging.debug(f"Целевая высота: {target_height} пикс")
            if target_height <= 0:
                messagebox.showerror("Ошибка", "Высота видео должна быть положительным числом!")
                logging.error("Отрицательная или нулевая высота")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Неверное значение высоты видео!")
            logging.error("Неверное значение высоты")
            return

        if not os.path.exists(input_folder):
            messagebox.showerror("Ошибка", f"Входная папка '{input_folder}' не существует!")
            logging.error(f"Входная папка '{input_folder}' не существует")
            return

        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                self.status_var.set(f"Создана выходная папка: '{output_folder}'")
                logging.info(f"Создана выходная папка: {output_folder}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать выходную папку: {str(e)}")
            logging.error(f"Ошибка создания выходной папки: {str(e)}")
            return

        if not os.path.exists(self.FFMPEG_PATH):
            messagebox.showerror("Ошибка", f"FFmpeg не найден по пути '{self.FFMPEG_PATH}'!")
            logging.error(f"FFmpeg не найден: {self.FFMPEG_PATH}")
            return

        if not os.path.exists(self.FFPROBE_PATH):
            messagebox.showerror("Ошибка", f"FFprobe не найден по пути '{self.FFPROBE_PATH}'!")
            logging.error(f"FFprobe не найден: {self.FFPROBE_PATH}")
            return

        video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        self.video_files_count = len(video_files)
        self.current_file_index = 0
        self.files_count_var.set(f"Найдено файлов: {self.video_files_count}")
        logging.info(f"Найдено файлов: {self.video_files_count}, список: {video_files}")

        if not video_files:
            messagebox.showerror("Ошибка", f"В папке '{input_folder}' не найдено видеофайлов!")
            logging.error(f"Видеофайлы не найдены в {input_folder}")
            return

        self.status_var.set(f"Найдено {self.video_files_count} видеофайлов")
        self.progress_var.set(0)
        self.root.update()

        for filename in video_files:
            self.current_file_index += 1
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"processed_{filename}")
            logging.info(f"Обработка файла {self.current_file_index}/{self.video_files_count}: {filename}")

            self.status_var.set(f"Обработка файла {self.current_file_index}/{self.video_files_count}: {filename}")
            self.progress_var.set((self.current_file_index / self.video_files_count) * 100)
            self.root.update()

            # Получение информации о видео
            width, height, duration, rotation = self.get_video_info(input_path)
            if width is None or height is None or duration is None:
                self.status_var.set(f"Ошибка: Не удалось получить информацию о видео '{filename}'")
                logging.error(f"Пропуск файла {filename} из-за ошибки ffprobe")
                continue

            # Проверка длительности
            if duration < start_time:
                self.status_var.set(f"Ошибка: Видео '{filename}' короче времени обрезки ({start_time} сек). Пропускаем.")
                logging.warning(f"Видео {filename} короче времени обрезки: {duration} < {start_time}")
                continue

            actual_end_time = min(duration - start_time, end_time)
            logging.info(f"Обрезка видео: с {start_time} до {start_time + actual_end_time} секунд")

            # Учет поворота
            effective_width, effective_height = width, height
            if abs(rotation) == 90 or abs(rotation) == 270:
                effective_width, effective_height = height, width
                logging.info(f"Учет поворота: новое разрешение {effective_width}x{effective_height}")

            aspect_ratio = effective_width / effective_height
            target_aspect = target_width / target_height

            # Формирование фильтров
            filters = []
            if abs(rotation) == 90:
                filters.append("transpose=1")
            elif abs(rotation) == 270:
                filters.append("transpose=2")

            # Масштабирование и обрезка с учетом соотношения сторон
            if aspect_ratio > target_aspect:
                scale_filter = f"scale={target_width}:-1"
                crop_filter = f"crop={target_width}:{target_height}:0:((in_h-{target_height})/2)"
            else:
                scale_filter = f"scale=-1:{target_height}"
                crop_filter = f"crop={target_width}:{target_height}:((in_w-{target_width})/2):0"

            filters.extend([scale_filter, crop_filter])
            video_filter = ",".join(filters)
            logging.info(f"FFmpeg фильтр: {video_filter}")

            # Выполнение FFmpeg
            command = [
                self.FFMPEG_PATH,
                "-i", input_path,
                "-ss", str(start_time),
                "-t", str(actual_end_time),
                "-an",
                "-vf", video_filter,
                "-c:v", "libx264",
                "-y",
                output_path
            ]
            logging.debug(f"FFmpeg команда: {' '.join(command)}")

            try:
                result = subprocess.run(command, capture_output=True, text=True)
                logging.debug(f"FFmpeg код возврата: {result.returncode}")
                if result.returncode == 0:
                    self.status_var.set(f"Успешно обработано через FFmpeg: {output_path}")
                    if os.path.exists(output_path):
                        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        self.status_var.set(f"Размер файла: {file_size_mb:.2f} МБ")
                        logging.info(f"Файл успешно создан: {output_path}, размер: {file_size_mb:.2f} МБ")
                    else:
                        self.status_var.set(f"Ошибка: Файл {output_path} не создан после FFmpeg")
                        logging.error(f"Файл {output_path} не был создан после FFmpeg")
                else:
                    error_message = result.stderr
                    self.status_var.set(f"Ошибка FFmpeg: {error_message}")
                    logging.error(f"Ошибка FFmpeg: {error_message}")
            except Exception as e:
                self.status_var.set(f"Исключение в FFmpeg: {str(e)}")
                logging.error(f"Исключение в FFmpeg: {str(e)}")

            self.root.update()

        self.status_var.set("Обработка завершена!")
        self.progress_var.set(100)
        messagebox.showinfo("Успех", "Обработка видео завершена!")
        logging.info("Обработка завершена")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessorApp(root)
    root.mainloop()