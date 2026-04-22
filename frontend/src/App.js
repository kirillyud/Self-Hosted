import { useEffect, useState } from "react";

function App() {
  const [projects, setProjects] = useState([]);
  const [form, setForm] = useState({ name: "", repo: "", port: "", command: "" });
  const [logs, setLogs] = useState("");

  const fetchProjects = async () => {
    const res = await fetch("http://127.0.0.1:8000/projects");
    const data = await res.json();
    setProjects(data);
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const deploy = async (name) => {
    await fetch(`http://127.0.0.1:8000/deploy/${name}`, { method: "POST" });
    fetchProjects();
  };

  const stop = async (name) => {
    await fetch(`http://127.0.0.1:8000/stop/${name}`, { method: "POST" });
    fetchProjects();
  };

  const remove = async (name) => {
    await fetch(`http://127.0.0.1:8000/projects/${name}`, { method: "DELETE" });
    fetchProjects();
  };

  const addProject = async () => {
    await fetch("http://127.0.0.1:8000/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: form.name,
        repo_url: form.repo,
        port: Number(form.port),
        command: form.command,
      }),
    });

    setForm({ name: "", repo: "", port: "", command: "" });
    fetchProjects();
  };

  const getLogs = async (name) => {
    const res = await fetch(`http://127.0.0.1:8000/projects/${name}/logs`);
    const data = await res.text();
    setLogs(data);
  };

  return (
    <div style={{ background: "#111", color: "white", minHeight: "100vh", padding: "20px" }}>
      <h1>Projects</h1>

      <div style={{ marginBottom: "20px" }}>
        <input placeholder="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input placeholder="repo" value={form.repo} onChange={(e) => setForm({ ...form, repo: e.target.value })} />
        <input placeholder="port" value={form.port} onChange={(e) => setForm({ ...form, port: e.target.value })} />
        <input placeholder="command" value={form.command} onChange={(e) => setForm({ ...form, command: e.target.value })} />
        <button onClick={addProject}>add</button>
      </div>

      {projects.map((p) => (
        <div key={p.name} style={{
          background: "#222",
          padding: "10px",
          marginBottom: "10px",
          borderRadius: "10px",
          display: "flex",
          justifyContent: "space-between"
        }}>
          <div>
            <div>{p.name}</div>
            <div style={{ color: "gray" }}>{p.status}</div>
          </div>

          <div>
            <button onClick={() => deploy(p.name)}>deploy</button>
            <button onClick={() => stop(p.name)}>stop</button>
            <button onClick={() => remove(p.name)}>delete</button>
            <button onClick={() => getLogs(p.name)}>logs</button>
          </div>
        </div>
      ))}

      {logs && (
        <div style={{ marginTop: "20px", background: "#000", padding: "10px" }}>
          <h3>Logs</h3>
          <pre>{logs}</pre>
        </div>
      )}
    </div>
  );
}

export default App;