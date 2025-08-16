// =======================
//  Slideshow de Fondos
// =======================

// Array de imágenes de fondo basadas en las imágenes disponibles en la carpeta img
const backgroundImages = [
  // Imagen 1: Celebración con arco "CAMPEON"
  "./img/liga_campeon2023.jpeg",
  
  // Imagen 2: Celebración en podio con fuegos artificiales
  "./img/idvcampeon.jpeg",
  
  // Imagen 3: Estadio con fuegos artificiales
  "./img/monumental.jpg",
  
  // Imagen 4: Estadio Monumental Banco Pichincha
  "./img/monumental_centenario.jpg",
  
  // Imagen 5: Estadio lleno con tifos y bengalas
  "./img/monumetal_dia.jpg",
  
  // Imagen 6: Barcelona
  "./img/barcelona.jpg"
];

let currentBackgroundIndex = 0;
let slideshowInterval;

// Función para cambiar el fondo
function changeBackground() {
  const bgDiv = document.querySelector('.bg');
  if (bgDiv) {
    // Aplicar transición suave
    bgDiv.style.transition = 'background-image 1s ease-in-out';
    bgDiv.style.backgroundImage = `url('${backgroundImages[currentBackgroundIndex]}')`;
    
    // Avanzar al siguiente fondo
    currentBackgroundIndex = (currentBackgroundIndex + 1) % backgroundImages.length;
  }
}

// Función para iniciar el slideshow
function startSlideshow() {
  // Cambiar inmediatamente al primer fondo
  changeBackground();
  
  // Configurar el intervalo para cambiar cada 10 segundos
  slideshowInterval = setInterval(changeBackground, 10000);
}

// Función para detener el slideshow
function stopSlideshow() {
  if (slideshowInterval) {
    clearInterval(slideshowInterval);
    slideshowInterval = null;
  }
}

// Iniciar el slideshow cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  startSlideshow();
});

// Exportar funciones para uso global
window.backgroundSlideshow = {
  start: startSlideshow,
  stop: stopSlideshow,
  change: changeBackground
};



