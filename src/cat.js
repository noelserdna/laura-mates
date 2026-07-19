// ================= GATO NEGRO PERSONALIZABLE (SVG por capas) =================
// Devuelve un string SVG. st = {skin, eye, head, eyes, neck}
const EYE_C = {verde:"#3ad07a", ambar:"#ffb02e", azul:"#4bb8ff", rosa:"#ff77c8", lila:"#b98cff"};

function skinCfg(skin){
  // base = color del pelaje; ear = oreja interna; extras dibujados aparte
  const c = {
    clasico:  {base:"#20202c", ear:"#ff9ec4", cheek:null},
    esmoquin: {base:"#20202c", ear:"#ff9ec4", cheek:null},
    corazon:  {base:"#20202c", ear:"#ff9ec4", cheek:"#ff9ec4"},
    rayado:   {base:"#22222f", ear:"#ff9ec4", cheek:null},
    vaca:     {base:"#20202c", ear:"#ff9ec4", cheek:null},
    galaxia:  {base:"#251a44", ear:"#b98cff", cheek:null},
  };
  return c[skin] || c.clasico;
}

function skinMarks(skin){
  // marcas sobre cuerpo/cabeza segun skin
  if(skin==="esmoquin"){
    return `<path d="M100 150 L84 215 Q100 224 116 215 Z" fill="#fff"/>
      <ellipse cx="76" cy="222" rx="12" ry="8" fill="#fff"/>
      <ellipse cx="124" cy="222" rx="12" ry="8" fill="#fff"/>
      <path d="M100 108 q13 6 0 20 q-13 -14 0 -20" fill="#fff"/>`;
  }
  if(skin==="corazon"){
    return `<path d="M100 168 c-10 -14 -30 -4 -20 10 c4 8 20 18 20 18 c0 0 16 -10 20 -18 c10 -14 -10 -24 -20 -10 z" fill="#ff7ab0"/>`;
  }
  if(skin==="rayado"){
    return `<g stroke="#3a3a4d" stroke-width="4" stroke-linecap="round" fill="none">
      <path d="M70 60 q6 8 0 16"/><path d="M100 54 q0 9 0 16"/><path d="M130 60 q-6 8 0 16"/>
      <path d="M80 168 q6 9 0 18"/><path d="M100 172 q0 9 0 18"/><path d="M120 168 q-6 9 0 18"/></g>`;
  }
  if(skin==="vaca"){
    return `<path d="M64 92 q-14 12 2 26 q18 4 16 -14 q-2 -16 -18 -12z" fill="#fff"/>
      <ellipse cx="120" cy="180" rx="20" ry="15" fill="#fff"/>
      <ellipse cx="80" cy="205" rx="12" ry="9" fill="#fff"/>`;
  }
  if(skin==="galaxia"){
    let s="";
    const pts=[[70,70],[128,66],[110,100],[80,120],[132,130],[92,168],[124,182],[68,150]];
    pts.forEach(p=>{ s+=`<g transform="translate(${p[0]},${p[1]})"><path d="M0 -4 L1 -1 L4 0 L1 1 L0 4 L-1 1 L-4 0 L-1 -1 Z" fill="#fff"/></g>`; });
    return s;
  }
  return "";
}

// ---- accesorios ----
function accHead(id){
  if(!id) return "";
  if(id==="lazo") return `<g><path d="M100 40 L72 24 Q66 40 72 56 Z" fill="#ff6fae"/><path d="M100 40 L128 24 Q134 40 128 56 Z" fill="#ff6fae"/><circle cx="100" cy="40" r="9" fill="#ff3f92"/></g>`;
  if(id==="fiesta") return `<g><path d="M100 2 L82 46 L118 46 Z" fill="#4dc9e6"/><path d="M100 2 L90 46 M100 2 L110 46" stroke="#fff" stroke-width="3"/><circle cx="100" cy="2" r="6" fill="#ffcc33"/></g>`;
  if(id==="flor") return `<g transform="translate(100,38)">${[0,72,144,216,288].map(a=>`<circle cx="${(13*Math.cos(a*Math.PI/180)).toFixed(1)}" cy="${(13*Math.sin(a*Math.PI/180)).toFixed(1)}" r="9" fill="#ff8fc8"/>`).join("")}<circle r="7" fill="#ffd84d"/></g>`;
  if(id==="gorro") return `<g><path d="M60 44 Q100 6 140 44 Z" fill="#7b5cff"/><rect x="58" y="40" width="84" height="12" rx="6" fill="#5a3fd6"/><circle cx="100" cy="10" r="9" fill="#fff"/></g>`;
  if(id==="mago") return `<g><path d="M100 -6 L74 46 L126 46 Z" fill="#5a3fd6"/><rect x="66" y="44" width="68" height="9" rx="4" fill="#3d2a9e"/><path d="M96 20 l3 5 5 1 -4 4 1 5 -5 -3 -5 3 1 -5 -4 -4 5 -1z" fill="#ffcc33"/></g>`;
  if(id==="corona") return `<g><path d="M66 46 L70 20 L86 38 L100 14 L114 38 L130 20 L134 46 Z" fill="#ffcf3f" stroke="#e0a800" stroke-width="2"/><circle cx="100" cy="30" r="4" fill="#ff5b7f"/><circle cx="78" cy="34" r="3" fill="#4bb8ff"/><circle cx="122" cy="34" r="3" fill="#4bb8ff"/></g>`;
  return "";
}
function accEyes(id){
  if(!id) return "";
  if(id==="gafas") return `<g fill="none" stroke="#2a2350" stroke-width="4"><circle cx="76" cy="94" r="17"/><circle cx="124" cy="94" r="17"/><path d="M93 94 h14"/><path d="M59 92 l-10 -6 M141 92 l10 -6"/></g>`;
  if(id==="gafas_sol") return `<g><rect x="58" y="80" width="36" height="26" rx="12" fill="#1a1a22"/><rect x="106" y="80" width="36" height="26" rx="12" fill="#1a1a22"/><path d="M94 88 h12" stroke="#1a1a22" stroke-width="5"/><path d="M58 84 l-9 -6 M142 84 l9 -6" stroke="#1a1a22" stroke-width="4"/></g>`;
  if(id==="antifaz") return `<g><path d="M50 88 Q100 74 150 88 Q150 108 128 110 Q112 100 100 100 Q88 100 72 110 Q50 108 50 88 Z" fill="#ff5b7f"/><ellipse cx="76" cy="94" rx="9" ry="7" fill="#fff"/><ellipse cx="124" cy="94" rx="9" ry="7" fill="#fff"/></g>`;
  return "";
}
function accNeck(id){
  if(!id) return "";
  if(id==="cascabel") return `<g><path d="M62 150 Q100 168 138 150" stroke="#e0322f" stroke-width="9" fill="none"/><circle cx="100" cy="162" r="10" fill="#ffcf3f" stroke="#e0a800" stroke-width="2"/><circle cx="100" cy="164" r="2.5" fill="#8a6a00"/></g>`;
  if(id==="pajarita") return `<g><path d="M100 152 L80 142 Q76 152 80 162 Z" fill="#ff5b7f"/><path d="M100 152 L120 142 Q124 152 120 162 Z" fill="#ff5b7f"/><rect x="95" y="147" width="10" height="12" rx="3" fill="#d63a63"/></g>`;
  if(id==="bandana") return `<g><path d="M66 146 Q100 156 134 146 L118 176 Q100 184 82 176 Z" fill="#4dc9e6"/><g fill="#fff"><circle cx="90" cy="158" r="2.5"/><circle cx="110" cy="158" r="2.5"/><circle cx="100" cy="168" r="2.5"/></g></g>`;
  if(id==="bufanda") return `<g><path d="M60 148 Q100 166 140 148 Q142 160 132 166 Q100 178 68 166 Q58 160 60 148 Z" fill="#ff9d2e"/><path d="M120 164 l14 34 -16 -4 -6 -26 Z" fill="#ff8a00"/></g>`;
  return "";
}

