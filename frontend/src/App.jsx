import {useEffect,useMemo,useState} from "react";
import Preview from "./Preview.jsx";
const API=import.meta.env.VITE_API||"http://localhost:8000";

export default function App(){
 const[screen,setScreen]=useState("home"),[projects,setProjects]=useState([]),[project,setProject]=useState(null),[job,setJob]=useState(null),[preview,setPreview]=useState(null),[setup,setSetup]=useState(null),[preflight,setPreflight]=useState(null);
 async function refresh(){setProjects(await(await fetch(`${API}/api/projects`)).json())}
 async function refreshSetup(){setSetup(await(await fetch(`${API}/api/setup`)).json());setPreflight(await(await fetch(`${API}/api/preflight/real-mode`)).json())}
 useEffect(()=>{refresh();refreshSetup()},[]);
 return <main>
  <header><button className="brand" onClick={()=>setScreen("home")}>Maker Splat</button><button onClick={()=>setScreen("new")}>+ New Project</button><button onClick={()=>setScreen("gallery")}>Gallery</button><button onClick={()=>setScreen("setup")}>Setup</button></header>
  {screen==="home"&&<Home setScreen={setScreen} setup={setup} preflight={preflight}/>}
  {screen==="setup"&&<Setup setup={setup} preflight={preflight} refreshSetup={refreshSetup}/>}
  {screen==="new"&&<NewProject onCreated={(p)=>{setProject(p);setScreen("project");refresh()}}/>}
  {screen==="gallery"&&<Gallery projects={projects} open={(p)=>{setProject(p);setScreen("project")}} refresh={refresh}/>}
  {screen==="project"&&project&&<Project project={project} setProject={setProject} job={job} setJob={setJob} setPreview={setPreview} refresh={refresh}/>}
  {preview&&<Preview {...preview} onClose={()=>setPreview(null)}/>}
 </main>
}

function Home({setScreen,setup,preflight}){
 return <section className="home"><p className="pill">3.1 Release Candidate</p><h1>Turn a phone video into a splat.</h1><p className="subtitle">Local maker workflow with Demo Mode plus a real GPU/Nerfstudio path.</p>{setup&&<p className="muted">{setup.computer.summary}</p>}{preflight&&<p className="muted">Real mode: {preflight.message}</p>}<div className="bigActions"><button className="primary" onClick={()=>setScreen("new")}>+ New Project</button><button onClick={()=>setScreen("gallery")}>Open Gallery</button><button onClick={()=>setScreen("setup")}>Real-Mode Setup</button></div><section className="coach"><h2>Capture Modes</h2><div className="coachGrid"><div><b>Object</b><span>Circle slowly and capture high/low angles.</span></div><div><b>Room</b><span>Move slowly and capture corners.</span></div><div><b>Outdoor</b><span>Use soft light and avoid motion.</span></div><div><b>Turntable</b><span>Keep camera still and rotate slowly.</span></div></div></section></section>
}

function Setup({setup,preflight,refreshSetup}){
 return <section className="card narrow"><h1>Setup</h1><button onClick={refreshSetup}>Re-check computer</button>{!setup?<p>Checking...</p>:<><p>{setup.demo_mode}</p><p>{setup.real_mode}</p><h2>{setup.computer.summary}</h2><div className="toolList">{Object.entries(setup.computer.tools).map(([n,i])=><div className="tool" key={n}><b>{i.found?"✓":"×"} {n}</b><span>{i.path||"Not found"}</span></div>)}</div><h2>Real Mode Preflight</h2>{preflight&&<><p>{preflight.message}</p><p className="muted">Missing: {preflight.missing.length?preflight.missing.join(", "):"none"}</p><pre>{JSON.stringify(preflight.gpu,null,2)}</pre></>}<h2>Real mode steps</h2>{setup.real_mode_steps.map(s=><p className="muted" key={s}>• {s}</p>)}</>}</section>
}

function NewProject({onCreated}){
 const[name,setName]=useState("My Splat"),[mode,setMode]=useState("object"),[preset,setPreset]=useState("balanced"),[source,setSource]=useState("video");
 async function create(){const b=new FormData();b.append("name",name);b.append("capture_mode",mode);b.append("preset",preset);b.append("source_type",source);onCreated(await(await fetch(`${API}/api/projects`,{method:"POST",body:b})).json())}
 return <section className="card narrow"><h1>New Project</h1><label>Project name<input value={name} onChange={e=>setName(e.target.value)}/></label><h2>Capture Mode</h2><div className="choiceGrid">{["object","room","outdoor","turntable"].map(x=><button className={mode===x?"choice active":"choice"} onClick={()=>setMode(x)} key={x}><b>{x}</b><span>Maker preset</span></button>)}</div><h2>Input</h2><div className="choiceRow">{["video","photos"].map(x=><button className={source===x?"choice active":"choice"} onClick={()=>setSource(x)} key={x}><b>{x}</b></button>)}</div><h2>Quality</h2><div className="choiceRow">{["fast","balanced","best"].map(x=><button className={preset===x?"choice active":"choice"} onClick={()=>setPreset(x)} key={x}><b>{x}</b></button>)}</div><button className="primary" onClick={create}>Create Project</button></section>
}

