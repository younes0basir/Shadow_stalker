import pygame
import numpy as np
import math
import os

def generate_beep_wave(frequency, duration, volume=0.1):
    """Generate a simple sine wave beep."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate
    # Sine wave
    wave = np.sin(2 * np.pi * frequency * t) * volume
    # Fade out to avoid clicking
    fade_len = int(sample_rate * 0.01)
    if n_samples > fade_len:
        fade = np.linspace(1, 0, fade_len)
        wave[-fade_len:] *= fade
    
    # Convert to 16-bit signed integers
    audio = (wave * 32767).astype(np.int16)
    # Duplicate for stereo
    stereo_audio = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo_audio)

class AudioSystem:
    def __init__(self):
        # Force mixer initialization if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Get the root directory for assets
        self.root_dir = os.path.dirname(os.path.dirname(__file__))
        self.sfx_dir = os.path.join(self.root_dir, "assets", "FreeSFX")
            
        # Load sounds from FreeSFX folder
        self.sounds = self._load_sounds()
        
        self.music = None
        self.music_playing = False
        self.current_music_type = None  # 'menu' or 'gameplay'
    
    def _load_sound(self, relative_path, fallback_freq=None, fallback_dur=None, fallback_vol=None):
        """Load a sound file, with fallback to generated sound if file not found."""
        full_path = os.path.join(self.root_dir, relative_path)
        if os.path.exists(full_path):
            try:
                return pygame.mixer.Sound(full_path)
            except Exception as e:
                print(f"Warning: Could not load {full_path}: {e}")
        
        # Fallback to generated sound
        if fallback_freq and fallback_dur and fallback_vol:
            return generate_beep_wave(fallback_freq, fallback_dur, fallback_vol)
        return None
    
    def _load_sounds(self):
        """Load all game sound effects from FreeSFX folder."""
        sounds = {}
        
        # UI Sounds
        sounds['hover'] = self._load_sound(
            "assets/FreeSFX/GameSFX/Events/Retro Event UI 01.wav",
            440, 0.05, 0.05
        )
        sounds['click'] = self._load_sound(
            "assets/FreeSFX/GameSFX/Events/Retro Event UI StereoUP 01.wav",
            880, 0.1, 0.1
        )
        sounds['back'] = self._load_sound(
            "assets/FreeSFX/GameSFX/Events/Negative/Retro Negative Short 07.wav",
            220, 0.1, 0.1
        )
        
        # Game Over Sounds
        sounds['game_over'] = self._load_sound(
            "assets/FreeSFX/Voices/Game Over.wav",
            150, 0.5, 0.15
        )
        sounds['death'] = self._load_sound(
            "assets/FreeSFX/GameSFX/Impact/Retro Impact Punch Hurt 01.wav",
            100, 0.3, 0.12
        )
        
        # Victory Sound
        sounds['victory'] = self._load_sound(
            "assets/FreeSFX/Voices/You Win.wav",
            660, 0.3, 0.1
        )
        
        # Additional useful sounds (for future use)
        sounds['jump'] = self._load_sound(
            "assets/FreeSFX/GameSFX/Bounce Jump/Retro Jump Simple A 01.wav"
        )
        sounds['coin'] = self._load_sound(
            "assets/FreeSFX/GameSFX/PickUp/Retro PickUp Coin 04.wav"
        )
        sounds['powerup'] = self._load_sound(
            "assets/FreeSFX/GameSFX/PowerUp/Retro PowerUP 09.wav"
        )
        sounds['explosion'] = self._load_sound(
            "assets/FreeSFX/GameSFX/Explosion/Retro Explosion Short 01.wav"
        )
        
        # Filter out None values
        return {k: v for k, v in sounds.items() if v is not None}

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def start_menu_music(self):
        """Plays a procedurally generated simple looping background ambiance."""
        if self.music_playing: return
        
        # Ensure mixer is ready
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Generate a more audible ambient pad
        sample_rate = 44100
        duration = 4.0  # 4 second loop
        n_samples = int(sample_rate * duration)
        t = np.arange(n_samples) / sample_rate
        
        # Mix a few frequencies for a richer sound
        # Using a fundamental and harmonics
        wave = (np.sin(2 * np.pi * 110 * t) * 0.4 + 
                np.sin(2 * np.pi * 165 * t) * 0.3 + 
                np.sin(2 * np.pi * 220 * t) * 0.2 +
                np.sin(2 * np.pi * 55 * t) * 0.1) # Sub-bass
        
        # Normalize and set volume
        wave = wave / np.max(np.abs(wave))
        
        # Apply a long crossfade for seamless looping
        fade_len = int(sample_rate * 0.5)
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        wave[:fade_len] *= fade_in
        wave[-fade_len:] *= fade_out
        
        # Final volume adjustment (audible but background)
        audio = (wave * 0.15 * 32767).astype(np.int16)
        stereo_audio = np.column_stack((audio, audio))
        
        self.music = pygame.sndarray.make_sound(stereo_audio)
        self.music.play(loops=-1) # Loop indefinitely
        self.music_playing = True

    def stop_music(self):
        if self.music_playing:
            self.music.stop()
            self.music_playing = False
            self.current_music_type = None
    
    def start_gameplay_music(self, music_type='nes'):
        """Start background music during gameplay.
        
        Args:
            music_type: 'nes' for NES-style loop, 'chipwave' for chipwave style
        """
        # Stop current music if playing
        if self.music_playing:
            self.stop_music()
        
        # Ensure mixer is ready
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Select music file based on type
        if music_type == 'nes':
            music_path = "assets/FreeSFX/GameSFX/Music/Nes Style/Retro Music Loop - PV8 - NES Style 01.wav"
        elif music_type == 'chipwave':
            music_path = "assets/FreeSFX/GameSFX/Music/ChipWave/Retro Music - ABMU - ChipWave 01.wav"
        else:
            # Default to NES style
            music_path = "assets/FreeSFX/GameSFX/Music/Nes Style/Retro Music Loop - PV8 - NES Style 01.wav"
        
        full_path = os.path.join(self.root_dir, music_path)
        
        if os.path.exists(full_path):
            try:
                # Load music file
                self.music = pygame.mixer.Sound(full_path)
                # Set volume lower for background music (30% volume)
                self.music.set_volume(0.3)
                # Play in infinite loop
                self.music.play(loops=-1)
                self.music_playing = True
                self.current_music_type = 'gameplay'
                print(f"[Audio] Gameplay music started: {music_type}")
            except Exception as e:
                print(f"Warning: Could not load gameplay music: {e}")
                self.current_music_type = None
        else:
            print(f"Warning: Music file not found: {full_path}")
            self.current_music_type = None

audio_sys = AudioSystem()
