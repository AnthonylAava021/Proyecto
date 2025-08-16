// =======================
//  Diccionario (intacto)
// =======================
const equipos_dict = {
  'Barcelona SC': 0,
  'El Nacional': 2,
  'Emelec': 4,
  'LDU de Quito': 5,
  'Mushuc Runa SC': 6,
  'Independiente del Valle': 7,
  'CD Tecnico Universitario': 8,
  'Delfin': 9,
  'Deportivo Cuenca': 10,
  'Aucas': 12,
  'Universidad Catolica': 13,
  'CSD Macara': 14,
  'Orense SC': 15,
  'Manta FC': 17,
  'Libertad': 20,
  'Vinotinto': 22
};

// =======================
//  Configuración de rutas
// =======================
// Si tus imágenes están junto a index.html, deja "./".
// Si las mueves a ./assets/, cambia a "./assets/".
const ASSETS_BASE = "./img/";
const API_ENDPOINT = "/api/predict"; // cambia si tu backend vive en otro lado

// Nombres de archivo EXACTOS (según tu carpeta)
const NAME_TO_FILE = {
  "Barcelona SC": "Barcelona_Sporting_Club_Logo.png",
  "El Nacional": "Nacional.png",
  "Emelec": "EscudoCSEmelec.png",
  "LDU de Quito": "Liga_Deportiva_Universitaria_de_Quito.png",
  "Mushuc Runa SC": "MushucRuna.png",
  "Independiente del Valle": "Independiente_del_Valle_Logo_2022.png",
  "CD Tecnico Universitario": "Técnico_Universitario.png",
  "Delfin": "Delfín_SC_logo.png",
  "Deportivo Cuenca": "Depcuenca.png",
  "Aucas": "SD_Aucas_logo.png",
  "Universidad Catolica": "Ucatólica.png",
  "CSD Macara": "Macara_6.png",
  "Orense SC": "Orense_SC_logo.png",
  "Manta FC": "Manta_F.C.png",
  "Libertad": "Libertad_FC_Ecuador.png",
  "Vinotinto": "Vinotinto.png"
};

// fondo (tu archivo se llama bg.jpg)
const BG_FILE = "bg.jpg";

// =======================
//  Helpers UI
// =======================
const $ = (sel, root = document) => root.querySelector(sel);

const bgDiv   = $(".bg");
const homeSel = $("#homeSelect");
const awaySel = $("#awaySelect");
const homeLogo = $("#homeLogo");
const awayLogo = $("#awayLogo");
const swapBtn  = $("#swapBtn");
const predictBtn = $("#predictBtn");

const lblHome = $("#lblHome");
const lblAway = $("#lblAway");
const barHome = $("#barHome");
const barDraw = $("#barDraw");
const barAway = $("#barAway");
const pctHome = $("#pctHome");
const pctDraw = $("#pctDraw");
const pctAway = $("#pctAway");
const scoreEl = $("#score");

// NUEVOS: elementos para Córners y Tarjetas
const cornersTotalesEl = $("#cornersTotales");
const cardsHomeEl   = $("#cardsHome");
const cardsAwayEl   = $("#cardsAway");

const notice  = $("#notice");

// fija el fondo sin importar dónde esté
bgDiv.style.backgroundImage = `url('./img/${BG_FILE}')`;

// opciones por defecto
const TEAM_NAMES = Object.keys(equipos_dict);
const DEFAULT_HOME = "Emelec";
const DEFAULT_AWAY = "Barcelona SC";

// Rellena selects respetando el diccionario
function populateSelects(){
  TEAM_NAMES.forEach(name => {
    const o1 = document.createElement("option");
    o1.value = name; o1.textContent = name; homeSel.appendChild(o1);
    const o2 = document.createElement("option");
    o2.value = name; o2.textContent = name; awaySel.appendChild(o2);
  });
  homeSel.value = DEFAULT_HOME;
  awaySel.value = DEFAULT_AWAY;
  updateLogosAndLabels();
}
populateSelects();

