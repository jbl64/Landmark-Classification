import { useEffect, useState } from 'react'

import Predictions from './Predictions.jsx'

const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')

const UNREACHABLE_MESSAGE =
  "Couldn't reach the server. If you use an ad blocker or Brave Shields, try turning it off for this page."
  
function messageForStatus(status) {
  if (status === 400) return "That file doesn't look like a valid image."
  if (status === 413) return 'That image is larger than 10 MB. Try a smaller one.'
  return 'Something went wrong on the server. Please try again.'
}

function App() {
  const [serverStatus, setServerStatus] = useState('loading')
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
    setClassifyStatus('loading')
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
      setServerStatus('ready')
      setClassifyStatus('done')
    } catch {
      setErrorMessage(UNREACHABLE_MESSAGE)
      setClassifyStatus('error')
    }
  }

  return (
    <main className="app">
      <h1>Landmark Classifier</h1>
      <p className="subtitle">
        Upload a photo of a landmark and the model will guess which one it is.
      </p>
      <p className={`status ${serverStatus}`}>
        {serverStatus === 'loading' && 'Waking up the server. The first visit can take a while...'}
        {serverStatus === 'ready' && 'Server is ready.'}
        {serverStatus === 'error' && UNREACHABLE_MESSAGE}
      </p>

      <section className="card">
        <label className="file-button">
          <input type="file" accept="image/*" onChange={handleFileChange} hidden />
          {file ? 'Choose a different photo' : 'Choose a photo'}
        </label>
        {file && <p className="filename">{file.name}</p>}
        {previewUrl && <img className="preview" src={previewUrl} alt="Selected photo" />}
        <button
          className="primary"
          onClick={handleClassify}
          disabled={!file || classifyStatus === 'loading'}
        >
          {classifyStatus === 'loading' ? 'Classifying...' : 'Classify'}
        </button>
        {classifyStatus === 'loading' && (
          <p className="note" role="status">
            <span className="spinner" aria-hidden="true" /> Analyzing your photo...
          </p>
        )}
        {classifyStatus === 'loading' && serverStatus === 'waking' && (
          <p className="note">The server is still waking up, so this may take a moment.</p>
        )}
      </section>

      {classifyStatus === 'error' && <p className="error">{errorMessage}</p>}
      {predictions.length > 0 && <Predictions predictions={predictions} />}
    </main>
  )
}

export default App