function catSVG(st){
  st = st||{};
  const skin = st.skin||"clasico";
  const cf = skinCfg(skin);
  const iris = EYE_C[st.eye||"verde"];
  const base = cf.base, out = "#454560";
  const cheek = cf.cheek;
  return `<svg viewBox="0 0 200 235" class="cat">
    <!-- cola -->
    <path d="M150 196 C196 186 190 120 156 130 C182 140 176 176 150 180 Z" fill="${base}" stroke="${out}" stroke-width="2"/>
    <!-- cuerpo -->
    <ellipse cx="100" cy="184" rx="54" ry="48" fill="${base}" stroke="${out}" stroke-width="2"/>
    <ellipse cx="80" cy="220" rx="15" ry="10" fill="${base}" stroke="${out}" stroke-width="2"/>
    <ellipse cx="120" cy="220" rx="15" ry="10" fill="${base}" stroke="${out}" stroke-width="2"/>
    <!-- orejas -->
    <path d="M56 62 L44 14 L94 46 Z" fill="${base}" stroke="${out}" stroke-width="2"/>
    <path d="M144 62 L156 14 L106 46 Z" fill="${base}" stroke="${out}" stroke-width="2"/>
    <path d="M62 52 L56 26 L84 44 Z" fill="${cf.ear}"/>
    <path d="M138 52 L144 26 L116 44 Z" fill="${cf.ear}"/>
    <!-- cabeza -->
    <ellipse cx="100" cy="94" rx="60" ry="55" fill="${base}" stroke="${out}" stroke-width="2"/>
    <!-- marcas de pelaje -->
    ${skinMarks(skin)}
    <!-- mejillas -->
    ${cheek?`<circle cx="62" cy="112" r="9" fill="${cheek}" opacity=".8"/><circle cx="138" cy="112" r="9" fill="${cheek}" opacity=".8"/>`:""}
    <!-- ojos -->
    <g>
      <ellipse cx="76" cy="94" rx="15" ry="19" fill="${iris}"/>
      <ellipse cx="124" cy="94" rx="15" ry="19" fill="${iris}"/>
      <ellipse cx="76" cy="96" rx="7" ry="12" fill="#161620"/>
      <ellipse cx="124" cy="96" rx="7" ry="12" fill="#161620"/>
      <circle cx="72" cy="88" r="4" fill="#fff"/>
      <circle cx="120" cy="88" r="4" fill="#fff"/>
    </g>
    <!-- nariz y boca -->
    <path d="M94 114 L106 114 L100 121 Z" fill="#ff7ab0"/>
    <path d="M100 121 q-8 9 -16 4 M100 121 q8 9 16 4" fill="none" stroke="#3a3a4d" stroke-width="2.5" stroke-linecap="round"/>
    <!-- bigotes -->
    <g stroke="#5a5a70" stroke-width="2" stroke-linecap="round">
      <path d="M60 112 L26 104 M60 118 L26 120 M60 124 L28 134"/>
      <path d="M140 112 L174 104 M140 118 L174 120 M140 124 L172 134"/>
    </g>
    <!-- accesorios -->
    ${accNeck(st.neck)}
    ${accEyes(st.eyes)}
    ${accHead(st.head)}
  </svg>`;
}
