import { Canvas, useLoader } from "@react-three/fiber";
import { PLYLoader } from "three/examples/jsm/loaders/PLYLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { extend } from "@react-three/fiber";
import * as THREE from "three";
import { useEffect, useRef, useState } from "react";
import * as GaussianSplats3D from "@mkkellogg/gaussian-splats-3d";
extend({ OrbitControls });

export default function Preview({url,type,onClose,settings}) {
 const [auto,setAuto]=useState(settings?.viewer_auto_rotate ?? true);
 const [size,setSize]=useState(settings?.viewer_point_size || .012);
 const [bg,setBg]=useState("#0b0906");
 const wrap=useRef(null);
 function screenshot(){const c=wrap.current?.querySelector("canvas");if(!c)return;const a=document.createElement("a");a.download="maker-splat-screenshot.png";a.href=c.toDataURL("image/png");a.click()}
 return <div className="overlay"><div className="viewer" ref={wrap}><div className="viewerTop"><b>Explore your scene</b><div className="viewerButtons">{type==="ply"&&<button onClick={()=>setAuto(!auto)}>{auto?"Stop Rotate":"Auto Rotate"}</button>}{type==="ply"&&<label className="slider">Point size <input type="range" min="0.004" max="0.04" step="0.002" value={size} onChange={e=>setSize(Number(e.target.value))}/></label>}{type==="ply"&&<button onClick={()=>setBg(bg==="#0b0906"?"#f4efe7":"#0b0906")}>Background</button>}{type==="ply"&&<button onClick={screenshot}>Screenshot</button>}<button onClick={()=>wrap.current?.requestFullscreen?.()}>Fullscreen</button><button onClick={onClose}>Close</button></div></div>{type==="splat"?<SplatScene url={url}/>:<Canvas camera={{position:[0,0,3],fov:55}} gl={{preserveDrawingBuffer:true}}><color attach="background" args={[bg]}/><ambientLight intensity={1}/><PointCloud url={url} size={size}/><OrbitControls args={[undefined,undefined]} autoRotate={auto} autoRotateSpeed={0.8}/></Canvas>}<div className="viewerHelp">Mouse: rotate · wheel: zoom · right/middle drag: pan · Esc: close</div></div></div>
}
function PointCloud({url,size}){const geometry=useLoader(PLYLoader,url);geometry.computeBoundingSphere();const hasColor=Boolean(geometry.getAttribute("color"));return <points geometry={geometry}><pointsMaterial size={size} vertexColors={hasColor} color={hasColor?undefined:new THREE.Color("white")}/></points>}
function SplatScene({url}){const mount=useRef(null);useEffect(()=>{if(!mount.current)return;const viewer=new GaussianSplats3D.Viewer({rootElement:mount.current,initialCameraPosition:[0,1,3],initialCameraLookAt:[0,0,0]});viewer.addSplatScene(url,{progressiveLoad:true}).then(()=>viewer.start()).catch(err=>{mount.current.innerHTML=`<div class="splatError"><h2>Could not open this real splat yet</h2><p>${String(err)}</p></div>`});return()=>{try{viewer.dispose()}catch{}}},[url]);return <div className="splatMount" ref={mount}/>}
