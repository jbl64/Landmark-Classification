import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')

function messageForStatus(status) {
  if (status === 400) return "That file doesn't look like a valid image."
  if (status === 413) return 'That image is larger than 10 MB. Try a smaller one.'
  return 'Something went wrong on the server. Please try again.'
}

function App() {
  const [serverStatus, setServerStatus] = useState('waking')
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [classifyStatus, setClassifyStatus] = useState('ready')
  const [predictions, setPredictions] = useState([])
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => {
        setServerStatus(res.ok ? 'ready' : 'error')
      })
      .catch(() => setServerStatus('error'))
  }, [])

  function handleFileChange(event) {
    const chosen = event.target.files[0]
    if (!chosen) return
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setFile(chosen)
    setPreviewUrl(URL.createObjectURL(chosen))
    setClassifyStatus('ready')
    setPredictions([])
    setErrorMessage('')
  }

  async function handleClassify() {
    setClassifyStatus('Loading')
    setPredictions([])
    setErrorMessage('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        setErrorMessage(messageForStatus(res.status))
        setClassifyStatus('error')
        return
      }
      const data = await res.json()
      setPredictions(data.predictions)
      setClassifyStatus('done')
    } catch {
      setErrorMessage(
        "Couldn't reach the server. If you use an ad blocker or Brave Shields, try turning it off for this page."
      )
      setClassifyStatus('error')
    }
  }

  return (
    <main>
      <h1>Landmark Classifier</h1>
      <p>
        {serverStatus === 'waking' && 'Waking up the server...'}
        {serverStatus === 'ready' && 'Server is ready.'}
        {serverStatus === 'error' && "Couldn't reach the server."}
      </p>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      {file && <p>{file.name}</p>}
      {previewUrl && <img src={previewUrl} alt="Selected photo" width="300" />}
      <div>
        <button
          onClick={handleClassify}
          disabled={!file || classifyStatus === 'loading'}
        >
          {classifyStatus === 'loading' ? 'Classifying...' : 'Classify'}
        </button>
      </div>
      {classifyStatus === 'error' && <p>{errorMessage}</p>}
      {predictions.length > 0 && (
        <ul>
          {predictions.map((p) => (
            <li key={p.label}>
              {p.label}: {(p.confidence * 100).toFixed(1)}%
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}

export default App