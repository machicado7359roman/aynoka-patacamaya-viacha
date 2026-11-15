import * as T from './vendor/three.module.min.js';

export const puentePrincipal = 7;
export const pasoDeRegreso = -14.7;

export function alturaTerreno(x,z){
  const radio = ((x+6)/8)**2 + ((z-24)/6)**2;
  return 2.65 * Math.max(0,1-radio)**2;
}

// Distancias en el mismo sistema local que los centros de las cuatro ruedas.
export function apoyarTractor(tractor, rumbo){
  const x=tractor.position.x, z=tractor.position.z;
  const seno=Math.sin(rumbo), coseno=Math.cos(rumbo);
  function apoyo(lateral,longitud){
    return alturaTerreno(x+lateral*coseno+longitud*seno,z-lateral*seno+longitud*coseno);
  }
  const izqDel=apoyo(-.58,-.67), derDel=apoyo(.58,-.67);
  const izqTras=apoyo(-.58,.69), derTras=apoyo(.58,.69);
  const delante=(izqDel+derDel)/2, detras=(izqTras+derTras)/2;
  const pendienteLongitudinal=(delante-detras)/1.36;
  const pendienteLateral=(derDel+derTras-izqDel-izqTras)/2.32;
  const cabeceo=Math.atan(pendienteLongitudinal);
  tractor.rotation.set(cabeceo,rumbo,Math.atan(pendienteLateral*Math.cos(cabeceo)),'YXZ');
  tractor.position.y=delante-.67*pendienteLongitudinal;
}

function bordeOrilla(x){
  return 14.8 + Math.sin(x*.22)*1.1;
}

export function enTerreno(x,z){
  if(x < -17 || x > 14 || z < -9.55 || z > 29.3)return false;
  if(z < 10 || z > bordeOrilla(x)+.4)return true;
  return Math.abs(x-puentePrincipal)<.86 || Math.abs(x-pasoDeRegreso)<1.12;
}

export const compuerta={x:4,z:18.2};
export const obstaculosOrilla=[
  [8.4,12.4,21.7,24.3], [4,7.3,25.4,27.4], [9.1,11.9,26.3,27.6],
  [8.05,8.36,22.45,23.55], [3.12,4.9,15.8,18],
  [-4.25,-3.49,-2.74,-1.8], [-8.55,-8,-1.8,-1.2]
];

