// ================= TUTOR IA OPCIONAL (Claude Haiku) =================
// La app funciona 100% sin esto. La clave de API la escribe la familia UNA VEZ
// en su dispositivo (Zona de familia) y vive solo en localStorage, en una clave
// SEPARADA del progreso ("laura_mates_familia") para que "Borrar mi progreso"
// nunca la toque. La clave JAMÁS se escribe en el repositorio ni en la web
// publicada. Si algo falla (sin red, clave mala, límite), la app sigue igual.
const AI_MODEL = "claude-haiku-4-5";
const AI_MAX = {retos: 10, pistas: 30, msgs: 5};       // techos duros
let famConf = {enabled: false, key: "", retos: 3, pistas: 10, msgs: 2, usage: null, lastError: null};

function famLoad(){
  try{ famConf = Object.assign(famConf, JSON.parse(localStorage.getItem("laura_mates_familia")||"{}")); }catch(e){}
  famUsage();
}
function famSave(){ try{ localStorage.setItem("laura_mates_familia", JSON.stringify(famConf)); }catch(e){} }
function famUsage(){
  const d = new Date(), hoy = d.toDateString(), mes = d.getFullYear()+"-"+d.getMonth();
  if(!famConf.usage) famConf.usage = {date:hoy, mes:mes, retos:0, pistas:0, msgs:0, tokIn:0, tokOut:0, calls:0};
  if(famConf.usage.date !== hoy){ famConf.usage.date = hoy; famConf.usage.retos = 0; famConf.usage.pistas = 0; famConf.usage.msgs = 0; }
  if(famConf.usage.mes !== mes){ famConf.usage.mes = mes; famConf.usage.tokIn = 0; famConf.usage.tokOut = 0; famConf.usage.calls = 0; }
}

let aiCooldown = 0, aiKeyFails = 0;
function aiOn(){ return famConf.enabled && !!famConf.key; }
function aiAllowed(tipo){
  famUsage();
  if(!aiOn()) return false;
  if(typeof navigator !== "undefined" && navigator.onLine === false) return false;
  if(Date.now() < aiCooldown) return false;
  if(tipo && famConf.usage[tipo] >= Math.min(famConf[tipo], AI_MAX[tipo])) return false;
  return true;
}

async function aiCall(system, user, schema, maxTok, tipo){
  try{
    const body = {model: AI_MODEL, max_tokens: maxTok||500, system: system,
                  messages: [{role: "user", content: user}]};
    if(schema) body.output_config = {format: {type: "json_schema", schema: schema}};
    const opts = {method: "POST",
      headers: {"Content-Type": "application/json", "x-api-key": famConf.key,
                "anthropic-version": "2023-06-01",
                "anthropic-dangerous-direct-browser-access": "true"},
      body: JSON.stringify(body)};
    try{ if(window.AbortSignal && AbortSignal.timeout) opts.signal = AbortSignal.timeout(15000); }catch(e){}
    const res = await fetch("https://api.anthropic.com/v1/messages", opts);
    if(res.status === 401 || res.status === 403){
      aiKeyFails++;
      if(aiKeyFails >= 2){ famConf.enabled = false; famConf.lastError = "key"; famSave(); }
      return null;
    }
    if(res.status === 429 || res.status === 529){ aiCooldown = Date.now() + 600000; return null; }
    if(!res.ok) return null;
    aiKeyFails = 0;
    const data = await res.json();
    famUsage();
    if(data.usage){
      famConf.usage.tokIn += data.usage.input_tokens||0;
      famConf.usage.tokOut += data.usage.output_tokens||0;
      famConf.usage.calls++;
    }
    if(tipo) famConf.usage[tipo] = (famConf.usage[tipo]||0) + 1;
    famConf.lastError = null; famSave();
    const txt = (data.content||[]).filter(b=>b.type==="text").map(b=>b.text).join("");
    return schema ? JSON.parse(txt) : txt;
  }catch(e){ return null; }
}
function aiCostMes(){ famUsage(); return (famConf.usage.tokIn*1 + famConf.usage.tokOut*5)/1e6; }
function escT(s){ return String(s==null?"":s).replace(/[<>&"]/g, c=>({"<":"&lt;",">":"&gt;","&":"&amp;",'"':"&quot;"}[c])); }

// ---- generación de ejercicios (Reto del gato) ----
const AI_RETO_SCHEMA = {
  type: "object", additionalProperties: false, required: ["ejercicios"],
  properties: { ejercicios: { type: "array", items: {
    type: "object", additionalProperties: false,
    required: ["tipo", "a", "b", "texto", "emoji"],
    properties: {
      tipo: {type: "string", enum: ["sub", "mul", "miss", "prob_mul", "prob_sub"]},
      a: {type: "integer"}, b: {type: "integer"},
      texto: {type: "string"}, emoji: {type: "string"},
    }}}},
};
const AI_RETO_SYS = "Eres el tutor de matemáticas de Laura, una niña española de 7 años. Genera exactamente 6 ejercicios variados adaptados a su progreso (te lo dan en JSON). Refuerza lo que más falla y mezcla con lo que domina. REGLAS DURAS: tipo sub: resta con llevada, 10 <= b < a <= 999 (usa 3 cifras solo si ya practica restas de 3 cifras). tipo mul: a y b entre 2 y 10, SOLO de tablas que ya haya practicado. tipo miss: a entre 2 y 10 es el factor conocido, b entre 2 y 9 el que falta (se mostrará a × ? = a*b). tipo prob_mul: problema de grupos, a = número de grupos (2-6), b = elementos por grupo (2-6), texto = enunciado de máximo 90 caracteres que hable de a grupos de b cosas, emoji = UN solo emoji que represente la cosa. tipo prob_sub: problema de quitar, a total (hasta 999), b lo que se quita, texto máximo 90 caracteres, emoji UN emoji. En sub, mul y miss deja texto vacío y emoji vacío. Español de España, tono alegre, cosas que le gusten a una niña (animales, gatos, helados, flores, cromos). No repitas ejercicios.";

// ---- pistas personalizadas ----
const AI_PISTA_SCHEMA = {type: "object", additionalProperties: false, required: ["pista"],
                         properties: {pista: {type: "string"}}};
const AI_PISTA_SYS = "Eres un profesor muy cariñoso de una niña española de 7 años que acaba de fallar un ejercicio. Te dan en JSON el ejercicio y sus intentos fallidos. Escribe UNA pista de máximo 2 frases cortas: comenta su error concreto (ej: 'has puesto 5, pero...') y dale el truco del paso, SIN decir el resultado final. Español de España, tono dulce, tutéala. Nada técnico.";

// ---- mensaje del gato al final del día ----
const AI_MSG_SCHEMA = {type: "object", additionalProperties: false, required: ["mensaje"],
                       properties: {mensaje: {type: "string"}}};
const AI_MSG_SYS = "Eres el gato mascota de Laura (7 años) en su app de mates. Habla en primera persona como su gato. Te dan en JSON cómo le ha ido hoy, tu nombre (gato.nombre, úsalo si viene) y qué ropa llevas puesta. Escribe 1-2 frases dulces y juguetonas: celebra algo concreto de su sesión o bromea con tu accesorio. JAMÁS riñas ni menciones fallos. Español de España, puedes usar 1 emoji. Máximo 140 caracteres.";
