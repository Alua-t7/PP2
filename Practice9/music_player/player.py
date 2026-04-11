import pygame
import os

class MusicPlayer:
    def __init__(self, tracks_folder):
        pygame.mixer.init()
        self.tracks = self._load_tracks(tracks_folder)
        self.index = 0
        self.playing = False
        self.start_time = 0  # when current track started

    def _load_tracks(self, folder):
        supported = (".mp3", ".wav")
        files = [
            os.path.join(folder, f)
            for f in sorted(os.listdir(folder))
            if f.endswith(supported)
        ]
        if not files:
            raise FileNotFoundError(f"No audio files found in '{folder}'")
        return files

    def current_track_name(self):
        name = os.path.basename(self.tracks[self.index])
        return os.path.splitext(name)[0]  # strip extension

    def play(self):
        pygame.mixer.music.load(self.tracks[self.index])
        pygame.mixer.music.play()
        self.start_time = pygame.time.get_ticks()
        self.playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def next_track(self):
        self.index = (self.index + 1) % len(self.tracks)
        self.play()

    def prev_track(self):
        self.index = (self.index - 1) % len(self.tracks)
        self.play()

    def get_position_seconds(self):
        if not self.playing:
            return 0
        return (pygame.time.get_ticks() - self.start_time) / 1000