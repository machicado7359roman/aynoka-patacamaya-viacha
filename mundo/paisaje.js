import * as T from './vendor/three.module.min.js';

import { alturaTerreno, pasoDeRegreso } from './orilla.js';

// Distribución estable: los mismos macizos y piedras al volver a la finca.
export function vestirPaisaje(scene, materials) {
  let seed = 4729;
  const random = () => ((seed = (Math.imul(seed,1664525)+1013904223)>>>0) / 4294967296);
  const tile = document.createElement('canvas');
  tile.width = tile.height = 128;
  const ctx = tile.getContext('2d');
  ctx.fillStyle = '#f8f2e5';
  ctx.fillRect(0,0,128,128);
  for(let i=0;i<2100;i++){
    ctx.fillStyle = random()>.4 ? 'rgba(90,61,36,.15)' : 'rgba(255,255,252,.8)';
    ctx.fillRect(random()*128,random()*128,.7+random()*2,1);
  }
  for(const [color,u,v] of [[0xc9a775,12,9],[0xe6c390,8,2],[0xb0824e,1,2],[0xf1d6a2,2,2]]){
    const tex=new T.CanvasTexture(tile);
    tex.colorSpace=T.SRGBColorSpace;
    tex.wrapS=tex.wrapT=T.RepeatWrapping; tex.repeat.set(u,v);
    materials.get(color).map=tex; materials.get(color).needsUpdate=true;
  }

  const groups=new Map();
  const shapes={
    blade:new T.ConeGeometry(1,1,3), stone:new T.IcosahedronGeometry(1,0),
    trunk:new T.CylinderGeometry(.75,1,1,6), box:new T.BoxGeometry(1,1,1)
  };
  function place(shape,x,y,z,w,h,d,color,turn=0,lean=0){
    const object=new T.Object3D();
    object.position.set(x,y,z);object.scale.set(w,h,d);object.rotation.set(0,turn,lean);
    object.updateMatrix();
    if(!groups.has(shape))groups.set(shape,[]);
    groups.get(shape).push([object.matrix,color]);
  }
  const grasses=[0x96914f,0x999551,0xc1a65e,0xac944c,0x817c40];
  const stones=[0xb99b8b,0xb3a597,0x967e72];
  for(const [cx,cz,rx,rz] of [[-11,-5,1.5,3],[-3,8.7,6,.45],[10,-4,2.5,2.7],[.8,6.3,1.7,2],[-6,-8,5,1],[12,2,1,.8],[1,-1.45,1.8,.55],[-6,26.35,4,.95],[-10.6,22.8,.95,1.6],[2,20.35,1,.6],[1.5,26.5,1.7,.9],[14.3,21.2,1.4,2.5],[-3.6,17.2,2.3,.65],[-13.4,25.2,1.6,1.4]]){
    for(let i=0;i<95;i++){
      const theta=random()*Math.PI*2,r=Math.sqrt(random());
      const x=cx+Math.cos(theta)*rx*r,z=cz+Math.sin(theta)*rz*r;
      for(let j=0;j<4;j++){
        const h=.16+random()*.34;
        place('blade',x+(random()-.5)*.28,alturaTerreno(x,z)+h/2,z+(random()-.5)*.28,.065,h,.07,grasses[i%5],random()*6,(random()-.5)*.65);
      }
      if(i%14===0)place('stone',x,alturaTerreno(x,z)+.08,z,.21,.14,.18,stones[i%3],theta);
    }
  }
  for(const [x,z] of [[-13.45,2.15],[-11,6],[-12,-7],[11,-6],[10,-7],[12,7],[-4,-8],[14.2,25],[13.5,27.7],[1.6,28.6],[-16.6,23]]){
    const h=1.8+random();
    place('trunk',x,h/2,z,.19,h,.17,0x775e45);
    for(let j=0;j<7;j++){
      const angle=j*2.4;
      place('stone',x+Math.cos(angle)*.64,h+j*.1,z+Math.sin(angle)*.64,.73,.91,.7,
        [0x63783e,0x859348,0xa29c4c][j%3],angle);
    }
  }
  // Canal al pie del terreno con orillas sinuosas y un paso de madera.
  const vertices=[],indices=[];
  for(let i=0;i<=90;i++){
    const x=i*.65-30,z=13.5+Math.sin(x*.22)*1.1;
    vertices.push(x,-1.01,z-1.1,x,-1.01,z+1.1);
    if(i){const k=i*2;indices.push(k-2,k-1,k,k,k-1,k+1)}
    for(const side of [-1,1])place('stone',x,-.99,z+side*1.15,.46,.23,.34,stones[i%3],random()*4);
  }
  const water=new T.BufferGeometry();
  water.setAttribute('position',new T.Float32BufferAttribute(vertices,3)); water.setIndex(indices);water.computeVertexNormals();
  scene.add(new T.Mesh(water,new T.MeshStandardMaterial({color:0x528e88,roughness:.38})));
  for(let i=0;i<20;i++)place('box',7,-.07,10.5+i*.29,3.3,.14,.27,i%3===0?0xac8056:0x996c46);
  for(const side of [-1,1]){
    place('box',7+side*1.6,.63,13.25,.08,.1,5.6,0x78563b);
    for(let i=0;i<4;i++)place('box',7+side*1.6,-.13,10.6+i*1.8,.12,1.8,.12,0x78563b);
  }
  // Paso de losas sobre el canal para volver al camino de la casa.
  for(let i=0;i<13;i++){
    place('box',pasoDeRegreso,-.075,10.5+i*.46,3.5,.15,.455,stones[i%3]);
  }
  for(const x of [pasoDeRegreso-1.65,pasoDeRegreso+1.65]){
    for(const z of [10.6,13.3,15.95])place('stone',x,.18,z,.27,.22,.25,stones[1]);
  }
  const viento={value:0};
  for(const [shape,items] of groups){
    const mesh=new T.InstancedMesh(shapes[shape],new T.MeshStandardMaterial({flatShading:true,roughness:.95}),items.length);
    if(shape==='blade'){
      mesh.material.onBeforeCompile=shader=>{
        shader.uniforms.tiempoViento=viento;
        shader.vertexShader='uniform float tiempoViento;\n'+shader.vertexShader.replace('#include <begin_vertex>',
          '#include <begin_vertex>\n transformed += inverse(mat3(instanceMatrix)) * vec3(1.,0.,.12) * pow(position.y+.5,2.) * (.05+.035*sin(tiempoViento*2.8+instanceMatrix[3].x*.6));');
      };
    }
    items.forEach(([matrix,color],i)=>{mesh.setMatrixAt(i,matrix);mesh.setColorAt(i,new T.Color(color))});
    mesh.castShadow=shape!=='blade';mesh.receiveShadow=true;scene.add(mesh);
  }
  const movimientoReducido=matchMedia('(prefers-reduced-motion: reduce)').matches;
  return time=>{viento.value=movimientoReducido?0:time};
}
