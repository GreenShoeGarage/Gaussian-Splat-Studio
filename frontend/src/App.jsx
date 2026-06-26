import {useState} from "react"

export default function App(){

const [file,setFile]=useState(null)

async function run(){

const body=new FormData()
body.append("file",file)

const r=await fetch(
"http://localhost:8000/api/v1/create",
{
method:"POST",
body
})

const b=await r.blob()

const url=URL.createObjectURL(b)

const a=document.createElement("a")
a.href=url
a.download="gaussian_scene.ply"
a.click()

}

return (
<div>
<h1>Gaussian Splat Studio</h1>

<input
type="file"
onChange={e=>setFile(e.target.files[0])}
/>

<button onClick={run}>
Generate
</button>

</div>
)

}