import pygame

class MusicApp:
    def __init__(self, page: ft.Page):
        pygame.mixer.init()
        self.current_song_index = 0
        self.playing = False

        self.page.add(
            ft.Row([
                ft.ElevatedButton("Reproducir", on_click=self.play_music),
                ft.ElevatedButton("Pausar", on_click=self.pause_music),
                ft.ElevatedButton("Detener", on_click=self.stop_music),
            ])
        )

    def play_music(self, e):
        if self.music_files:
            pygame.mixer.music.load(self.music_files[self.current_song_index][1])
            pygame.mixer.music.play()
            self.playing = True

    def pause_music(self, e):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False

    def stop_music(self, e):
        pygame.mixer.music.stop()
        self.playing = False
