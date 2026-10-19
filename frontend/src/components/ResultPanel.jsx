export default function ResultPanel({ result, error, loading }) {
  if (loading) return <div className="panel">Estimating…</div>;
  if (error) return <div className="panel error">{error}</div>;
  if (!result) return <div className="panel muted">No point selected yet.</div>;

  // TODO: download lớn + mức chất lượng, khoảng 80%, upload, độ trễ,
  // tốc độ lý thuyết, ảnh hưởng thực tế, danh sách trạm gần nhất
  return <div className="panel">{result.download_mbps} Mbps</div>;
}
