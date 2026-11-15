import * as T from './vendor/three.module.min.js';

export const portal={x:-15.4,z:3.8,medioAncho:1.44};
export function cruzaPortal(x0,z0,x1,z1){
  if(x0===x1 || (x0<portal.x)===(x1<portal.x))return false;
  const t=(portal.x-x0)/(x1-x0);
  return Math.abs(z0+t*(z1-z0)-portal.z)<portal.medioAncho;
}

export function crearPortal(scene,box,stations){
  const {x,z}=portal;
  const piedra=0xa17c59;
  for(const lado of [-1,1]){
    const pz=z+lado*1.76;
    box(x,.20,pz,.75,.40,.77,piedra);
    box(x,1.64,pz,.46,2.88,.46,0xb1916c);
    box(x,3.1,pz,.7,.22,.68,piedra);
    box(x,1.68,pz-lado*.25,.18,2.65,.065,0x63c8bd);
  }
  box(x,3.36,z,.62,.36,4.15,0x775940);
  const velo=new T.Mesh(new T.PlaneGeometry(3.05,3.1),
    new T.MeshBasicMaterial({color:0x81e2ca,transparent:true,opacity:.13,side:T.DoubleSide,depthWrite:false}));
  velo.rotation.y=Math.PI/2;velo.position.set(x,1.57,z);scene.add(velo);
  const mini=document.querySelector('#mini'), ctx=mini.getContext('2d');
  const label=document.querySelector('#portalLabel');
  const punto=new T.Vector3();
  let ultimoDibujo=-1;
  return (time,tractor,camera,overview,station)=>{
    velo.material.opacity=.12+.035*Math.sin(time*2);
    punto.set(x,3.65,z).project(camera);
    label.hidden=!!station || Math.abs(punto.x)>1 || Math.abs(punto.y)>1;
    label.style.left=(1+punto.x)*50+'%';label.style.top=(1-punto.y)*50+'%';
    label.textContent='Portal · '+(window.farmArgs?.destino_nombre || '…');
    if(!ctx || time-ultimoDibujo<.12)return;
    ultimoDibujo=time;
    ctx.setTransform(2,0,0,2,0,0);
    ctx.clearRect(0,0,124,130);
    const px=v=>13+(v+17)*2.65, pz=v=>13+(v+10)*2.55;
    ctx.lineWidth=4;ctx.strokeStyle='#74a6a0';ctx.beginPath();
    for(let i=-18;i<=18;i++)ctx.lineTo(px(i),pz(13.5+Math.sin(i*.22)*1.1));
    ctx.stroke();
    ctx.fillStyle='#386043';ctx.font='bold 9px system-ui';
    for(const s of stations){
      const sx=px(s.x),sy=pz(s.z);
      ctx.beginPath();ctx.arc(sx,sy,3,0,Math.PI*2);ctx.fill();
      ctx.fillText({'Rotaciones':'R','Estación climática':'C','Sensor de suelo':'S','Aplicación del agricultor':'4'}[s.name],sx+4,sy);
    }
    ctx.strokeStyle='#14796c';ctx.lineWidth=2;ctx.strokeRect(px(x)-3,pz(z)-3,6,6);
    ctx.save();ctx.translate(px(tractor.position.x),pz(tractor.position.z));ctx.rotate(-tractor.rotation.y);
    ctx.fillStyle='#a64027';ctx.beginPath();ctx.moveTo(0,-5);ctx.lineTo(4,4);ctx.lineTo(-4,4);ctx.closePath();ctx.fill();ctx.restore();
    ctx.fillStyle='#304b40';ctx.fillText('◇ Portal   ▲ Tractor',9,124);
  };
}
