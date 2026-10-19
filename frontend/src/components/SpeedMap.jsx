import { MapContainer, TileLayer } from "react-leaflet";
import ClickHandler from "./ClickHandler.jsx";
import TowerLayer from "./TowerLayer.jsx";
import SelectedPoint from "./SelectedPoint.jsx";

const HANOI_CENTER = [21.0285, 105.8542];

export default function SpeedMap({ towers, showTowers, result, onMapClick }) {
  return (
    <MapContainer center={HANOI_CENTER} zoom={12} preferCanvas className="map">
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      <ClickHandler onMapClick={onMapClick} />
      {showTowers && <TowerLayer towers={towers} />}
      {result && <SelectedPoint result={result} />}
    </MapContainer>
  );
}
