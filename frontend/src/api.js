const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path) {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status}`);
  }
  return res.json();
}

export function fetchDashboard() {
  return request("/dashboard");
}

export function fetchPatients() {
  return request("/patients");
}

export function fetchPatient(patientId) {
  return request(`/patients/${patientId}`);
}
