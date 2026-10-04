function formatPercent(confidence) {
  const pct = confidence * 100
  if (pct < 0.1) return '<0.1%'
  if (pct > 99.9) return '>99.9%'
  return `${pct.toFixed(1)}%`
}

function Predictions({ predictions }) {
  return (
    <ul className="predictions">
      {predictions.map((p, index) => (
        <li key={p.label} className="prediction">
          <div className={index === 0 ? 'prediction-row top' : 'prediction-row'}>
            <span>{p.label}</span>
            <span>{formatPercent(p.confidence)}</span>
          </div>
          <div className="bar-track">
            <div className="bar-fill" style={{ width: `${p.confidence * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  )
}

export default Predictions