function Gallery({projects,open,refresh}){
 const[query,setQuery]=useState(""),[sort,setSort]=useState("recent");
 const shown=useMemo(()=>{let arr=projects.filter(p=>p.name.toLowerCase().includes(query.toLowerCase())); if(sort==="name")arr=[...arr].sort((a,b)=>a.name.localeCompare(b.name)); if(sort==="done")arr=arr.filter(p=>p.status==="done"); return arr},[projects,query,sort]);
 return <section className="gallery"><h1>Gallery</h1><div className="toolbar"><input placeholder="Search projects" value={query} onChange={e=>setQuery(e.target.value)}/><button onClick={()=>setSort(sort==="name"?"recent":"name")}>Sort: {sort}</button><button onClick={()=>setSort("done")}>Done only</button><button onClick={()=>{setSort("recent");setQuery("");refresh()}}>Refresh</button></div><div className="tiles">{shown.map(p=><button className="tile" key={p.id} onClick={()=>open(p)}>{p.artifacts?.includes("thumbnail")?<img src={`${API}/api/projects/${p.id}/download/thumbnail`}/>:<div className="emptyThumb">✦</div>}<b>{p.name}</b><span>{p.status} · {p.capture_mode}</span></button>)}</div></section>
}

function Project({project,setProject,job,setJob,setPreview,refresh}){
 const[files,setFiles]=useState([]),[log,setLog]=useState(""),[rename,setRename]=useState(project.name),[error,setError]=useState("");
 async function reload(){const p=await(await fetch(`${API}/api/projects/${project.id}`)).json();setProject(p);setRename(p.name);refresh()}
 async function upload(){const b=new FormData();files.forEach(f=>b.append("files",f));setProject(await(await fetch(`${API}/api/projects/${project.id}/upload`,{method:"POST",body:b})).json())}
 async function analyze(){const q=await(await fetch(`${API}/api/projects/${project.id}/analyze`,{method:"POST"})).json();setProject({...project,quality:q})}
 async function generate(){setError("");const res=await fetch(`${API}/api/projects/${project.id}/generate`,{method:"POST"});if(!res.ok){const data=await res.json();setError(data.detail||"Could not start generation");return}setJob(await res.json())}
 async function cancel(){if(job) setJob(await(await fetch(`${API}/api/jobs/${job.id}/cancel`,{method:"POST"})).json())}
 async function makeExport(p){await fetch(`${API}/api/projects/${project.id}/export/${p}`,{method:"POST"}); window.location.href=`${API}/api/projects/${project.id}/download-export/${p}`}
 async function saveName(){const b=new FormData();b.append("name",rename);setProject(await(await fetch(`${API}/api/projects/${project.id}`,{method:"PATCH",body:b})).json());refresh()}
 useEffect(()=>{if(!job||["done","error","canceled"].includes(job.status))return;const t=setInterval(async()=>{setJob(await(await fetch(`${API}/api/jobs/${job.id}`)).json());reload()},1000);return()=>clearInterval(t)},[job]);
 const url=n=>`${API}/api/projects/${project.id}/download/${n}`;
 return <section className="workspace"><div className="left"><div className="card"><p className="pill">Project</p><h1>{project.name}</h1><div className="rename"><input value={rename} onChange={e=>setRename(e.target.value)}/><button onClick={saveName}>Rename</button></div><p className="muted">{project.capture_mode} · {project.preset}</p>{project.mode_tips&&<div className="miniTips">{project.mode_tips.map(t=><p key={t}>• {t}</p>)}</div>}<label className="drop"><input type="file" multiple accept="image/*,video/*" onChange={e=>setFiles(Array.from(e.target.files||[]))}/><b>{files.length?`${files.length} file(s) selected`:"Drop or choose video/photos"}</b><span>Short video or 30–150 photos.</span></label><div className="actions"><button disabled={!files.length} onClick={upload}>1. Import</button><button disabled={project.status==="created"} onClick={analyze}>2. Check Quality</button><button className="primary" disabled={project.status==="created"} onClick={generate}>3. Generate</button>{job&&["queued","running","canceling"].includes(job.status)&&<button onClick={cancel}>Cancel</button>}</div>{error&&<p className="warnings">⚠ {error}</p>}</div>{project.quality&&<Quality q={project.quality}/>} {job&&<div className="card"><h2>{job.stage}</h2><progress value={job.progress} max="100"/><p>{job.message}</p></div>}{project.error&&<div className="card warnings">⚠ {project.error}</div>}{log&&<pre className="log">{log}</pre>}</div><aside className="side card"><h2>Explore</h2><p>{project.status}</p><p>{project.stage}</p><div className="sideActions">{project.artifacts?.includes("ply")&&<button onClick={()=>setPreview({url:url("ply"),type:"ply"})}>Preview PLY</button>}{project.artifacts?.includes("splat")&&<button onClick={()=>setPreview({url:url("splat"),type:"splat"})}>Preview SPLAT</button>}<button onClick={()=>makeExport("supersplat")}>Export SuperSplat</button><button onClick={()=>makeExport("playcanvas")}>Export PlayCanvas</button><button onClick={()=>makeExport("blender")}>Export Blender</button><button onClick={()=>makeExport("web")}>Export Web Viewer</button>{project.artifacts?.includes("zip")&&<a href={url("zip")}>Everything ZIP</a>}<button onClick={async()=>setLog(await(await fetch(`${API}/api/projects/${project.id}/log`)).text())}>Show Log</button><button onClick={async()=>{await fetch(`${API}/api/projects/${project.id}`,{method:"DELETE"});refresh()}}>Delete</button></div></aside></section>
}

function Quality({q}){return <div className="card"><h2>Capture Score</h2><div className="score">{q.score}%</div><p>{q.label} · {q.count} · {q.mode}</p>{Object.entries(q.metrics).map(([k,v])=><div className="metric" key={k}><span>{k}</span><div><i style={{width:`${v}%`}}/></div><b>{v}%</b></div>)}{q.warnings?.map(w=><p className="warnings" key={w}>⚠ {w}</p>)}{q.tips?.map(t=><p className="muted" key={t}>Tip: {t}</p>)}</div>}
