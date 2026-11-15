import * as T from './vendor/three.module.min.js';

// Las medidas del corral también delimitan la conducción.
export const corralLlamas = [.85, 4.65, 4.6, 8.8];
export const potreroOvejas = [-12.8, -7.4, -9.35, -6.2];

export function colocarRebanos(scene, box) {
  function cercar([left,right,back,front]) {
    for(const z of [back,front]){
      for(const x of [left,(left+right)/2,right])box(x,.46,z,.12,.92,.12,0x806447);
      for(const y of [.32,.67])box((left+right)/2,y,z,right-left,.09,.08,0xab8459);
    }
    for(const x of [left,right]){
      box(x,.46,(back+front)/2,.12,.92,.12,0x806447);
      for(const y of [.32,.67])box(x,y,(back+front)/2,.08,.09,front-back,0xab8459);
    }
  }
  cercar(corralLlamas);
  cercar(potreroOvejas);
  const oval=new T.IcosahedronGeometry(1,1), hoof=new T.CylinderGeometry(.76,1,1,6);
  const wool=new T.MeshStandardMaterial({flatShading:true,roughness:.98});
  const pieces=new Map();
  const animals=[];
  function animal(kind,x,y,z,angle,scale,coat,behavior='idle'){
    const root=new T.Group();
    root.position.set(x,y,z);root.rotation.y=angle;root.scale.setScalar(scale);
    const sheep=kind==='oveja',alpaca=kind==='alpaca';
    function part(parent,shape,px,py,pz,w,h,d,color,tilt=0){
      const node=new T.Object3D();
      node.position.set(px,py,pz);node.scale.set(w,h,d);node.rotation.z=tilt;
      parent.add(node);
      if(!pieces.has(shape))pieces.set(shape,[]);
      pieces.get(shape).push({node,color});
    }
    const belly=sheep?.62:.84;
    part(root,oval,0,belly,0,.67,sheep||alpaca?.40:.32,.32,coat);
    for(const px of [-.4,.4])for(const pz of [-.17,.17]){
      part(root,hoof,px,belly*.48,pz,.073,belly*.85,.072,sheep?0x846956:coat);
      part(root,oval,px+.02,.065,pz,.092,.075,.082,0x564539);
    }
    part(root,oval,-.56,belly+.18,0,.18,.14,.14,coat,.35);
    const neck=new T.Group(); neck.position.set(.45,belly+.1,0);root.add(neck);
    const rise=sheep?.18:alpaca?.52:.73;
    part(neck,oval,.12,rise*.48,0,alpaca?.20:.145,rise*.7,.16,coat,-.23);
    part(neck,oval,.22,rise,0,.235,.19,.165,sheep?0x816550:coat);
    part(neck,oval,.40,rise-.06,0,.16,.105,.13,0xb99b7d);
    for(const side of [-1,1]){
      part(neck,oval,.14,rise+.18,side*.11,sheep?.12:.055,sheep?.06:alpaca?.12:.2,.057,coat,sheep?-.25:.19);
      part(neck,oval,.30,rise+.035,side*.14,.034,.034,.025,0x302a25);
    }
    animals.push({root,neck,behavior});
  }
  animal('llama',2.15,0,5.75,.6,1,0xf0d6af,'graze');
  animal('llama',3.45,0,7.4,-.6,1,0xac7651,'watch');
  animal('llama',4.04,0,6.68,-.75,.62,0xd6ae84);
  animal('oveja',-11.5,0,-8,.3,.94,0xe7dbba,'graze');
  animal('oveja',-9.5,0,-7.4,-.65,.88,0xc9b79c);
  animal('oveja',-8.65,0,-8.55,2,.76,0xf3e6c9);
  animal('alpaca',10.5,0,17.8,2.6,1.02,0xe0c098);
  animal('alpaca',12,0,17.1,2,1,0xa77b60,'graze');

  const batches=[];
  for(const [geometry,parts] of pieces){
    const mesh=new T.InstancedMesh(geometry,wool,parts.length);
    mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=false;
    mesh.instanceMatrix.setUsage(T.DynamicDrawUsage);
    parts.forEach(({color},i)=>mesh.setColorAt(i,new T.Color(color)));
    scene.add(mesh);batches.push({mesh,parts});
  }
  return function animate(time,dt,position){
    animals.forEach(({root,neck,behavior},i)=>{
      let angle=.055*Math.sin(time*1.2+i);
      if(behavior==='graze')angle=-1.84+.12*Math.sin(time*1.5+i);
      if(behavior==='watch'){
        const distance=Math.hypot(position.x-root.position.x,position.z-root.position.z);
        angle+=distance<4.8?.05:-1.46;
      }
      neck.rotation.z=T.MathUtils.damp(neck.rotation.z,angle,3.8,dt);
      root.updateMatrixWorld(true);
    });
    for(const {mesh,parts} of batches){
      parts.forEach(({node},i)=>mesh.setMatrixAt(i,node.matrixWorld));
      mesh.instanceMatrix.needsUpdate=true;
    }
  };
}
