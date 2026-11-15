/* Modelo local independiente de la interfaz y del firmware físico. */
(function (root) {
  'use strict';
  const sensors = [
    ['T2M','Temperatura del aire · 2 m','°C',-25,45,.1,9.4,'air'],
    ['RH2M','Humedad del aire · 2 m','%',0,100,.1,58.3,'air'],
    ['T15CM','Temperatura del aire · 15 cm','°C',-25,50,.1,9.1,'low'],
    ['RH15CM','Humedad del aire · 15 cm','%',0,100,.1,63,'low'],
    ['VWC_5CM','Humedad del suelo · 5 cm','m³/m³',0,.6,.001,.138,'soil5'],
    ['VWC_25CM','Humedad del suelo · 25 cm','m³/m³',0,.6,.001,.196,'soil25'],
    ['VWC_100CM','Humedad del suelo · 100 cm','m³/m³',0,.6,.001,.254,'soil100'],
    ['TSOIL_25CM','Temperatura del suelo · 25 cm','°C',-15,45,.1,12.6,'soil25'],
    ['EC_SOIL','Conductividad del suelo','dS/m',0,10,.01,1.35,'ec'],
    ['PH_SOIL','pH del suelo · sensor propuesto','pH',0,14,.1,6.7,'ph'],
    ['PRECTOTCORR','Lluvia diaria acumulada','mm/day',0,150,.1,2.4,'rain'],
    ['WS2M','Velocidad del viento','m/s',0,35,.1,2.4,'wind'],
    ['WS2M_MAX','Ráfaga máxima','m/s',0,60,.1,6.9,'wind'],
    ['ALLSKY_SFC_SW_DWN','Radiación de onda corta','W/m²',0,1400,1,318.7,'sun'],
    ['ALLSKY_SFC_LW_DWN','Radiación de onda larga','W/m²',0,800,1,247.9,'sun'],
    ['PS','Presión atmosférica','kPa',40,110,.01,62.28,'air'],
    ['T2M_MIN','Temperatura mínima diaria','°C',-30,45,.1,1.2,'air'],
    ['T2M_MAX','Temperatura máxima diaria','°C',-25,55,.1,17.8,'air'],
    ['BAT_V','Voltaje de batería','V',2,4.5,.01,3.76,'box'],
    ['LORA_RSSI','Intensidad de señal recibida','dBm',-140,-30,1,-84,'antenna'],
    ['LORA_SNR','Relación señal / ruido','dB',-20,15,.1,7.5,'antenna']
  ].map(([key,label,unit,min,max,step,value,part])=>({key,label,unit,min,max,step,value,part}));
  const rules = [
    {key:'battery',label:'Batería baja por debajo de',unit:'V',min:2,max:4.5,step:.01,value:3.3},
    {key:'rssi',label:'Señal débil por debajo de',unit:'dBm',min:-140,max:-30,step:1,value:-110},
    {key:'snr',label:'SNR bajo por debajo de',unit:'dB',min:-20,max:15,step:.1,value:0},
    {key:'soil',label:'Humedad a 25 cm por debajo de',unit:'m³/m³',min:0,max:.6,step:.001,value:.12},
    {key:'cold',label:'Temperatura del aire por debajo de',unit:'°C',min:-25,max:45,step:.1,value:0},
    {key:'phLow',label:'pH propuesto por debajo de',unit:'pH',min:0,max:14,step:.1,value:5.5},
    {key:'phHigh',label:'pH propuesto por encima de',unit:'pH',min:0,max:14,step:.1,value:8}
  ];
  const start = Date.UTC(2026,10,14,10,0,0); // reloj civil ficticio LST, sin conversión de zona
  const day = now => new Date(now).toISOString().slice(0,10).replaceAll('-','');
  const time = now => new Date(now).toISOString().slice(11,19);
  function create() {
    const state={now:start,thresholds:Object.fromEntries(rules.map(r=>[r.key,r.value])),events:[],nodes:[]};
    state.nodes=['P01','P02','P03'].map((id,i)=>({id,values:Object.fromEntries(sensors.map(s=>[s.key,s.value])),link:true,received:null,last:null,invalid:false,active:[]}));
    state.nodes[1].values.T2M=11.2;state.nodes[1].values.VWC_25CM=.224;
    state.nodes[2].values.T2M=8.6;state.nodes[2].values.LORA_RSSI=-96;
    state.nodes.forEach((n,i)=>{n.address=i+1;n.location='';});
    state.inactive=[];
    reconcile(state); return state;
  }
  function resize(state,count) {
    if(!Number.isInteger(count)||count<1||count>12)throw Error('Selecciona entre 1 y 12 torres de parcela.');
    while(state.nodes.length<count)addTower(state);
    while(state.nodes.length>count)removeTower(state,state.nodes.at(-1));
  }
  function addTower(state) {
    if(state.nodes.length>=12)throw Error('Máximo de 12 torres.');
    let tower=state.inactive.pop();
    if(!tower){
      const index=state.nodes.length+1;
      let address=index;
      while(state.nodes.some(n=>n.address===address))address++;
      tower={id:'P'+String(index).padStart(2,'0'),address,location:'',values:Object.fromEntries(sensors.map(s=>[s.key,s.value])),link:true,received:null,last:null,invalid:false,active:[]};
    }
    state.nodes.push(tower);
    reconcile(state);
    return tower;
  }
  function removeTower(state,tower) {
    if(state.nodes.length<=1||!state.nodes.includes(tower))throw Error('Debe quedar al menos una torre.');
    state.nodes.splice(state.nodes.indexOf(tower),1);
    state.inactive.push(tower);
    reconcile(state);
  }
  function identity(n) {
    const slug=n.location.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,48).replace(/^-+|-+$/g,'')||'parcela';
    return {zona_id:n.zona_id||null,hostname:slug+'-'+n.id.toLowerCase()+'.test',simulated_ipv4:'10.42.'+Math.floor(n.address/256)+'.'+(n.address%256),location_source:n.point?.source||null};
  }
  function parsePoint(input) {
    input=input.trim();
    if(!input)return null;
    let pair=input,source='coordenadas introducidas';
    if(/^https?:/i.test(input)){
      const u=new URL(input);
      if(u.hostname==='maps.app.goo.gl'||u.hostname==='goo.gl')throw Error('Abre el enlace corto en Maps y copia las coordenadas del marcador o su enlace completo.');
      if(!/^(?:(?:www|maps)\.)?google\.(?:com(?:\.bo)?|es|bo)$/.test(u.hostname))throw Error('Usa un enlace de Google Maps o latitud, longitud.');
      const place=decodeURIComponent(u.pathname).match(/!3d(-?[\d.]+)!4d(-?[\d.]+)/);
      pair=place?place.slice(1).join(','):u.searchParams.get('query')||u.searchParams.get('q')||decodeURIComponent(u.pathname).match(/\/place\/([^/]+)/)?.[1]||'';
      source='enlace Google Maps';
    }
    const match=pair.match(/^\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*,\s*([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*$/);
    if(!match)throw Error('Copia las coordenadas del marcador en Google Maps como latitud, longitud.');
    const [lat,lon]=match.slice(1).map(Number);
    if(Math.abs(lat)>90||Math.abs(lon)>180)throw Error('Coordenadas fuera de rango.');
    return {lat,lon,source};
  }
  function identify(state,node,address,location,point=node.point) {
    if(!Number.isInteger(address)||address<1||address>65535)throw Error('La dirección debe ser un entero entre 1 y 65535; 0 se reserva para la central.');
    if([...state.nodes,...state.inactive].some(n=>n!==node&&n.address===address))throw Error('Esa dirección ya pertenece a otra torre, incluso si está inactiva.');
    location=String(location).trim();if(location.length>80)throw Error('La ubicación admite hasta 80 caracteres.');
    node.address=address;node.location=location;node.point=point;
  }
  function collection(state) {
    return {schema:'farmastra.adquisicion/1.1',source:'SIMULACION',exported_at_simulated:new Date(state.now).toISOString().slice(0,19),time_standard:'LST',central:{id:'CENTRAL',address:0,connection:'SIMULADA'},station_count:state.nodes.length,thresholds:{...state.thresholds},stations:state.nodes.map(n=>({id:n.id,configured_address:n.address,...identity(n),location:n.location||null,status:status(n).label,conditions:[...n.active],link_available:n.link,last_received_at_simulated:n.last===null?null:new Date(n.last).toISOString().slice(0,19),age_minutes:n.last===null?null:(state.now-n.last)/60000,local_preview:packet(state,n),last_valid_received:n.received?JSON.parse(JSON.stringify(n.received)):null})),notes:['Solo torres activas. No es historial de todas las transmisiones.','local_preview contiene valores editados; last_valid_received conserva solo la última recepción válida.','Direcciones lógicas del simulador; no configuran el firmware ni una dirección IP.','Si cambia la dirección, el paquete recibido mantiene la dirección original hasta un nuevo envío.']};
  }
  function packet(state,node) {
    const date=day(state.now), parameter={},parameters={};
    sensors.forEach(s=>{parameter[s.key]={[date]:node.values[s.key]};parameters[s.key]={units:s.unit.replace('°C','C').replace('m³/m³','m3/m3').replace('W/m²','W/m2'),longname:s.label};});
    const round=n=>Math.round(n*1000)/1000;
    parameter.GWETTOP={[date]:round(Math.min(1,node.values.VWC_5CM/.45))};
    parameter.GWETROOT={[date]:round(Math.min(1,(node.values.VWC_5CM*.15+node.values.VWC_25CM*.45+node.values.VWC_100CM*.4)/.45))};
    parameters.GWETTOP={units:'1',longname:'Humedad superficial derivada · porosidad ilustrativa 0.45'};
    parameters.GWETROOT={units:'1',longname:'Humedad radicular derivada · pesos ilustrativos 0.15 / 0.45 / 0.40'};
    parameters.PH_SOIL.proposed=true;
    return {type:'Feature',geometry:node.point?{type:'Point',coordinates:[node.point.lon,node.point.lat]}:null,properties:{parameter},header:{station:{...identity(node),id:node.id,address:node.address,location:node.location||null},title:`SIMULACIÓN LOCAL · Nodo ${node.id}`,api:{version:'1.0',name:`LoRa nodo ${node.id}`},sources:['SIMULACION'],fill_value:-999,time_standard:'LST',start:date,end:date},messages:['Valores de ejemplo editables; no son mediciones físicas ni datos NASA.',node.point?'Ubicación de referencia asignada por el usuario.':'Ubicación geográfica pendiente.','PH_SOIL es una extensión propuesta, ausente del firmware revisado.','Escenario diario ilustrativo: no reproduce el muestreo ni la agregación temporal del firmware.'],parameters};
  }
  function validate(p,node) {
    if(!p || p.type!=='Feature' || p.header?.api?.name!==`LoRa nodo ${node.id}` || p.header?.sources?.length!==1 || p.header.sources[0]!=='SIMULACION') throw Error('Cabecera, nodo o procedencia no válidos para esta simulación.');
    if(p.header.station?.id!==node.id || p.header.station?.address!==node.address)throw Error('La dirección del paquete no corresponde a esta torre.');
    if(p.geometry!==null){
      const xy=p.geometry?.coordinates;
      if(p.geometry?.type!=='Point'||!Array.isArray(xy)||xy.length!==2||!xy.every(Number.isFinite)||Math.abs(xy[0])>180||Math.abs(xy[1])>90)throw Error('Geometría de parcela inválida.');
    }
    const date=p.header.start;
    if(!/^\d{8}$/.test(date)||p.header.end!==date)throw Error('Período diario inválido.');
    const iso=`${date.slice(0,4)}-${date.slice(4,6)}-${date.slice(6,8)}`;
    if(!Number.isFinite(Date.parse(iso)) || new Date(iso).toISOString().slice(0,10)!==iso)throw Error('Fecha inválida.');
    for(const s of [...sensors,{key:'GWETTOP',min:0,max:1},{key:'GWETROOT',min:0,max:1}]) {
      const series=p.properties?.parameter?.[s.key],v=series?.[date];
      if(!Number.isFinite(v)||v<s.min||v>s.max||Object.keys(series).length!==1)throw Error(`Valor ausente o fuera de rango: ${s.key}.`);
      if(!p.parameters?.[s.key]?.units)throw Error(`Falta unidad de ${s.key}.`);
    }
    const v=k=>p.properties.parameter[k][date];
    if(v('T2M_MIN')>v('T2M')||v('T2M')>v('T2M_MAX'))throw Error('Temperatura incoherente: mínima ≤ media ≤ máxima.');
    if(v('WS2M')>v('WS2M_MAX'))throw Error('La ráfaga máxima debe ser mayor o igual al viento medio.');
    return p;
  }
  function conditions(state,node) {
    const out=[];
    if(!node.link)out.push('Enlace interrumpido');
    if(node.last===null)out.push('Sin datos recibidos');
    else if(state.now-node.last>15*60000)out.push('Sin datos recientes (>15 min)');
    if(node.invalid)out.push('JSON inválido');
    if(node.received) {
      const t=state.thresholds, p=node.received, v=k=>p.properties.parameter[k][p.header.start];
      if(v('BAT_V')<t.battery)out.push('Batería baja');
      if(v('LORA_RSSI')<t.rssi||v('LORA_SNR')<t.snr)out.push('Señal débil');
      if(v('VWC_25CM')<t.soil)out.push('Humedad baja · 25 cm');
      if(v('T2M')<t.cold)out.push('Temperatura baja');
      if(v('PH_SOIL')<t.phLow||v('PH_SOIL')>t.phHigh)out.push('pH fuera de umbral · propuesto');
    }
    return out;
  }
  function reconcile(state) {
    state.nodes.forEach(n=>{
      const next=conditions(state,n);
      next.filter(x=>!n.active.includes(x)).forEach(x=>state.events.unshift({node:n.id,time:state.now,text:x,resolved:false}));
      n.active.filter(x=>!next.includes(x)).forEach(x=>state.events.unshift({node:n.id,time:state.now,text:x,resolved:true}));
      n.active=next;
    });state.events=state.events.slice(0,60);
  }
  function receive(state,node,raw) {
    if(!node.link)return {ok:false,error:'Enlace interrumpido: el paquete no llegó a la central.'};
    try {
      const p=validate(typeof raw==='string'?JSON.parse(raw):raw,node);
      node.received=JSON.parse(JSON.stringify(p));node.last=state.now;node.invalid=false;reconcile(state);return {ok:true};
    }catch(e){node.invalid=true;reconcile(state);return {ok:false,error:e.message};}
  }
  function status(n) {
    if(!n.link)return {label:'Sin señal',tone:'bad'};
    if(n.last===null)return {label:'Sin datos',tone:'idle'};
    if(n.active.some(x=>x.startsWith('Sin datos recientes')))return {label:'Sin señal · >15 min',tone:'bad'};
    if(n.active.length)return {label:'Alerta',tone:'warn'};
    return {label:'En línea',tone:'good'};
  }
  const api={sensors,rules,create,packet,validate,receive,reconcile,status,time,day,resize,identify,collection,addTower,removeTower,identity,parsePoint};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.Acquisition=api;
})(typeof globalThis!=='undefined'?globalThis:this);