// devuelve la ruta exacta según tu carpeta
function teamLogo(name){
  const file = NAME_TO_FILE[name];
  return file ? ASSETS_BASE + file : "";
}

function setLogo(img, teamName){
  const src = teamLogo(teamName);
  img.src = src;
  img.alt = teamName;
  img.onerror = () => { img.style.visibility = "hidden"; };
  img.onload  = () => { img.style.visibility = "visible"; };
}

function updateLogosAndLabels(){
  const h = homeSel.value, a = awaySel.value;
  setLogo(homeLogo, h);
  setLogo(awayLogo, a);
  lblHome.textContent = `Gana ${h}`;
  lblAway.textContent = `Gana ${a}`;
}

homeSel.addEventListener("change", () => {
  if (homeSel.value === awaySel.value) {
    const idx = TEAM_NAMES.indexOf(homeSel.value);
    awaySel.value = TEAM_NAMES[(idx + 1) % TEAM_NAMES.length];
  }
  updateLogosAndLabels();
});
awaySel.addEventListener("change", () => {
  if (awaySel.value === homeSel.value) {
    const idx = TEAM_NAMES.indexOf(awaySel.value);
    homeSel.value = TEAM_NAMES[(idx + 1) % TEAM_NAMES.length];
  }
  updateLogosAndLabels();
});

swapBtn.addEventListener("click", () => {
  const tmp = homeSel.value;
  homeSel.value = awaySel.value;
  awaySel.value = tmp;
  updateLogosAndLabels();
});

// =======================
//  Predicción
// =======================
predictBtn.addEventListener("click", predict);

async function predict(){
  setLoading(true);
  notice.classList.add("hide");
  try{
    const payload = {
      home_name: homeSel.value,
      away_name: awaySel.value,
      home_code: equipos_dict[homeSel.value],
      away_code: equipos_dict[awaySel.value]
    };

    const res = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if(!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    
    const data = await res.json();
    renderResults(data);
  } catch(e){
    console.error(e);
    showNotice("Error conectando con el servidor. Verifica que el backend esté funcionando.");
  } finally{
    setLoading(false);
  }
}

function setLoading(on){
  predictBtn.disabled = on;
  predictBtn.textContent = on ? "Calculando…" : "Predecir";
}

function showNotice(msg){
  notice.textContent = msg;
  notice.classList.remove("hide");
}

function renderResults(res){
  // Verificar si hay error
  if (res.error) {
    showNotice(res.error);
    // Limpiar resultados
    barHome.style.width = "0%";
    barDraw.style.width = "0%";
    barAway.style.width = "0%";
    pctHome.textContent = "—";
    pctDraw.textContent = "—";
    pctAway.textContent = "—";
    scoreEl.textContent = "—";
    if (cornersTotalesEl) cornersTotalesEl.textContent = "—";
    if (cardsHomeEl) cardsHomeEl.textContent = "—";
    if (cardsAwayEl) cardsAwayEl.textContent = "—";
    return;
  }

  // Solo mostrar corners si hay predicción exitosa
  if (res.corners_totales !== null && res.corners_totales !== undefined) {
    const cornersTotales = Math.round(res.corners_totales);
    if (cornersTotalesEl) cornersTotalesEl.textContent = cornersTotales;
  } else {
    if (cornersTotalesEl) cornersTotalesEl.textContent = "—";
  }

  // Los otros campos se mantienen vacíos ya que no tenemos esos modelos
  barHome.style.width = "0%";
  barDraw.style.width = "0%";
  barAway.style.width = "0%";
  pctHome.textContent = "—";
  pctDraw.textContent = "—";
  pctAway.textContent = "—";
  scoreEl.textContent = "—";
  if (cardsHomeEl) cardsHomeEl.textContent = "—";
  if (cardsAwayEl) cardsAwayEl.textContent = "—";
}

// Utilidad
function randomInt(min, max){
  return Math.floor(Math.random() * (max - min + 1)) + min;
}