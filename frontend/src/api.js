export async function fetchTowers() {
  const res = await fetch("/api/towers");
  if (!res.ok) throw new Error("Could not load towers");
  return res.json();
}

export async function fetchPrediction(lat, lon) {
  const res = await fetch(`/api/predict?lat=${lat}&lon=${lon}`);
  const body = await res.json();
  if (!res.ok) throw new Error(body.detail || "Prediction failed");
  return body;
}
