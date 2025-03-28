import json
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
        self.paused = False
        
        pygame.mixer.init()
        
        self.folder_picker = ft.FilePicker(on_result=self.pick_folder)
        page.overlay.append(self.folder_picker)
        
        self.playlist_dropdown = ft.Dropdown(
            options=[],
            on_change=self.select_playlist
        )
        
        self.music_table = ft.DataTable(columns=[
            ft.DataColumn(ft.Text("File Name")),
            ft.DataColumn(ft.Text("Artist")),
            ft.DataColumn(ft.Text("Duration")),
            ft.DataColumn(ft.Text("Add to Playlist")),
            ft.DataColumn(ft.Text("Remove from Playlist"))
        ], rows=[])
        
        self.playlist_view = ft.ListView()
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Music Playlist Organizer", size=24, weight="bold"),
                    ft.Row([
                        ft.ElevatedButton("Select Folder", on_click=lambda _: self.folder_picker.get_directory_path()),
                        ft.ElevatedButton("Create Playlist", on_click=self.create_playlist),
                        ft.ElevatedButton("Delete Playlist", on_click=self.delete_playlist),
                        ft.ElevatedButton("Save Playlists", on_click=self.save_playlists),
                        ft.ElevatedButton("Load Playlists", on_click=self.load_playlists)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    self.playlist_dropdown,
                    self.music_table,
                    ft.Text("Playlists", size=20, weight="bold"),
                    self.playlist_view,
                    ft.Row([
                        ft.ElevatedButton("Play", on_click=self.play_music),
                        ft.ElevatedButton("Pause", on_click=self.pause_music),
                        ft.ElevatedButton("Stop", on_click=self.stop_music),
                        ft.ElevatedButton("Next", on_click=self.next_song),
                        ft.ElevatedButton("Previous", on_click=self.previous_song)
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                padding=20,
                border_radius=10,
                bgcolor=ft.colors.GREY_900
            )
        )
    
    def pause_music(self, e):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            self.paused = True
        elif self.paused:
            pygame.mixer.music.unpause()
            self.playing = True
            self.paused = False

    def stop_music(self, e):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False

    def play_music(self, e):
        if self.current_playlist and self.playlists[self.current_playlist]:
            if self.paused:
                pygame.mixer.music.unpause()
                self.playing = True
                self.paused = False
            else:
                self.current_song_index = 0
                self.load_and_play_song()
    
    def load_and_play_song(self):
        song_path = self.playlists[self.current_playlist][self.current_song_index]
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        self.playing = True
        self.paused = False

    def next_song(self, e):
        if self.current_playlist and self.current_song_index < len(self.playlists[self.current_playlist]) - 1:
            self.current_song_index += 1
            self.load_and_play_song()
    
    def previous_song(self, e):
        if self.current_playlist and self.current_song_index > 0:
            self.current_song_index -= 1
            self.load_and_play_song()
    
    def delete_playlist(self, e):
        if self.current_playlist in self.playlists:
            del self.playlists[self.current_playlist]
            self.current_playlist = None
            self.update_playlist_dropdown()
            self.update_playlist_view()
    
    def pick_folder(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.music_folder = Path(e.path)
            self.scan_music_folder()
    
    def scan_music_folder(self):
        if not self.music_folder:
            return
        
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
                        ft.DataCell(ft.Text(metadata["artist"])),
                        ft.DataCell(ft.Text(metadata["duration"])),
                        ft.DataCell(ft.ElevatedButton("Add", on_click=lambda e, f=file_path: self.add_to_playlist(f))),
                        ft.DataCell(ft.ElevatedButton("Remove", on_click=lambda e, f=file_path: self.remove_from_playlist(f)))
                    ])
                )
        
        self.page.update()
    
    def get_metadata(self, file_path):
        try:
            if file_path.suffix == ".mp3":
                audio = MP3(file_path)
            else:
                audio = WAVE(file_path)
            duration = int(audio.info.length)
            return {"artist": "Unknown", "album": "Unknown", "duration": f"{duration // 60}:{duration % 60:02}"}
        except:
            return {"artist": "Unknown", "album": "Unknown", "duration": "0:00"}
    
    def create_playlist(self, e):
        playlist_name = f"Playlist {len(self.playlists) + 1}"
        self.playlists[playlist_name] = []
        self.update_playlist_dropdown()
        self.update_playlist_view()
    
    def select_playlist(self, e):
        self.current_playlist = self.playlist_dropdown.value
    
    def add_to_playlist(self, file_path):
        if not self.playlists or not self.current_playlist:
            return
        if str(file_path) not in self.playlists[self.current_playlist]:
            self.playlists[self.current_playlist].append(str(file_path))
            self.update_playlist_view()
    
    def remove_from_playlist(self, file_path):
        if self.current_playlist and str(file_path) in self.playlists[self.current_playlist]:
            self.playlists[self.current_playlist].remove(str(file_path))
            self.update_playlist_view()
    
    def save_playlists(self, e):
        with open("playlists.json", "w") as f:
            json.dump(self.playlists, f)
    
    def load_playlists(self, e):
        try:
            with open("playlists.json", "r") as f:
                self.playlists = json.load(f)
                self.update_playlist_dropdown()
                self.update_playlist_view()
        except FileNotFoundError:
            pass
    
    def update_playlist_dropdown(self):
        self.playlist_dropdown.options = [ft.dropdown.Option(name) for name in self.playlists.keys()]
        self.page.update()
    
    def update_playlist_view(self):
        self.playlist_view.controls.clear()
        for name, songs in self.playlists.items():
            self.playlist_view.controls.append(ft.Text(f"{name}: {', '.join(songs)}"))
        self.page.update()

def main(page: ft.Page):
    page.title = "Music Playlist Organizer"
    app = MusicApp(page)
    page.update()

ft.app(target=main)
