import {useState} from "react"

export default function App(){

const [file,setFile]=useState()

async function create(){

const data=new FormData()
data.append("file",file)

await fetch(
"http://localhost:8000/api/jobs",
{
method:"POST",
body:data
})

alert("Gaussian scene created")
}

return <main>

<h1>
Gaussian Splat Studio v5
</h1>

<input
type="file"
onChange={
e=>setFile(e.target.files[0])
}
/>

<button onClick={create}>
Generate
</button>

</main>
}