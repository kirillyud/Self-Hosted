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

  const inputStyle = {
    padding: "8px",
    marginRight: "8px",
    borderRadius: "6px",
    border: "1px solid #ccc"
  };

  const buttonStyle = {
    padding: "6px 10px",
    marginRight: "6px",
    borderRadius: "6px",
    border: "none",
    cursor: "pointer"
  };

  return (
    <div style={{ background: "#f5f5f5", minHeight: "100vh", padding: "30px", fontFamily: "sans-serif" }}>
      <h1 style={{ marginBottom: "20px" }}>Projects</h1>

      <div style={{ marginBottom: "25px" }}>
        <input style={inputStyle} placeholder="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input style={inputStyle} placeholder="repo" value={form.repo} onChange={(e) => setForm({ ...form, repo: e.target.value })} />
        <input style={inputStyle} placeholder="port" value={form.port} onChange={(e) => setForm({ ...form, port: e.target.value })} />
        <input style={inputStyle} placeholder="command" value={form.command} onChange={(e) => setForm({ ...form, command: e.target.value })} />
        <button style={{ ...buttonStyle, background: "#4CAF50", color: "white" }} onClick={addProject}>add</button>
      </div>

      {projects.map((p) => (
        <div key={p.name} style={{
          background: "white",
          padding: "15px",
          marginBottom: "12px",
          borderRadius: "10px",
          display: "flex",
          justifyContent: "space-between",
          boxShadow: "0 2px 6px rgba(0,0,0,0.05)"
        }}>
          <div>
            <div style={{ fontWeight: "600" }}>{p.name}</div>
            <div style={{ color: "gray", fontSize: "14px" }}>{p.status}</div>
          </div>

          <div>
            <button style={{ ...buttonStyle, background: "#2196F3", color: "white" }} onClick={() => deploy(p.name)}>deploy</button>
            <button style={{ ...buttonStyle, background: "#FF9800", color: "white" }} onClick={() => stop(p.name)}>stop</button>
            <button style={{ ...buttonStyle, background: "#f44336", color: "white" }} onClick={() => remove(p.name)}>delete</button>
            <button style={{ ...buttonStyle, background: "#555", color: "white" }} onClick={() => getLogs(p.name)}>logs</button>
          </div>
        </div>
      ))}

      {logs && (
        <div style={{ marginTop: "25px", background: "white", padding: "15px", borderRadius: "10px", boxShadow: "0 2px 6px rgba(0,0,0,0.05)" }}>
          <h3 style={{ marginBottom: "10px" }}>Logs</h3>
          <pre style={{ background: "#eee", padding: "10px", borderRadius: "6px", overflowX: "auto" }}>{logs}</pre>
        </div>
      )}
    </div>
  );
}

export default App;