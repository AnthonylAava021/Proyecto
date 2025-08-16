// =======================
//  Música de Fondo Automática
// =======================

let isMusicPlaying = false;
let musicVolume = 0.3; // Volumen inicial al 30%

// Elementos del DOM
const audioElement = document.getElementById('background-music');

// Función para iniciar la música
function startMusic() {
  if (audioElement) {
    audioElement.volume = musicVolume;
    audioElement.play().then(() => {
      isMusicPlaying = true;
      console.log('🎵 Música de fondo iniciada automáticamente');
    }).catch(error => {
      console.log('No se pudo reproducir la música automáticamente:', error);
      // En algunos navegadores, el autoplay está bloqueado
      // El usuario tendrá que hacer clic en cualquier parte
    });
  }
}

// Función para ajustar el volumen
function setVolume(volume) {
  if (audioElement) {
    musicVolume = Math.max(0, Math.min(1, volume));
    audioElement.volume = musicVolume;
  }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
  // Eventos del audio
  if (audioElement) {
    audioElement.addEventListener('play', () => {
      isMusicPlaying = true;
    });
    
    audioElement.addEventListener('pause', () => {
      isMusicPlaying = false;
    });
    
    audioElement.addEventListener('ended', () => {
      // La música está en loop, pero por si acaso
      if (audioElement.loop) {
        audioElement.play();
      }
    });
    
    audioElement.addEventListener('error', (error) => {
      console.error('Error con el audio:', error);
    });
  }
  
  // Intentar iniciar la música automáticamente
  startMusic();
});

// Función para manejar la interacción del usuario (requerida por algunos navegadores)
function enableAudioOnUserInteraction() {
  if (audioElement && !isMusicPlaying) {
    startMusic();
  }
}

// Agregar event listeners para interacciones del usuario
document.addEventListener('click', enableAudioOnUserInteraction, { once: true });
document.addEventListener('keydown', enableAudioOnUserInteraction, { once: true });
document.addEventListener('touchstart', enableAudioOnUserInteraction, { once: true });

// Exportar funciones para uso global
window.backgroundMusic = {
  start: startMusic,
  setVolume: setVolume,
  isPlaying: () => isMusicPlaying
};
