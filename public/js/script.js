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
const cornersTotalesEl = $("#cornersTotales");

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
      equipo_local_id: equipos_dict[homeSel.value],
      equipo_visitante_id: equipos_dict[awaySel.value]
    };

    // Hacer predicción de resultado
    const resResultado = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    if(!resResultado.ok) {
      throw new Error(`HTTP ${resResultado.status}`);
    }
    
    const dataResultado = await resResultado.json();
    
    // Hacer predicción de corners
    const resCorners = await fetch("/api/predict-corners", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    // Obtener datos históricos
    const resHistoricos = await fetch("/api/historical-data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    let dataCorners = null;
    if(resCorners.ok) {
      dataCorners = await resCorners.json();
    }
    
    let dataHistoricos = null;
    if(resHistoricos.ok) {
      dataHistoricos = await resHistoricos.json();
    }
    
    // Combinar resultados
    const combinedData = {
      ...dataResultado,
      corners_data: dataCorners,
      historicos: dataHistoricos
    };
    
    renderResults(combinedData);
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
    cornersTotalesEl.textContent = "—";
    return;
  }

  // Mostrar resultado del partido
  if (res.goles_local && res.goles_visitante) {
    const golesLocal = res.goles_local.rounded;
    const golesVisitante = res.goles_visitante.rounded;
    
    // Mostrar marcador
    scoreEl.textContent = `${golesLocal} - ${golesVisitante}`;
    
    // Determinar probabilidades basadas en el resultado
    let homeProb = 0, drawProb = 0, awayProb = 0;
    
    if (res.resultado_1x2 === 1) {
      homeProb = 0.6;
      drawProb = 0.25;
      awayProb = 0.15;
    } else if (res.resultado_1x2 === 0) {
      homeProb = 0.25;
      drawProb = 0.5;
      awayProb = 0.25;
    } else {
      homeProb = 0.15;
      drawProb = 0.25;
      awayProb = 0.6;
    }
    
    // Actualizar barras de probabilidad
    barHome.style.width = `${homeProb * 100}%`;
    barDraw.style.width = `${drawProb * 100}%`;
    barAway.style.width = `${awayProb * 100}%`;
    
    pctHome.textContent = `${Math.round(homeProb * 100)}%`;
    pctDraw.textContent = `${Math.round(drawProb * 100)}%`;
    pctAway.textContent = `${Math.round(awayProb * 100)}%`;
    
    // Mostrar información adicional
    console.log(`Predicción: ${homeSel.value} ${golesLocal} - ${golesVisitante} ${awaySel.value}`);
    console.log(`Resultado: ${res.resultado_1x2 === 1 ? 'Local' : res.resultado_1x2 === 0 ? 'Empate' : 'Visitante'}`);
    console.log(`Fecha de corte: ${res.as_of}`);
    console.log(`Modelo usado: ${res.model_type} (${res.model_version})`);
    console.log(`Nota: ${res.prediction_note}`);
    
    // Mostrar corners si están disponibles
    if (res.corners_data && res.corners_data.corners_totales) {
      cornersTotalesEl.textContent = Math.round(res.corners_data.corners_totales);
      console.log(`Corners totales: ${res.corners_data.corners_totales}`);
      console.log(`Modelo de corners: ${res.corners_data.model_type} (${res.corners_data.model_version})`);
      console.log(`Escalador: ${res.corners_data.scaler_type}`);
      console.log(`Nota corners: ${res.corners_data.prediction_note}`);
    } else {
      cornersTotalesEl.textContent = "—";
    }
    
    // Mostrar datos históricos si están disponibles
    if (res.historicos) {
      const hist = res.historicos;
      

      
      // Datos del enfrentamiento histórico
      if (hist.enfrentamiento_historico) {
        const enf = hist.enfrentamiento_historico;
        
        document.getElementById('totalEnfrentamientos').textContent = enf.total_partidos;
        document.getElementById('promedioGolesEnfrentamiento').textContent = 
          `${enf.goles_promedio.toFixed(2)} por partido`;

        document.getElementById('victoriasLocal').textContent = enf.victorias_local;
        document.getElementById('empates').textContent = enf.empates;
        document.getElementById('victoriasVisitante').textContent = enf.victorias_visitante;
        document.getElementById('posesionLocalHist').textContent = Math.round(enf.posesion_local_promedio) + '%';
        document.getElementById('posesionVisitanteHist').textContent = Math.round(enf.posesion_visitante_promedio) + '%';
      }
      
      console.log('📊 Datos históricos cargados:', hist);
    } else {
      // Limpiar datos históricos si no están disponibles
      document.getElementById('totalEnfrentamientos').textContent = "—";
      document.getElementById('promedioGolesEnfrentamiento').textContent = "—";
      document.getElementById('posesionLocalHist').textContent = "—";
      document.getElementById('posesionVisitanteHist').textContent = "—";
      document.getElementById('victoriasLocal').textContent = "—";
      document.getElementById('empates').textContent = "—";
      document.getElementById('victoriasVisitante').textContent = "—";

    }
  } else {
    // Limpiar si no hay datos
    barHome.style.width = "0%";
    barDraw.style.width = "0%";
    barAway.style.width = "0%";
    pctHome.textContent = "—";
    pctDraw.textContent = "—";
    pctAway.textContent = "—";
    scoreEl.textContent = "—";
    cornersTotalesEl.textContent = "—";
  }
}

// Utilidad
function randomInt(min, max){
  return Math.floor(Math.random() * (max - min + 1)) + min;
}