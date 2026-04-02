import React, { useState, useEffect } from 'react';
import { getProjects, createProject } from './api';

function App() {
  const [projects, setProjects] = useState([]);
  const [name, setName] = useState('');
  const [repo, setRepo] = useState('');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    const data = await getProjects();
    setProjects(data);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !repo) return;
    await createProject({ name, repo });
    setName('');
    setRepo('');
    fetchProjects();
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1>DevTrack Dashboard</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Project Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ marginRight: '0.5rem' }}
        />
        <input
          type="text"
          placeholder="Repo URL"
          value={repo}
          onChange={(e) => setRepo(e.target.value)}
          style={{ marginRight: '0.5rem' }}
        />
        <button type="submit">Add Project</button>
      </form>

      <ul style={{ marginTop: '2rem' }}>
        {projects.map((p) => (
          <li key={p.id}>
            <strong>{p.name}</strong> - <a href={p.repo}>{p.repo}</a> - {p.status}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;