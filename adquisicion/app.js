/* Interfaz sin dependencias, servicios ni acceso a la red. */
'use strict';
const M=Acquisition,$=id=>document.getElementById(id);
let state=M.create(),selected='P01',sensorKey='T2M',jsonMode='preview',toastTimer;
const node=()=>state.nodes.find(n=>n.id===selected);
const escapeHTML=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=value=>Number(value).toLocaleString('es-BO',{maximumFractionDigits:3});
const badge=n=>{const s=M.status(n);return `<span class="status ${s.tone}">${s.label}</span>`;};
function toast(message){$('toast').textContent=message;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),4200);}
const miniTower=(x,y,central=false)=>`<g transform="translate(${x} ${y})"><ellipse cx="0" cy="7" rx="32" ry="10" fill="#405435" opacity=".12"/><path d="M-7 0 L0 -106 L7 0 M-5 -25 L5 -45 L-4 -65 L3 -85" fill="none" stroke="#747e69" stroke-width="3"/><path d="M0 -92 L27 -92 M0 -75 L-21 -75" stroke="#747e69" stroke-width="3"/><rect x="-13" y="-53" width="27" height="31" rx="3" fill="#e7e5d4" stroke="#89947a"/><rect x="-7" y="-47" width="15" height="13" rx="1" fill="#356951"/><circle cx="5" cy="-28" r="2" fill="#87bd6f"/><path d="M0 -105 L0 -128" stroke="#375b48" stroke-width="3"/><path d="M-11 -119 Q-20 -111 -11 -103 M11 -119 Q20 -111 11 -103" fill="none" stroke="#819771" stroke-width="1.3"/>${central?'<path d="M-32 -68 L-8 -78 L-8 -62 L-32 -52Z" fill="#46685a" stroke="#94a69a"/><path d="M-26 -69 L-26 -57 M-19 -72 L-19 -60 M-32 -61 L-8 -71" stroke="#95ac9e"/>':'<path d="M22 -92 L22 -108 M11 -108 L33 -108" stroke="#49634c" stroke-width="2"/><ellipse cx="10" cy="-108" rx="5" ry="3" fill="#526c4e"/><ellipse cx="35" cy="-108" rx="5" ry="3" fill="#526c4e"/><rect x="-27" y="-78" width="13" height="9" rx="2" fill="#faf9e9" stroke="#b2baa4"/><path d="M-29 -75 L-12 -75" stroke="#a6b19a"/><path d="M20 2 L20 -18 L32 -18 L32 2" fill="#a4b5a0"/><ellipse cx="26" cy="-18" rx="9" ry="3" fill="#e8edde"/>'}</g>`;
function crops(x,y,color){let out='';for(let row=0;row<4;row++)for(let col=0;col<9;col++){const a=x+col*16+row*10,b=y+row*15;out+=`<path d="M${a} ${b} v-9 m0 5 l-4 -4 m4 2 l4 -5" stroke="${color}" stroke-width="2" fill="none"/>`;}return out;}
function renderMap(){
  const count=state.nodes.length,cols=Math.min(3,count),rows=Math.ceil(count/cols),height=245+rows*210;
  const positions=state.nodes.map((n,i)=>[390+(i%cols-(cols-1)/2)*245,350+Math.floor(i/cols)*210]);
  $('map').innerHTML=`<svg viewBox="0 0 780 ${height}" role="group" aria-label="Campo ilustrativo con ${count} torres y una central"><defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".7" fill="#bac2a7" opacity=".3"/></pattern></defs><rect width="780" height="${height}" fill="url(#dots)"/><text x="30" y="30" fill="#6a795c" font-size="10" letter-spacing="2">ALTIPLANO / CAMPO EXPERIMENTAL</text><path d="M0 200 Q390 170 780 200" fill="none" stroke="#e9d8b2" stroke-width="22"/>
  ${positions.map(([x,y],i)=>`<path id="path-${state.nodes[i].id}" class="radio-path ${state.nodes[i].link?'':'off'}" d="M${x} ${y-100} Q${x} 165 390 65"/>`).join('')}
  <g role="button" tabindex="0" data-central="true" class="map-node" aria-label="Abrir estación central"><ellipse class="selection" cx="390" cy="125" rx="65" ry="34"/>${miniTower(390,150,true)}<rect x="315" y="157" width="150" height="28" rx="7" fill="#214d3d"/><text x="390" y="176" text-anchor="middle" fill="#fffef3" font-size="12">Central · dirección 0</text></g>
  ${positions.map(([x,y],i)=>{const n=state.nodes[i];return `<g class="map-node ${n.id===selected?'selected':''}" data-node="${n.id}" tabindex="0" role="button" aria-label="Seleccionar ${n.id}, dirección ${n.address}" aria-pressed="${n.id===selected}"><path d="M${x-100} ${y-20} L${x+20} ${y-52} L${x+104} ${y+16} L${x-20} ${y+48}Z" fill="${i%2?'#e4d2aa':'#d4dbb1'}" stroke="#bcc59a"/>${crops(x-65,y-10,'#81945c')}<ellipse class="selection" cx="${x}" cy="${y-30}" rx="105" ry="95"/>${miniTower(x,y)}<rect x="${x-76}" y="${y+30}" width="152" height="27" rx="6" fill="${n.id===selected?'#2d654d':'#fffdf1'}" stroke="#d1d7bd"/><text x="${x}" y="${y+48}" text-anchor="middle" fill="${n.id===selected?'#fffdf1':'#36533d'}" font-size="12" font-weight="600">${n.id} · Dir. ${n.address}</text><text x="${x}" y="${y+74}" text-anchor="middle" fill="#53644c" font-size="11">${escapeHTML(n.location.length>26?n.location.slice(0,23)+'…':n.location||'Ubicación sin asignar')}</text></g>`;}).join('')}</svg>`;
  $('map').querySelectorAll('[data-node]').forEach(el=>activate(el,()=>selectNode(el.dataset.node)));
  activate($('map').querySelector('[data-central]'),()=>setTab('central'));
}
function activate(el,fn){el.addEventListener('click',fn);el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fn();}});}
function pulse(id){const svg=$('map').querySelector('svg'),path=$('path-'+id);if(!path||!svg||matchMedia('(prefers-reduced-motion: reduce)').matches)return;const dot=document.createElementNS('http://www.w3.org/2000/svg','circle');dot.setAttribute('r','5');dot.setAttribute('class','packet');svg.append(dot);const start=performance.now(),len=path.getTotalLength();function frame(now){if(!dot.isConnected)return;const t=Math.min(1,(now-start)/1000),p=path.getPointAtLength(t*len);dot.setAttribute('cx',p.x);dot.setAttribute('cy',p.y);if(t<1)requestAnimationFrame(frame);else dot.remove();}requestAnimationFrame(frame);}
function detail(){
 const part=M.sensors.find(s=>s.key===sensorKey).part;
 const hot=(key,x,y,w,h,body)=>`<g class="sensor-hotspot ${M.sensors.find(s=>s.key===key).part===part?'selected':''}" data-sensor="${key}" tabindex="0" role="button" aria-label="Editar ${M.sensors.find(s=>s.key===key).label}"><rect class="hit" x="${x}" y="${y}" width="${w}" height="${h}" rx="8"/>${body}</g>`;
 $('tower-detail').innerHTML=`<svg viewBox="0 0 690 440" role="group" aria-label="Detalle de sensores en la torre y corte del suelo"><path d="M210 248 H475 V418 H210Z" fill="#e6d1ae"/><path d="M210 285 H475 V348 H210Z" fill="#d6bb92"/><path d="M210 348 H475 V418 H210Z" fill="#b99d79"/><path d="M210 248 H475" stroke="#8b9b5d" stroke-width="8"/><path d="M296 247 V60 M310 247 V60 M296 80 L310 110 L296 140 L310 170 L296 200 L310 230" stroke="#85917a" stroke-width="3" fill="none"/><path d="M303 68 V30" stroke="#3b6250" stroke-width="3"/><path d="M296 98 H240 M310 80 H375" stroke="#85917a" stroke-width="3"/>
 ${hot('LORA_RSSI',290,6,250,48,'<path d="M320 24 Q333 34 320 44 M286 24 Q273 34 286 44" fill="none" stroke="#91a27f" stroke-width="2"/><text x="346" y="30">Antena LoRa · 915 MHz</text><text x="346" y="46" style="font-size:9px">RSSI / SNR del enlace simulado</text>')}
 ${hot('WS2M',322,53,290,48,'<path d="M370 80 V60 M350 60 H390" stroke="#40644d" stroke-width="3"/><ellipse cx="348" cy="60" rx="8" ry="4" fill="#607b52"/><ellipse cx="393" cy="60" rx="8" ry="4" fill="#607b52"/><text x="421" y="70">Anemómetro · viento</text>')}
 ${hot('ALLSKY_SFC_SW_DWN',40,63,230,55,'<ellipse cx="239" cy="92" rx="15" ry="4" fill="#63856c"/><path d="M228 90 Q239 76 250 90" fill="#d3e4c7" stroke="#7f9873"/><text x="50" y="86">Radiación corta / larga</text><path d="M181 89 H215" stroke="#a4ad92"/>')}
 ${hot('T2M',37,120,256,55,'<rect x="270" y="128" width="19" height="30" rx="3" fill="#faf8e8" stroke="#a9b298"/><path d="M268 134 H291 M268 140 H291 M268 146 H291 M268 152 H291" stroke="#b2bba2"/><text x="50" y="141">Aire · 2 m</text><text x="50" y="157" style="font-size:9px">Temperatura, humedad y presión</text><path d="M210 141 H264" stroke="#a4ad92"/>')}
 ${hot('BAT_V',305,113,300,76,'<rect x="309" y="119" width="49" height="61" rx="6" fill="#e1e6d5" stroke="#84967a"/><rect x="317" y="128" width="31" height="25" rx="3" fill="#306d52"/><path d="M322 134 H342 M322 141 H335" stroke="#9bb68b"/><rect x="318" y="160" width="19" height="9" rx="2" fill="#9db679"/><text x="380" y="140">Pico 2W + radio LoRa</text><text x="380" y="158" style="font-size:9px">Caja de electrónica y batería</text>')}
 ${hot('T15CM',36,192,260,44,'<rect x="273" y="203" width="19" height="18" rx="3" fill="#faf8e8" stroke="#a9b298"/><path d="M270 209 H294 M270 215 H294" stroke="#b2bba2"/><text x="50" y="214">Aire · 15 cm</text><path d="M150 211 H267" stroke="#a4ad92"/>')}
 ${hot('PRECTOTCORR',365,194,275,53,'<path d="M384 241 V215 L379 209 H408 L403 215 V241Z" fill="#b2c4ac" stroke="#81977b"/><ellipse cx="394" cy="208" rx="15" ry="4" fill="#e8efdf" stroke="#81977b"/><text x="434" y="222">Pluviómetro</text>')}
 <path d="M303 248 V395" stroke="#4e6e50" stroke-width="2" fill="none"/>
 ${hot('VWC_5CM',240,253,420,30,'<path d="M303 264 H350" stroke="#547b60" stroke-width="5"/><circle cx="350" cy="264" r="5" fill="#edf1cf"/><path d="M358 264 H495" stroke="#9c926f" stroke-dasharray="3 3"/><text x="505" y="268">Humedad · 5 cm</text>')}
 ${hot('VWC_25CM',240,287,420,37,'<path d="M303 303 H350" stroke="#547b60" stroke-width="5"/><circle cx="350" cy="303" r="5" fill="#edf1cf"/><path d="M358 303 H495" stroke="#9c926f" stroke-dasharray="3 3"/><text x="505" y="307">Humedad · 25 cm</text>')}
 ${hot('TSOIL_25CM',36,287,204,37,'<text x="50" y="306">Temperatura · 25 cm</text><path d="M210 309 H266" stroke="#b17950" stroke-width="4"/>')}
 ${hot('EC_SOIL',36,329,250,37,'<text x="50" y="350">Conductividad (EC)</text><path d="M220 346 H276 M256 346 V358 M266 346 V358" stroke="#587153" stroke-width="3"/>')}
 ${hot('PH_SOIL',36,376,235,44,'<text x="50" y="392">pH · sensor propuesto</text><path d="M215 393 H266" stroke="#98713f" stroke-width="3" stroke-dasharray="4 4"/>')}
 ${hot('VWC_100CM',280,373,380,42,'<path d="M303 394 H350" stroke="#547b60" stroke-width="5"/><circle cx="350" cy="394" r="5" fill="#edf1cf"/><path d="M358 394 H495" stroke="#9c926f" stroke-dasharray="3 3"/><text x="505" y="398">Humedad · 100 cm</text>')}
 </svg>`;
 $('tower-detail').querySelectorAll('[data-sensor]').forEach(el=>activate(el,()=>{sensorKey=el.dataset.sensor;renderEditor();detail();$('sensor-select').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});}));
}
function renderEditor(){$('send').disabled=false;const n=node(),s=M.sensors.find(s=>s.key===sensorKey);$('node-title').textContent=`Parcela ${n.id}`;$('station-zone').value=n.zona_id||'';$('station-address').value=n.address;$('station-location').value=n.location;$('station-point').value=n.point?n.point.lat+', '+n.point.lon:'';updateMapsLink();$('identity-error').textContent='';$('identity-caption').textContent=`IP simulada ${M.identity(n).simulated_ipv4} · ${M.identity(n).hostname} · Dir. ${n.address} · ${n.location||'Ubicación sin asignar'}`;$('node-status').outerHTML=badge(n).replace('class="status','id="node-status" class="status');$('sensor-select').value=s.key;$('sensor-info').textContent=s.key==='PH_SOIL'?'Extensión propuesta: este sensor no está presente en el firmware de Nefi.':s.key.startsWith('LORA_')?'Calidad de recepción simulada en la central.':'Escenario editable. El firmware original agrega datos por día; aquí se ilustra su formato.';for(const id of ['sensor-value','sensor-range']){const input=$(id);input.min=s.min;input.max=s.max;input.step=s.step;input.value=n.values[s.key];}$('sensor-unit').textContent=s.unit;$('range-min').textContent=fmt(s.min);$('range-max').textContent=fmt(s.max);$('link-enabled').checked=n.link;$('edit-error').textContent='';$('receipt-note').textContent=n.last===null?'La central aún no recibió datos de este nodo.':`Última recepción válida: ${M.time(n.last)} · ${Math.floor((state.now-n.last)/60000)} min atrás. Editar no transmite.`;}
function renderCards(){$('node-cards').innerHTML=state.nodes.map(n=>`<button class="node-card ${n.id===selected?'selected':''}" data-card="${n.id}" aria-pressed="${n.id===selected}"><span class="card-heading">Parcela ${n.id}${badge(n)}</span><div class="readings"><div><small>AIRE</small><strong>${fmt(n.values.T2M)}</strong> <em>°C</em></div><div><small>SUELO · 25 CM</small><strong>${fmt(n.values.VWC_25CM*100)}</strong> <em>% vol.</em></div><div><small>pH · PROPUESTO</small><strong>${fmt(n.values.PH_SOIL)}</strong></div><div><small>BATERÍA</small><strong>${fmt(n.values.BAT_V)}</strong> <em>V</em></div><div><small>RSSI</small><strong>${fmt(n.values.LORA_RSSI)}</strong> <em>dBm</em></div><div><small>SNR</small><strong>${fmt(n.values.LORA_SNR)}</strong> <em>dB</em></div></div><div class="card-bottom">Dir. ${n.address} · ${escapeHTML(n.location||'Ubicación sin asignar')}<br>${M.identity(n).hostname} · IP simulada ${M.identity(n).simulated_ipv4}<br>Valores locales simulados · ${n.link?'enlace disponible':'enlace interrumpido'}</div></button>`).join('');$('node-cards').querySelectorAll('[data-card]').forEach(el=>el.onclick=()=>selectNode(el.dataset.card));}
function renderJSON(){const n=node(),p=jsonMode==='preview'?M.packet(state,n):n.received;$('json-node').innerHTML=state.nodes.map(n=>`<option value="${n.id}">${n.id} · ${n.address}</option>`).join('');$('json-node').value=selected;$('json-output').textContent=p?JSON.stringify(p,null,2):'Sin paquete recibido. Envía un paquete simulado desde Campo.';$('json-caption').textContent=jsonMode==='preview'?`${selected} · Vista previa local: cambia al editar. La central solo se actualiza al transmitir.`:`${selected} · Último paquete válido recibido${n.last===null?'':` a las ${M.time(n.last)}`}. Se conserva aunque el enlace falle.`;$('preview-mode').setAttribute('aria-pressed',jsonMode==='preview');$('received-mode').setAttribute('aria-pressed',jsonMode==='received');$('download').disabled=!p;}
function renderCentral(){const active=state.nodes.reduce((a,n)=>a+n.active.length,0);$('active-count').textContent=active;$('alert-count').textContent=active;$('online-count').textContent=`${state.nodes.filter(n=>n.last!==null&&state.now-n.last<=900000).length} / ${state.nodes.length}`;$('receipts').innerHTML=state.nodes.map(n=>{const p=n.received,d=p?.header.start;return `<tr><td><strong>${n.id} · Dir. ${n.address}</strong><small>${M.identity(n).hostname} · ${M.identity(n).simulated_ipv4}</small><small>${escapeHTML(n.location||'Ubicación sin asignar')}</small></td><td>${n.last===null?'Sin recepción':M.time(n.last)}<small>${n.last===null?'Envía un paquete para comenzar':'Reloj simulado · '+new Date(n.last).toISOString().slice(0,10)}</small></td><td>${n.last===null?'—':Math.floor((state.now-n.last)/60000)+' min'}</td><td>${p?`${fmt(p.properties.parameter.LORA_RSSI[d])} dBm / ${fmt(p.properties.parameter.LORA_SNR[d])} dB`:'—'}</td><td>${badge(n)}<small>${n.active.map(escapeHTML).join(' · ')||'Sin condiciones activas'}</small></td></tr>`;}).join('');$('events').innerHTML=state.events.length?state.events.map(e=>`<div class="event ${e.resolved?'resolved':''}"><small>${M.time(e.time)}</small><span>${e.resolved?'RESUELTO':'ALERTA'} · ${e.node}</span>${escapeHTML(e.text)}</div>`).join(''):'<p class="muted">Sin eventos registrados.</p>';}
function render(){M.reconcile(state);$('tower-count').value=state.nodes.length;$('add-tower').disabled=state.nodes.length>=12;$('remove-tower').disabled=state.nodes.length<=1;$('remove-tower').textContent='Quitar '+selected;$('clock').textContent=M.time(state.now);$('clock').nextElementSibling.textContent=new Date(state.now).toISOString().slice(0,10)+' · reloj detenido entre avances';renderMap();renderEditor();renderCards();renderCentral();renderJSON();detail();}
function selectNode(id){selected=id;render();}
function setTab(tab){$('field-view').hidden=tab!=='field';$('central-view').hidden=tab!=='central';document.querySelectorAll('[data-tab]').forEach(el=>{el.classList.toggle('active',el.dataset.tab===tab);el.setAttribute('aria-pressed',el.dataset.tab===tab);});}
function sendNodes(nodes){let successes=0;const errors=[];nodes.forEach(n=>{const r=M.receive(state,n,M.packet(state,n));if(r.ok)successes++;else errors.push(`${n.id}: ${r.error}`);});render();nodes.filter(n=>n.link&&!n.invalid).forEach(n=>pulse(n.id));toast(errors.length?errors.join(' · '):`${successes} paquete${successes===1?'':'s'} recibido${successes===1?'':'s'} por la central.`);}
$('sensor-select').innerHTML=M.sensors.map(s=>`<option value="${s.key}">${s.label}</option>`).join('');
$('sensor-select').onchange=e=>{sensorKey=e.target.value;renderEditor();detail();};
for(const id of ['sensor-value','sensor-range'])$(id).oninput=e=>{const s=M.sensors.find(s=>s.key===sensorKey),value=e.target.valueAsNumber;if(!Number.isFinite(value)||value<s.min||value>s.max){$('edit-error').textContent=`Introduce un valor entre ${s.min} y ${s.max}.`;$('send').disabled=true;return;}$('send').disabled=false;$('edit-error').textContent='';node().values[s.key]=value;$(id==='sensor-value'?'sensor-range':'sensor-value').value=value;renderCards();renderJSON();};
$('link-enabled').onchange=e=>{node().link=e.target.checked;render();};
$('send').onclick=()=>sendNodes([node()]);$('send-all').onclick=$('central-send').onclick=()=>sendNodes(state.nodes);
document.querySelectorAll('[data-advance]').forEach(el=>el.onclick=()=>{state.now+=Number(el.dataset.advance)*60000;render();toast(`Reloj avanzado ${el.dataset.advance} min. No se transmiten datos automáticamente.`);});
$('reset').onclick=()=>{state=M.create();selected='P01';sensorKey='T2M';jsonMode='preview';$('raw-result').textContent='';$('raw-json').value='{"type": "Feature", "properties":';renderThresholds();render();toast('Demostración restablecida. No hay datos recibidos.');};
document.querySelectorAll('[data-tab]').forEach(el=>el.onclick=()=>setTab(el.dataset.tab));
$('json-node').onchange=e=>selectNode(e.target.value);
$('preview-mode').onclick=()=>{jsonMode='preview';renderJSON();};$('received-mode').onclick=()=>{jsonMode='received';renderJSON();};
$('invalid-send').onclick=()=>{const r=M.receive(state,node(),$('raw-json').value);$('raw-result').textContent=r.ok?'Paquete válido recibido.':`Rechazado: ${r.error} Se conserva el último paquete válido.`;render();if(r.ok)pulse(selected);};
$('download').onclick=()=>{const p=jsonMode==='preview'?M.packet(state,node()):node().received;if(!p)return;const url=URL.createObjectURL(new Blob([JSON.stringify(p,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=`SIMULACION_${selected}_${jsonMode}_${M.day(state.now)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
function renderThresholds(){$('thresholds').innerHTML=M.rules.map(r=>`<label class="threshold"><span>${r.label}</span><span><input data-rule="${r.key}" type="number" min="${r.min}" max="${r.max}" step="${r.step}" value="${state.thresholds[r.key]}" aria-label="${r.label}"><small>${r.unit}</small></span></label>`).join('');$('thresholds').querySelectorAll('input').forEach(el=>el.onchange=()=>{const r=M.rules.find(r=>r.key===el.dataset.rule),v=el.valueAsNumber;if(!Number.isFinite(v)||v<r.min||v>r.max||(r.key==='phLow'&&v>=state.thresholds.phHigh)||(r.key==='phHigh'&&v<=state.thresholds.phLow)){el.value=state.thresholds[r.key];toast('Umbral fuera de rango o límites de pH invertidos.');return;}state.thresholds[r.key]=v;M.reconcile(state);renderCentral();renderCards();renderEditor();});}
$('tower-count').innerHTML=Array.from({length:12},(_,i)=>`<option value="${i+1}">${i+1} torre${i?'s':''}</option>`).join('');
$('tower-count').onchange=e=>{M.resize(state,Number(e.target.value));if(!state.nodes.some(n=>n.id===selected))selected=state.nodes[0].id;render();};
function readPoint(){
  const p=M.parsePoint($('station-point').value);
  const previous=node().point;
  return previous&&p&&previous.lat===p.lat&&previous.lon===p.lon?previous:p;
}
function updateMapsLink(){
  const query=$('station-location').value.trim()||'Altiplano, Bolivia';
  let point;
  try{point=M.parsePoint($('station-point').value);}catch{}
  $('maps-open').href='https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(point?point.lat+','+point.lon:query);
}
$('station-location').oninput=$('station-point').oninput=updateMapsLink;
$('add-tower').onclick=()=>{const n=M.addTower(state);selectNode(n.id);toast('Torre activa: '+n.id);};
$('remove-tower').onclick=()=>{const n=node();M.removeTower(state,n);selectNode(state.nodes[0].id);toast(n.id+' retirada. Añadir torre permite recuperarla.');};
$('save-identity').onclick=()=>{try{M.identify(state,node(),$('station-address').valueAsNumber,$('station-location').value, readPoint());node().zona_id=$('station-zone').value||null;render();toast('Identificación guardada. Los paquetes anteriores conservan su dirección original.');}catch(e){$('identity-error').textContent=e.message;}};
$('download-network').onclick=()=>{const bundle=M.collection(state),url=URL.createObjectURL(new Blob([JSON.stringify(bundle,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download=`SIMULACION_RED_${state.nodes.length}_TORRES_${M.day(state.now)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);toast(`JSON preparado con ${state.nodes.length} torres y sus direcciones.`);};
renderThresholds();render();

// Integración opcional. El mismo archivo sigue funcionando al abrir el HTML local.
if (window.parent !== window) {
  let clave = '', region = '';
  const enviar = (type, campos={}) => window.parent.postMessage({isStreamlitMessage:true,type,...campos}, '*');
  let alturaEnviada=0;
  function ajustarAltura(){
    // Medir el contenido, no el viewport del iframe: la pestaña también puede encogerse.
    const altura=Math.ceil(document.body.getBoundingClientRect().height);
    if(altura>0 && altura!==alturaEnviada){
      alturaEnviada=altura;
      enviar('streamlit:setFrameHeight',{height:altura});
    }
  }
  const recordar = () => {
    if (clave) {
      try {sessionStorage.setItem(clave, JSON.stringify(state));} catch {}
    }
  };
  function publicar() {
    recordar();
    enviar('streamlit:setComponentValue',{dataType:'json',value:{token:crypto.randomUUID(),red:M.collection(state)}});
    document.getElementById('confirmacion-astra').textContent='Enviando red a ASTRA…';
  }
  window.addEventListener('message', e => {
    if (e.source !== window.parent || e.data?.type !== 'streamlit:render') return;
    const {zona,nombre,sesion}=e.data.args;
    if (!clave) {
      clave='astra-adquisicion-'+sesion;
      let guardado;
      try {guardado=JSON.parse(sessionStorage.getItem(clave));} catch {}
      if(guardado) state=guardado;
      else {
        state.nodes[0].zona_id='patacamaya_01';
        state.nodes[1].zona_id='viacha_01';
        state.nodes.slice(0,2).forEach((n,i)=>{n.location='Parcela ilustrativa '+(i+1);M.receive(state,n,M.packet(state,n));});
      }
      document.body.classList.add('integrado');
      new ResizeObserver(ajustarAltura).observe(document.body);
      const boton=document.createElement('button');
      boton.id='aplicar-astra';boton.textContent='Aplicar red a ASTRA';
      boton.onclick=publicar;
      document.querySelector('.topbar').append(boton);
      const confirmacion=document.createElement('div');
      confirmacion.id='confirmacion-astra';
      confirmacion.setAttribute('role','status');
      confirmacion.style.cssText='padding:14px 22px;background:#e6efdf;color:#173f34;border-bottom:1px solid #b8c8ad;font-size:15px;line-height:1.5;';
      document.querySelector('.topbar').after(confirmacion);
      document.querySelector('.brand').removeAttribute('href');
      document.querySelector('.intro h1').textContent='Laboratorio de adquisición';
      document.querySelector('.intro .eyebrow').textContent='ESTACIÓN DE SUELO';
      document.querySelector('.intro p').textContent='Explora las torres de la red, transmite sus lecturas y pulsa «Aplicar red a ASTRA» para actualizar la ficha regional.';
      document.addEventListener('input', recordar);
      document.addEventListener('change', recordar);
      document.addEventListener('click', recordar);
      renderThresholds();
    }
    if(region!==zona) {
      region=zona;
      const local=state.nodes.find(n=>n.zona_id===zona);
      selected=(local||state.nodes[0]).id;
      document.querySelector('.intro .eyebrow').textContent='ESTACIÓN DE SUELO · '+nombre+(local?'':' · Sin torres locales');
      render();
    }
    document.getElementById('confirmacion-astra').textContent=e.data.args.confirmacion || 'Para registrar una toma: transmite la torre y pulsa Aplicar red a ASTRA. Para otra toma, avanza +15 min y transmite de nuevo.';
    ajustarAltura();
  });
  enviar('streamlit:componentReady',{apiVersion:1});
}
