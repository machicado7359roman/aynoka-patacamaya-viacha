import * as T from './vendor/three.module.min.js';

import { vestirPaisaje } from './paisaje.js';

import { colocarRebanos, corralLlamas, potreroOvejas } from './rebanos.js';
import { trazarCaminos, crearAmbiente } from './caminos.js';

import { apoyarTractor, enTerreno, compuerta, construirOrilla, obstaculosOrilla } from './orilla.js';

import { portal, crearPortal, cruzaPortal } from './portal.js';

const canvas = document.querySelector('canvas');
const stations = [
  {name:'Rotaciones', x:-7, z:-.7, verb:'Comparar rotaciones'},
  {name:'Estación climática', x:4, z:-3.4, verb:'Consultar el clima'},
  {name:'Aplicación del agricultor', x:6.65, z:23.15, verb:'Abrir AYNOKA'},
  {name:'Sensor de suelo', x:8, z:2.1, verb:'Ver sensor de suelo'},
];
function start() {
  const renderer = new T.WebGLRenderer({canvas, antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = T.PCFSoftShadowMap;
  const scene = new T.Scene();
  scene.background = new T.Color(0xf2dcbc);
  scene.fog = new T.FogExp2(0xf2dcbc,.017);
  const camera = new T.OrthographicCamera(-16,16,10,-10,.1,120);
  scene.add(new T.HemisphereLight(0xfff2d6,0xcc956a,2.3));
  const sun = new T.DirectionalLight(0xffddb0,2.5);
  sun.position.set(-16,16,9);
  sun.castShadow=true;
  Object.assign(sun.shadow.camera,{left:-34,right:34,top:35,bottom:-35});
  sun.shadow.mapSize.set(1024,1024);
  sun.shadow.normalBias=.03;
  scene.add(sun);
  const materials=new Map();
  function mesh(geo,color,x,y,z,parent=scene){
    if(!materials.has(color)) materials.set(color,new T.MeshStandardMaterial({color,flatShading:true,roughness:1}));
    const object=new T.Mesh(geo,materials.get(color));
    object.position.set(x,y,z);object.castShadow=true;object.receiveShadow=true;
    parent.add(object);return object;
  }
  const cube=new T.BoxGeometry(1,1,1);
  function box(x,y,z,w,h,d,color,parent){
    const object=mesh(cube,color,x,y,z,parent);
    object.scale.set(w,h,d);return object;
  }
  const ground=0xc9a775,wood=0x75533d,cream=0xf1d6a2;
  box(0,-1.12,0,160,.12,150,0xc4a174);
  box(-1.6,-.55,0,32.8,1,21,0xb47b51);
  box(-1.6,-.12,0,32.8,.25,21,ground);
  const camino=new T.MeshStandardMaterial({color:0xe6c390,roughness:1});
  materials.set(0xe6c390,camino);
  const rutas=[new T.Group(),new T.Group()];
  rutas.forEach((grupo,i)=>{scene.add(grupo);trazarCaminos(grupo,camino,Boolean(i));});
  const conjuntos=[];
  function moverConjunto(desde,dx,dz){
    const objetos=scene.children.slice(desde);
    const grupo=new T.Group();
    scene.add(grupo);
    objetos.forEach(o=>grupo.add(o));
    conjuntos.push({grupo,dx,dz});
  }
  const hill=new T.ConeGeometry(1,1,7);
  for(let i=0;i<12;i++){
    const h=5+4*Math.abs(Math.sin(i*2.2));
    const m=mesh(hill,[0xae8977,0x997f77,0xc49b82][i%3],i*4-25,h/2-1,-15-(i%3)*2);
    m.scale.set(6,h,5);m.rotation.y=i*.7;
  }
  const panoja=new T.IcosahedronGeometry(1,0);
  const plant=new T.ConeGeometry(.19,.72,5);
  for(const [cx,cz,color] of [[-8,-4.1,0xa15758],[.05,-7.15,0x7b8944],[11.6,-4.35,0xb3994a],[-7.4,6.85,0x87934b]]){
    const inicioCultivo=scene.children.length;
    box(cx,.07,cz,5,.13,3.6,0x966940);
    for(let row=0;row<5;row++){
      box(cx-2+row,.16,cz,.42,.19,3.35,0xb0824e);
      for(let n=0;n<7;n++){
        const x=cx-2+row,z=cz-1.4+n*.46;
        if(cx===-8 && row<2){
          mesh(plant,0x7a894c,x,.54,z).scale.set(.6,1.1,.6);
          mesh(panoja,0xac515a,x,.99,z).scale.set(.12,.31,.13);
        }else if(cx===-8 && row<4){
          mesh(panoja,0x617c40,x,.43,z).scale.set(.27,.22,.24);
        }else{
          const stem=mesh(plant,color,x,.56,z);
          if(cx===-8){stem.material=materials.get(0x7a894c);stem.scale.set(.58,1.15,.58)}
        }
      }
    }
    const cambio=cx===-8?[14,0]:cx===.05?[-4,0]:cx===11.6?[0,-2.5]:[18.5,0];
    moverConjunto(inicioCultivo,...cambio);
  }
  // Casa de adobe, techo a dos aguas y puerta hacia el camino.
  box(-10,1,1,3,2,2.6,cream);
  for(const side of [-1,1])box(-10,2.35,1+side*.72,3.5,.18,1.75,0xa15039).rotation.x=side*.42;
  box(-9.9,.73,2.32,.85,1.46,.08,wood);
  box(-10.85,1.2,2.33,.55,.57,.09,0x456963);
  for(let i=0;i<9;i++)box(-12+i*2,.56,9.3,.16,1.12,.16,wood);
  for(const y of [.4,.83])box(-4,y,9.3,16,.13,.12,wood);
  // Estación con panel fotovoltaico y anemómetro.
  let inicio=scene.children.length;
  box(4,1.6,-5,.16,3.2,.16,0x495855);
  const rotor=new T.Group();rotor.position.set(4,3.2,-5);scene.add(rotor);
  for(let i=0;i<3;i++){
    const arm=new T.Group();arm.rotation.y=i*Math.PI*2/3;rotor.add(arm);
    box(.34,0,0,.68,.07,.07,wood,arm);
    mesh(new T.SphereGeometry(.14,7,5),cream,.69,0,0,arm);
  }
  box(5.25,.72,-5,.12,1.44,.12,wood);
  box(5.25,1.5,-5,1.65,.13,1.08,0x355973).rotation.x=-.28;
  moverConjunto(inicio,-17,1);inicio=scene.children.length;
  box(8,.63,3.6,.16,1.25,.16,wood);
  box(8,1.15,3.6,.7,.72,.35,0x528077);
  moverConjunto(inicio,-7.5,-6);inicio=scene.children.length;
  // Panojas de quinua, sonda y gabinete visibles desde el camino.
  const flower=new T.IcosahedronGeometry(1,0);
  for(let i=0;i<8;i++){
    const x=-6.9+.48*Math.sin(i*.45),z=1.55-i*.29;
    box(x,.32,z,.045,.64,.045,0x727c45);
    mesh(flower,0xb56061,x,.73,z).scale.set(.11,.24,.11);
  }
  moverConjunto(inicio,14,0);inicio=scene.children.length;
  // Corte didáctico de suelo, con la sonda a la vista en la cara del perfil.
  box(8.7,.15,3.42,1.5,.3,.65,0xb48558);
  box(8.7,.40,3.42,1.5,.2,.65,0x946440);
  box(8.7,.57,3.42,1.5,.14,.65,0x684933);
  box(8.45,.47,3.77,.065,.85,.06,0x546c73);
  moverConjunto(inicio,-7.5,-6);inicio=scene.children.length;
  const manga=new T.Group();manga.position.set(4,3.85,-5);scene.add(manga);
  box(4,3.52,-5,.07,.75,.07,0x637475);
  for(let i=0;i<5;i++){
    const sleeve=mesh(new T.CylinderGeometry(.205-i*.026,.231-i*.026,.26,10,1,true),
      i%2?0xf3e2ba:0xc66334,.125+i*.253,0,0,manga);
    sleeve.rotation.z=-Math.PI/2;
  }
  moverConjunto(inicio,-17,1);inicio=scene.children.length;
  box(8.45,.48,3.6,.09,.96,.09,0x343c39);
  box(8.22,.9,3.6,.47,.06,.06,0x373c3a);
  box(8,1.18,3.81,.48,.3,.06,0xb9dbbe);
  moverConjunto(inicio,-7.5,-6);inicio=scene.children.length;
  for(let i=0;i<4;i++)box(5.25-.6+i*.4,1.59,-5,.025,.02,1,0x82b0ba).rotation.x=-.28;
  moverConjunto(inicio,-17,1);
  const riego=construirOrilla(scene,box,mesh);
  const animarRebanos=colocarRebanos(scene,box);
  const animarAmbiente=crearAmbiente(scene);
  const moverIchu=vestirPaisaje(scene,materials);
  const halos=stations.map(station=>{
    const halo=new T.Mesh(new T.RingGeometry(1.28,1.38,48),
      new T.MeshBasicMaterial({color:0xf8e5ac,transparent:true,opacity:.58,depthWrite:false}));
    halo.rotation.x=-Math.PI/2;halo.position.set(station.x,.09,station.z);
    scene.add(halo);return halo;
  });
  const dibujarPortal=crearPortal(scene,box,stations);
  const tractor=new T.Group();scene.add(tractor);
  tractor.position.set(-7.3,0,3.8);
  tractor.rotation.y=Math.PI/2;
  box(0,.55,.12,1,.35,1.82,0x44443a,tractor);
  box(0,.9,-.43,.93,.62,1.1,0xbc543e,tractor);
  box(0,1.19,.51,.68,.25,.62,wood,tractor);
  for(const x of [-.45,.45]){
    box(x,1.51,.66,.09,1.1,.09,0x355448,tractor);
    box(x*.72,.97,-1,.2,.22,.07,cream,tractor);
  }
  box(0,2.05,.48,1.28,.13,1.02,0xe9c182,tractor);
  box(.31,1.44,-.48,.12,.76,.13,wood,tractor);
  const wheels=[],frontAxles=[];
  for(const x of [-.58,.58])for(const z of [-.67,.69]){
    const r=z>0?.5:.34;
    const pivot=new T.Group();pivot.position.set(x,r,z);const axle=new T.Group();axle.position.copy(pivot.position);pivot.position.set(0,0,0);
    axle.add(pivot);tractor.add(axle);wheels.push(pivot);if(z<0)frontAxles.push(axle);
    for(const [radius,width,color] of [[r,.29,0x363a35],[r*.49,.32,0xb59366]]){
      mesh(new T.CylinderGeometry(radius,radius,width,12),color,0,0,0,pivot).rotation.z=Math.PI/2;
    }
  }
  const buttons=stations.map(s=>{
    const b=document.createElement('button');b.textContent=s.name;
    b.onclick=()=>visitFarm(s.name);document.querySelector('#markers').append(b);return b;
  });
  const keys=new Set();let nearby=null;
  const action=document.querySelector('#action');
  let juntoAlRiego=false;
  action.onclick=()=>{
    if(juntoAlRiego){riego.accionar();canvas.focus({preventScroll:true})}
    else if(nearby)visitFarm(nearby.name);
  };
  canvas.onkeydown=e=>{
    if(e.key.startsWith('Arrow')){e.preventDefault();keys.add(e.key)}
    if((e.key.toLowerCase()==='e'||e.key==='Enter')&&!e.repeat&&(nearby||juntoAlRiego)){e.preventDefault();action.click()}
  };
  window.onkeyup=e=>keys.delete(e.key);
  window.onblur=canvas.onblur=()=>keys.clear();
  let yaw=.56, pitch=.62, zoom=1;
  const pointers=new Map();
  const span=()=>{const [a,b]=pointers.values();return Math.hypot(a.x-b.x,a.y-b.y)};
  canvas.style.touchAction='none';
  canvas.onpointerdown=e=>{
    canvas.focus();canvas.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  };
  canvas.onpointermove=e=>{
    const last=pointers.get(e.pointerId);if(!last)return;
    const previous=pointers.size===2?span():0;
    yaw-=(e.clientX-last.x)*.007;
    pitch=T.MathUtils.clamp(pitch+(e.clientY-last.y)*.004,.35,1.18);
    pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(previous>1)zoom=T.MathUtils.clamp(zoom*span()/previous,.65,1.8);
  };
  canvas.onlostpointercapture=e=>pointers.delete(e.pointerId);
  canvas.addEventListener('wheel',e=>{
    e.preventDefault();zoom=T.MathUtils.clamp(zoom*Math.exp(-e.deltaY*.001),.65,1.8);
  },{passive:false});
  for(const b of document.querySelectorAll('[data-key]')){
    b.onpointerdown=e=>{b.setPointerCapture(e.pointerId);keys.add(b.dataset.key)};
    b.onlostpointercapture=()=>keys.delete(b.dataset.key);
  }
  let overview=false;
  const mapButton=document.querySelector('#overview');
  mapButton.onclick=()=>{
    overview=!overview;mapButton.setAttribute('aria-pressed',String(overview));
    mapButton.textContent=overview?'Seguir al tractor · M':'Vista aérea · M';
    resize();canvas.focus();
  };
  window.addEventListener('keydown',e=>{if(e.key.toLowerCase()==='m'&&!e.repeat)mapButton.click()});
  const eye=new T.Vector3(15,17,22),target=new T.Vector3(),point=new T.Vector3();
  function resize(){
    const w=canvas.clientWidth,h=canvas.clientHeight,aspect=w/h;
    renderer.setSize(w,h,false);
    const half=overview ? Math.max(22,20/aspect) : Math.max(5.4,6.8/aspect);
    Object.assign(camera,{left:-half*aspect,right:half*aspect,top:half,bottom:-half});
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(canvas);resize();
  const clock=new T.Clock();
  let speed=0,steering=0;
  const postesPortal=[-1,1].map(lado=>{
    const z=portal.z+lado*1.76;
    return [portal.x-.24,portal.x+.24,z-.24,z+.24];
  });
  const comunes=[...postesPortal,...obstaculosOrilla,corralLlamas,potreroOvejas,
    [-11.55,-8.45,-.4,2.4],[-12.1,4.1,9.2,9.4],

  ];
  let obstacles=comunes;
  function distribuir(viacha){
    const clima=viacha?[-17,1]:[0,0],sensor=viacha?[-7.5,-6]:[0,0];
    conjuntos.forEach(({grupo,dx,dz})=>grupo.position.set(viacha?dx:0,0,viacha?dz:0));
    rutas.forEach((g,i)=>g.visible=i===Number(viacha));
    const posiciones=viacha?[[7,-.7],[-13,-2.4],[6.65,23.15],[.5,-3.9]]:[[-7,-.7],[4,-3.4],[6.65,23.15],[8,2.1]];
    stations.forEach((s,i)=>{[s.x,s.z]=posiciones[i];halos[i].position.set(s.x,.09,s.z);});
    const trasladar=([l,r,t,b],[dx,dz])=>[l+dx,r+dx,t+dz,b+dz];
    obstacles=comunes.concat([[3.9,4.1,-5.1,-4.9],[5.1,5.4,-5.1,-4.9]].map(r=>trasladar(r,clima)),
      [[7.95,9.45,3.09,3.77],[7.65,8.52,3.43,3.79]].map(r=>trasladar(r,sensor)));
    scene.background.setHex(viacha?0xd7e4dd:0xf2dcbc);
    scene.fog.color.copy(scene.background);
    materials.get(ground).color.setHex(viacha?0xa6ac76:ground);
  }
  function driveable(x,z){
    if(!enTerreno(x,z))return false;
    return obstacles.every(([l,r,t,b])=>Math.hypot(x-T.MathUtils.clamp(x,l,r),z-T.MathUtils.clamp(z,t,b))>.78);
  }
  let lastStation=null,requestedStation=null;
  window.addEventListener('farmenter',event=>{
    requestedStation=event.detail;speed=0;keys.clear();
  });
  let viajePendiente=false, localidadAnterior=null, finAviso=0, temporizador, recuperacion;
  const aviso=document.querySelector('#viaje'),cortina=document.querySelector('#transicion');
  const pausa=()=>matchMedia('(prefers-reduced-motion: reduce)').matches?0:420;
  function actualizarRegion(){
    const args=window.farmArgs;
    if(!args)return;
    if(localidadAnterior!==args.localidad){
      distribuir(args.localidad==='Viacha');
      if(localidadAnterior || sessionStorage.getItem('astra-destino-portal')===args.localidad){
        clearTimeout(recuperacion);
        sessionStorage.removeItem('astra-destino-portal');
        speed=steering=0;keys.clear();nearby=null;requestedStation=null;
        tractor.position.set(portal.x+2.5,0,portal.z);
        apoyarTractor(tractor,-Math.PI/2);target.copy(tractor.position);
        aviso.textContent='Llegaste a '+args.localidad;finAviso=performance.now()+2600;
        requestAnimationFrame(()=>requestAnimationFrame(()=>cortina.classList.remove('visible')));
        clearTimeout(temporizador);
        temporizador=setTimeout(()=>{viajePendiente=false;canvas.focus({preventScroll:true});},pausa());
      }
      localidadAnterior=args.localidad;
    }
    if(args.parada===requestedStation)requestedStation=null;
  }
  window.addEventListener('farmrender',actualizarRegion);
  actualizarRegion();
  function iniciarViaje(args){
    viajePendiente=true;speed=steering=0;keys.clear();
    aviso.textContent='Viajando a '+args.destino_nombre;
    cortina.textContent=args.destino_nombre;cortina.classList.add('visible');
    sessionStorage.setItem('astra-destino-portal',args.destino_nombre);
    temporizador=setTimeout(()=>window.viajar(args.destino_id),pausa());
    recuperacion=setTimeout(()=>{
      sessionStorage.removeItem('astra-destino-portal');cortina.classList.remove('visible');
      viajePendiente=false;aviso.textContent='Cruza nuevamente para viajar.';finAviso=performance.now()+3000;
    },8000);
  }
  let ultimoFotograma=-Infinity;
  function frame(ahora=0){
    requestAnimationFrame(frame);
    if(document.hidden || ahora-ultimoFotograma<1000/32)return;
    ultimoFotograma=ahora;
    const dt=Math.min(clock.getDelta(),.05);
    const station=stations.find(s=>s.name===(requestedStation || window.farmArgs?.parada));
    if(lastStation && !station){keys.clear();canvas.focus({preventScroll:true})}
    lastStation=station;
    const throttle=Number(keys.has('ArrowUp'))-Number(keys.has('ArrowDown'));
    const steer=Number(keys.has('ArrowLeft'))-Number(keys.has('ArrowRight'));
    steering=T.MathUtils.damp(steering,steer*.54,9,dt);
    const desired=throttle>0?5.4:throttle*3;
    const step=(throttle && speed*throttle>=0?3.6:8)*dt;
    speed=station||viajePendiente?0:speed+T.MathUtils.clamp(desired-speed,-step,step);
    const direction=tractor.rotation.y+speed*Math.tan(steering)*dt/1.4;
    const nextX=tractor.position.x-Math.sin(direction)*speed*dt;
    const nextZ=tractor.position.z-Math.cos(direction)*speed*dt;
    if(driveable(nextX,nextZ)){
      const cruza=cruzaPortal(tractor.position.x,tractor.position.z,nextX,nextZ);
      tractor.position.x=nextX;tractor.position.z=nextZ;apoyarTractor(tractor,direction);
      if(cruza && !viajePendiente && window.farmArgs?.destino_id){
        iniciarViaje(window.farmArgs);
      }
    }
    else speed=0;
    for(const axle of frontAxles)axle.rotation.y=steering;
    for(const wheel of wheels)wheel.rotation.x-=speed*dt/.43;
    rotor.rotation.y+=dt;
    const time=clock.elapsedTime;
    manga.rotation.set(0,.22*Math.sin(time*.9),-.15+.055*Math.sin(time*2.8));
    moverIchu(time);
    riego.animar(dt,time);
    animarRebanos(time,dt,tractor.position);
    animarAmbiente(time,dt,tractor,speed,throttle);
    if(overview&&!station){target.set(0,0,9.2);eye.set(0,34,.01)}
    else{
      point.copy(tractor.position);
      point.x-=Math.sin(direction)*speed*.4;point.z-=Math.cos(direction)*speed*.4;
      point.y=tractor.position.y+.7;
      if(station){
        if(station.name==='Estación climática')point.set(station.x+.5,1.5,station.z-1.6);
        else if(station.name==='Sensor de suelo')point.set(station.x,1,station.z+1.5);
        else if(station.name==='Aplicación del agricultor')point.set(8.18,1.1,23);
        else point.set(station.x-1,1,station.z-1.1);
        // Reservar el lateral derecho o la mitad inferior para la ficha.
        if(canvas.clientWidth>700){point.x+=Math.cos(yaw)*2.8;point.z-=Math.sin(yaw)*2.8}
        else point.y-=2.4;
      }
      target.lerp(point,1-Math.exp(-5*dt));
      eye.set(Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch)).multiplyScalar(29);
    }
    camera.zoom=T.MathUtils.damp(camera.zoom,station?1.22:overview?1:zoom,6,dt);
    camera.updateProjectionMatrix();
    camera.position.copy(target).add(eye);camera.lookAt(target);camera.updateMatrixWorld();
    // Un pequeño margen al salir evita que el aviso parpadee en el borde.
    const distancia=s=>Math.hypot(s.x-tractor.position.x,s.z-tractor.position.z);
    if(nearby && distancia(nearby)>2.9)nearby=null;
    if(!nearby)nearby=stations.find(s=>distancia(s)<2.4) || null;
    stations.forEach((s,i)=>{
      point.set(s.x,2.4,s.z).project(camera);
      buttons[i].style.left=(point.x+1)*50+'%';buttons[i].style.top=(1-point.y)*50+'%';
      buttons[i].setAttribute('aria-current',String(window.farmArgs?.parada===s.name));
      const active=nearby===s;
      halos[i].material.color.setHex(active?0xffbb51:0xffedbf);
      halos[i].material.opacity=active?.84:.44;
      halos[i].scale.setScalar(active?1.08:1);
      buttons[i].classList.toggle('cerca',active);
      buttons[i].hidden=!!station || !overview && !active && distancia(s)>7;
    });
    juntoAlRiego=!station && distancia(compuerta)<2.7;
    action.hidden=!!station||(!nearby&&!juntoAlRiego);
    if(juntoAlRiego)action.textContent=riego.abierta?'Cerrar compuerta · E':'Abrir compuerta · E';
    else if(nearby)action.textContent=nearby.verb+'  ↵';
    if(!viajePendiente && performance.now()>finAviso)aviso.textContent='';
    dibujarPortal(time,tractor,camera,overview,station);
    renderer.render(scene,camera);
  }
  frame();
}
try{start()}catch(error){
  console.error(error);
  document.querySelector('#hint').textContent='El visor 3D no está disponible. Abre el menú Estaciones.';
  document.querySelector('#touch').hidden=true;
}