export function construirOrilla(scene,box,mesh){
  const terreno=new T.PlaneGeometry(1,1,72,44);
  const vertices=terreno.attributes.position;
  for(let i=0;i<vertices.count;i++){
    const x=vertices.getX(i)*38;
    const borde=bordeOrilla(x);
    const z=borde+(.5-vertices.getY(i))*(31-borde);
    vertices.setXYZ(i,x,alturaTerreno(x,z),z);
  }
  terreno.computeVertexNormals();
  const suelo=new T.MeshStandardMaterial({color:0xbca276,roughness:1,side:T.DoubleSide});
  const orilla=new T.Mesh(terreno,suelo);
  orilla.receiveShadow=true;scene.add(orilla);

  // Perfil del talud contra el agua.
  const banco=[],indices=[];
  for(let i=0;i<=72;i++){
    const x=-19+38*i/72,z=bordeOrilla(x);
    banco.push(x,0,z,x,-1.1,z-.18);
    if(i){const k=2*i;indices.push(k-2,k-1,k,k,k-1,k+1)}
  }
  const talud=new T.BufferGeometry();
  talud.setAttribute('position',new T.Float32BufferAttribute(banco,3));talud.setIndex(indices);talud.computeVertexNormals();
  scene.add(new T.Mesh(talud,new T.MeshStandardMaterial({color:0xa6845c,side:T.DoubleSide})));

  const arcilla=0xcfa579, madera=0x805a40, teja=0xa05c43;
  box(10.35,.012,20.52,5.7,.026,2.7,0xd3af7b);
  box(10.4,1.25,23,4,2.5,2.6,arcilla);
  for(const lado of [-1,1]){
    box(10.4,2.7,23+lado*.75,4.55,.16,1.8,teja).rotation.x=lado*.37;
  }
  box(9.8,.88,21.66,1.05,1.76,.1,0x544332);
  box(11.6,1.35,21.64,.85,.69,.12,0x587679);
  box(10.5,2.12,20.98,4.2,.12,1.75,teja).rotation.x=-.1;
  for(const x of [8.55,12.4])box(x,1,20.25,.12,2,.12,madera);
  box(9.9,.74,19.6,1.3,1.48,.12,madera).rotation.y=.9;
  box(10.48,.8,19.1,.14,1.6,.16,arcilla);
  const saco=new T.IcosahedronGeometry(1,1);
  function costal(x,y,z,color){
    mesh(saco,color,x,y,z).scale.set(.25,.31,.22);
    box(x,y+.27,z,.15,.08,.14,madera);
  }
  costal(11.5,.31,21,0xb6a17a);costal(12,.30,21.4,0xb69a70);

  // Tablón bajo el alero occidental, junto al acceso a la cuarta estación.
  for(const z of [22.49,23.51])box(8.18,.88,z,.13,1.76,.13,madera);
  box(8.18,1.22,23,.15,.8,1.24,0x5c7166);
  box(8.18,1.69,23,.53,.12,1.48,teja);

  // Cobertizo abierto, herramientas y parvas en el patio posterior.
  for(const x of [4.15,7.12])for(const z of [25.55,27.24]){
    box(x,.89,z,.14,1.78,.14,madera);
  }
  box(5.64,1.82,26.4,3.65,.16,2.32,0x976f53).rotation.x=.12;
  for(let j=0;j<6;j++){
    box(4.36+j*.5,1.84,26.4,.045,.17,2.32,0xb38e68).rotation.x=.12;
  }
  box(5.5,.69,27.2,2.82,.1,.18,madera);
  for(let j=0;j<3;j++){
    const x=4.9+j*.51;
    box(x,.60,26.86,.055,1.12,.055,madera).rotation.x=.21;
    box(x,.13,26.76,.20,.22,.055,0x657066);
  }
  const heno=new T.CylinderGeometry(.46,.46,1.14,12);
  for(const [x,y,z] of [[9.8,.46,26.9],[10.85,.46,26.9],[10.32,1.23,26.9]]){
    mesh(heno,0xc59f58,x,y,z).rotation.x=Math.PI/2;
    for(const d of [-.35,.35]){
      mesh(new T.CylinderGeometry(.47,.47,.04,12),0x997947,x,y,z+d).rotation.x=Math.PI/2;
    }
  }

  // Paso de la parcela y carretilla con la rueda hacia el lindero.
  const piedra=new T.IcosahedronGeometry(1,0);
  for(const [inicio,fin] of [[-10.5,-8.3],[-4.55,-3.2]]){
    for(let x=inicio;x<=fin;x+=.48){
      mesh(piedra,0x998476,x,.18,-1.45).scale.set(.32,.24,.27);
      mesh(piedra,0xb79d88,x+.18,.36,-1.45).scale.set(.23,.16,.21);
    }
  }
  const rueda=mesh(new T.CylinderGeometry(.25,.25,.14,12),0x4c4943,-3.87,.26,-2.48);
  rueda.rotation.z=Math.PI/2;
  box(-3.87,.57,-2,.64,.31,.83,0x6f8378).rotation.x=.1;
  for(const x of [-4.11,-3.63]){
    box(x,.48,-1.64,.07,.08,1,madera).rotation.x=-.16;
    box(x,.24,-1.77,.07,.43,.07,madera);
  }
  costal(-3.88,.77,-2.08,0xc8b188);

  // Barbecho y rastrojo junto al camino de regreso.
  box(-12,.032,19,4.1,.064,2.7,0xb59569);
  for(let j=0;j<6;j++)box(-13.6+j*.62,.08,19,.22,.10,2.48,0xbca479);

  // Lecho, guías de la compuerta y corriente que avanza al abrir la palanca.
  const x=compuerta.x,zInicio=bordeOrilla(x)-.2,longitud=4;
  box(x,.03,zInicio+longitud/2,.68,.06,longitud,0x78684f);
  for(const lado of [-1,1]){
    box(x+lado*.37,.11,zInicio+longitud/2,.11,.22,longitud,0x9f907b);
    box(x+lado*.38,.68,zInicio+.35,.11,1.36,.14,madera);
  }
  box(x,1.27,zInicio+.35,.98,.13,.18,madera);
  const hoja=box(x,.46,zInicio+.35,.66,.75,.12,0x687d76);
  const palanca=box(x+.47,1.24,zInicio+.35,.68,.1,.12,0x945031);
  const agua=box(x,.106,zInicio,.59,.035,.01,0x599997);
  const brillo=box(x,.128,zInicio,.37,.01,.045,0xb3dbcd);
  let abierta=false, avance=0;
  return {
    get abierta(){return abierta},
    accionar(){abierta=!abierta},
    animar(dt,time){
      avance=T.MathUtils.damp(avance,abierta?1:0,2,dt);
      hoja.position.y=.46+.66*avance;palanca.rotation.z=.8*avance;
      agua.visible=avance>.014;brillo.visible=agua.visible;
      agua.scale.z=Math.max(.002,longitud*avance);
      agua.position.z=zInicio+agua.scale.z/2;
      brillo.position.z=zInicio+(time*.6%1)*agua.scale.z;
    }
  };
}
