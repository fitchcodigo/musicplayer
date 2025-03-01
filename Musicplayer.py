import flet as ft
import os
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

class MusicApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.music_folder = None
        self.music_files = []

        self.folder_picker = ft.FilePicker(on_result=self.pick_folder)
        page.overlay.append(self.folder_picker)

        self.music_table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Nombre del archivo")),
            ft.DataColumn(ft.Text("Duración")),
        ], rows=[])

        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Escáner de Música", size=24, weight="bold"),
                    ft.ElevatedButton("Seleccionar Carpeta", on_click=lambda _: self.folder_picker.get_directory_path()),
                    self.music_table,
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                padding=20
            )
        )

    def pick_folder(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.music_folder = Path(e.path)
            self.scan_music_folder()

    def scan_music_folder(self):
        self.music_files.clear()
        self.music_table.rows.clear()

        for file in os.listdir(self.music_folder):
            if file.endswith(".mp3") or file.endswith(".wav"):
                file_path = self.music_folder / file
                metadata = self.get_metadata(file_path)
                self.music_files.append((file, file_path, metadata))
                self.music_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(file)),
                        ft.DataCell(ft.Text(metadata["duration"])),
                    ])
                )
        self.page.update()

    def get_metadata(self, file_path):
        try:
            audio = MP3(file_path) if file_path.suffix == ".mp3" else WAVE(file_path)
            duration = int(audio.info.length)
            return {"duration": f"{duration // 60}:{duration % 60:02}"}
        except:
            return {"duration": "0:00"}

def main(page: ft.Page):
    page.title = "Escáner de Música"
    app = MusicApp(page)
    page.update()

ft.app(target=main)
