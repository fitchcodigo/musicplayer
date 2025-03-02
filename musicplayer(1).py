import flet as ft
import os
import pygame
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

class MusicApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.music_folder = None
        self.music_files = []
        self.playlists = {}
        self.current_playlist = None
        self.current_song_index = 0
        self.playing = False
        
        pygame.mixer.init()
        
        self.folder_picker = ft.FilePicker(on_result=self.pick_folder)
        page.overlay.append(self.folder_picker)
        
        self.playlist_dropdown = ft.Dropdown(
            options=[],
            on_change=self.select_playlist
        )
        
        self.music_table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("Archivo")),
            ft.DataColumn(ft.Text("Duración")),
            ft.DataColumn(ft.Text("Añadir a Lista"))
        ], rows=[])
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Organizador de Música", size=24, weight="bold"),
                    ft.ElevatedButton("Seleccionar Carpeta", on_click=lambda _: self.folder_picker.get_directory_path()),
                    self.playlist_dropdown,
                    self.music_table,
                    ft.Row([
                        ft.ElevatedButton("Reproducir", on_click=self.play_music),
                        ft.ElevatedButton("Pausar", on_click=self.pause_music),
                        ft.ElevatedButton("Detener", on_click=self.stop_music)
                    ], alignment=ft.MainAxisAlignment.CENTER)
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
                self.music_files.append((file, file_path))
                self.music_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(file)),
                        ft.DataCell(ft.Text(metadata["duration"])),
                        ft.DataCell(ft.ElevatedButton("Añadir", on_click=lambda e, f=file_path: self.add_to_playlist(f)))
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
    
    def create_playlist(self, e):
        playlist_name = f"Lista {len(self.playlists) + 1}"
        self.playlists[playlist_name] = []
        self.update_playlist_dropdown()
    
    def select_playlist(self, e):
        self.current_playlist = self.playlist_dropdown.value
    
    def add_to_playlist(self, file_path):
        if not self.playlists or not self.current_playlist:
            return
        self.playlists[self.current_playlist].append(str(file_path))
    
    def update_playlist_dropdown(self):
        self.playlist_dropdown.options = [ft.dropdown.Option(name) for name in self.playlists.keys()]
        self.page.update()
    
    def play_music(self, e):
        if self.current_playlist and self.playlists[self.current_playlist]:
            self.current_song_index = 0
            self.load_and_play_song()
    
    def load_and_play_song(self):
        song_path = self.playlists[self.current_playlist][self.current_song_index]
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        self.playing = True
    
    def pause_music(self, e):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
    
    def stop_music(self, e):
        pygame.mixer.music.stop()
        self.playing = False


def main(page: ft.Page):
    page.title = "Organizador de Música"
    app = MusicApp(page)
    page.update()

ft.app(target=main)