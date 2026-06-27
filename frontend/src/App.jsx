import { useEffect, useState } from "react";
import Preview from "./Preview.jsx";

const API = import.meta.env.VITE_API || "http://localhost:8000";

export default function App() {
  const [files, setFiles] = useState([]);
  const [job, setJob] = useState(null);
  const [log, setLog] = useState("");
  const [previewUrl, setPreviewUrl] = useState(null);

  async function generate() {
    const body = new FormData();
    for (const file of files) body.append("files", file);

    const res = await fetch(`${API}/generate`, { method: "POST", body });
    const data = await res.json();
    setJob(data);
    setLog("");
  }

  useEffect(() => {
    if (!job || ["done", "error"].includes(job.status)) return;

    const timer = setInterval(async () => {
      const res = await fetch(`${API}/jobs/${job.id}`);
      setJob(await res.json());
    }, 1000);

    return () => clearInterval(timer);
  }, [job]);

  async function loadLog() {
    if (!job) return;
    const res = await fetch(`${API}/jobs/${job.id}/log`);
    setLog(await res.text());
  }

  function downloadUrl(name) {
    return `${API}/jobs/${job.id}/download/${name}`;
  }

  return (
    <main>
      <section className="hero">
        <div>
          <p className="pill">Local maker tool</p>
          <h1>Maker Splat</h1>
          <p className="subtitle">
            Turn a phone video or a folder of photos into a Gaussian splat.
          </p>
        </div>
      </section>

      <section className="card">
        <label className="drop">
          <input
            type="file"
            multiple
            accept="image/*,video/*"
            onChange={(e) => setFiles(Array.from(e.target.files || []))}
          />
          <strong>{files.length ? `${files.length} file(s) selected` : "Drop or choose video/photos"}</strong>
          <span>Use a short video or 30–150 overlapping photos.</span>
        </label>

        <button className="mainButton" disabled={!files.length || job?.status === "running"} onClick={generate}>
          Generate Splat
        </button>

        {job && (
          <div className="job">
            <div className="row">
              <strong>{job.status}</strong>
              <span>{job.progress}%</span>
            </div>
            <progress value={job.progress} max="100" />
            <p>{job.message}</p>

            {job.status === "done" && (
              <div className="actions">
                {job.artifacts.includes("ply") && (
                  <>
                    <button onClick={() => setPreviewUrl(downloadUrl("ply"))}>Preview PLY</button>
                    <a href={downloadUrl("ply")}>Download PLY</a>
                  </>
                )}
                {job.artifacts.includes("splat") && <a href={downloadUrl("splat")}>Download SPLAT</a>}
                {job.artifacts.includes("zip") && <a href={downloadUrl("zip")}>Download ZIP</a>}
                <button onClick={loadLog}>View log</button>
              </div>
            )}

            {job.status === "error" && <p className="error">{job.message}</p>}
          </div>
        )}

        {log && <pre className="log">{log}</pre>}
      </section>

      <section className="tips">
        <h2>How to get a good splat</h2>
        <p>Move slowly. Keep the object centered. Use good light. Avoid shiny glassy things.</p>
      </section>

      {previewUrl && <Preview url={previewUrl} onClose={() => setPreviewUrl(null)} />}
    </main>
  );
}
