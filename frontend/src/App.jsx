import { useEffect, useState } from "react";
import SpeedMap from "./components/SpeedMap.jsx";
import Sidebar from "./components/Sidebar.jsx";
import { fetchPrediction, fetchTowers } from "./api.js";

export default function App() {
  const [towers, setTowers] = useState([]);
  const [showTowers, setShowTowers] = useState(true);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // TODO: fetchTowers().then(setTowers).catch((e) => setError(e.message));
  }, []);

  async function handleMapClick(lat, lon) {
    // TODO: setLoading(true) -> fetchPrediction(lat, lon) -> setResult / setError -> setLoading(false)
  }

  return (
    <div className="layout">
      <Sidebar
        towerCount={towers.length}
        showTowers={showTowers}
        onToggleTowers={setShowTowers}
        result={result}
        error={error}
        loading={loading}
      />
      <SpeedMap towers={towers} showTowers={showTowers} result={result} onMapClick={handleMapClick} />
    </div>
  );
}
