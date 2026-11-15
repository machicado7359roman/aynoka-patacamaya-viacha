import * as T from './vendor/three.module.min.js';

import { alturaTerreno, pasoDeRegreso } from './orilla.js';

export function trazarCaminos(scene, material, viacha=false) {
  function camino(points,width,height,tracks=false){
    const curve=new T.CatmullRomCurve3(points.map(([x,z])=>new T.Vector3(x,height,z)));
    function banda(offset,halfWidth,y,mat){
      const pos=[],uv=[],indices=[];
      const segments=Math.max(48, Math.ceil(curve.getLength()*3));
      for(let i=0;i<=segments;i++){
        const t=i/segments,p=curve.getPointAt(t),v=curve.getTangentAt(t);
        for(const side of [-1,1]){
          const shift=offset+side*halfWidth;
          const x=p.x+v.z*shift, z=p.z-v.x*shift;
          pos.push(x,y+alturaTerreno(x,z),z);
          uv.push((side+1)/2,t*curve.getLength()/width);
        }
        if(i){const j=i*2;indices.push(j-2,j-1,j,j,j-1,j+1)}
      }
      const geo=new T.BufferGeometry();
      geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));
      geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));
      geo.setIndex(indices);geo.computeVertexNormals();
      const strip=new T.Mesh(geo,mat);strip.receiveShadow=true;scene.add(strip);
    }
    banda(0,width/2,height,material);
    if(tracks){
      const rut=new T.MeshStandardMaterial({color:0xbf996d,roughness:1,side:T.DoubleSide});
      for(const offset of [-.57,.57])banda(offset,.075,height+.006,rut);
    }
  }
  material.side=T.DoubleSide;
  camino([[-16.5,3.8],[-14.4,3.8],[-12.2,3.7],[-10,3.65]],2.1,.062,true);
  if(viacha){
    camino([[-10,3.65],[-12.5,2.6],[-13,0],[-13,-2.4]],2,.055,true);
    camino([[-7.6,3.26],[-4.5,2],[-1,.8],[.2,-.8],[.5,-3.9]],2.1,.058,true);
    camino([[-1,.8],[2.5,.5],[5,.1],[7,-.7]],1.9,.045);
  }else{
  camino([[-10,3.65],[-7.6,3.26],[-4.5,1.85],[-1,.8],[2,.15],[3.8,-1.5],[4,-3.7]],2.05,.053,true);
  camino([[-6,2.5],[-5.75,1.4],[-6,.25],[-7,-.7]],1.9,.033);
  }
  camino([[-.4,.73],[2.4,1.75],[5.35,2.35],[6.05,4.5],[6.25,6.75],[6.95,8.6],[7,10.6]],2.25,.043);
  camino([[7,16.18],[7,18.1],[6.45,20],[4.9,21.1],[1,22.5],[-4,24],[-7,24],[-10,22.7],[-13.8,19.9],[pasoDeRegreso,17.6],[pasoDeRegreso,15.9]],2.55,.09,true);
  camino([[pasoDeRegreso,10.45],[pasoDeRegreso,8.4],[-14.3,5.2],[-12.6,3.7],[-10.4,3.85],[-7.6,3.26]],2.35,.051);
  camino([[5.05,21.05],[5.8,21.8],[6.65,23.15]],1.85,.055);
  camino([[6.85,18.55],[6.1,19.05],[5.15,19.12]],1.55,.043);
}

export function crearAmbiente(scene){
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const ripple=new T.InstancedMesh(new T.CircleGeometry(1,12),
    new T.MeshBasicMaterial({color:0xb8cec0,transparent:true,opacity:.45,depthWrite:false}),48);
  scene.add(ripple);ripple.frustumCulled=false;
  const count=28, positions=new Float32Array(count*3),life=new Float32Array(count);
  const geometry=new T.BufferGeometry();
  geometry.setAttribute('position',new T.BufferAttribute(positions,3));
  const dust=new T.Points(geometry,new T.PointsMaterial({color:0xc59871,size:.09,transparent:true,opacity:.5,depthWrite:false}));
  dust.frustumCulled=false;scene.add(dust);
  const obj=new T.Object3D();
  let next=0, interval=0;
  return function animate(time,dt,tractor,speed,throttle){
    if(reduced)time=0;
    for(let i=0;i<48;i++){
      const x=i*1.15-23+.16*Math.sin(time*.8+i);
      obj.position.set(x,-.995,13.5+Math.sin(x*.22)*1.1+.65*Math.sin(i*4.1));
      obj.rotation.x=-Math.PI/2;
      obj.scale.set(.18+.13*(1+Math.sin(time+i)),.036,1);
      obj.updateMatrix();ripple.setMatrixAt(i,obj.matrix);
    }
    ripple.instanceMatrix.needsUpdate=true;
    const bridge=tractor.position.z>=10.4 && tractor.position.z<=16.35;
    dust.visible=!bridge&&!reduced;
    if(!dust.visible)life.fill(0);
    interval+=dt;
    if(dust.visible && throttle && Math.abs(speed)>.8 && interval>.065){
      interval=0;
      const pos=positions.subarray(next*3,next*3+3);
      const side=next%2?.57:-.57;
      obj.position.set(side,.14,.75).applyQuaternion(tractor.quaternion).add(tractor.position);
      pos.set(obj.position.toArray());life[next]=.62;next=(next+1)%count;
    }
    for(let i=0;i<count;i++){
      life[i]-=dt;
      if(life[i]>0){positions[i*3]+=.18*dt;positions[i*3+1]+=.43*dt}
      else positions[i*3+1]=-5;
    }
    geometry.attributes.position.needsUpdate=true;
  };
}
