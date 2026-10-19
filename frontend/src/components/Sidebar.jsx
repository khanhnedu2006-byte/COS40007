import Legend from "./Legend.jsx";
import ResultPanel from "./ResultPanel.jsx";

export default function Sidebar({ towerCount, showTowers, onToggleTowers, result, error, loading }) {
  return (
    <aside className="sidebar">
      <h1>Hanoi Mobile Internet Speed</h1>
      <p className="hint">Click anywhere on the map to estimate the mobile internet speed at that point.</p>
      {/* TODO: checkbox bật/tắt trạm, hiện towerCount */}
      <Legend />
      <ResultPanel result={result} error={error} loading={loading} />
      <p className="credits">
        Data: Ookla Open Data (CC BY-NC-SA 4.0), OpenCelliD (CC BY-SA 4.0), map © OpenStreetMap contributors.
      </p>
    </aside>
  );
}
