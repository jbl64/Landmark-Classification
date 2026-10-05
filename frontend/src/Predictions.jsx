// We never show a flat 100% or 0% so that the model isn't shown as more certain than it is.
// Values above 99.9% display as ">99.9%" and values below 0.1% as "<0.1%"

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
          {/* The server returns predictions sorted highest first, meaning index 0 is the top answer */}
          <div className={index === 0 ? 'prediction-row top' : 'prediction-row'}>
            <span>{p.label}</span>
            <span>{formatPercent(p.confidence)}</span>
          </div>
          <div className="bar-track">
            {/* Inline because the width comes from the data at runtime, which CSS can't know */}
            <div className="bar-fill" style={{ width: `${p.confidence * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  )
}

export default Predictions