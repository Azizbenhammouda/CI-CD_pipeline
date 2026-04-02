let projects = [];

const getProjects = (req, res) => {
  res.json(projects);
};

const createProject = (req, res) => {
  const { name, repo } = req.body;

  if (!name || !repo) {
    return res.status(400).json({ message: "Missing fields" });
  }

  const newProject = {
    id: Date.now(),
    name,
    repo,
    status: "pending"
  };

  projects.push(newProject);

  res.status(201).json(newProject);
};

module.exports = {
  getProjects,
  createProject
};