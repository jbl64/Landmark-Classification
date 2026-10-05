import { useEffect, useState } from 'react'

import Predictions from './Predictions.jsx'

const API_URL = import.meta.env.VITE_API_URL.replace(/\/$/, '')

const UNREACHABLE_MESSAGE =
  "Couldn't reach the server. If you use an ad blocker, try turning it off for this page."

// Maps the backend's error codes to messages for the user.
// 400 = invalid image, 413 = over the 10 MB limit.
// (see backend/README.md for more)
function messageForStatus(status) {
  if (status === 400) return "That file doesn't look like a valid image."
  if (status === 413) return 'That image is larger than 10 MB. Try a smaller one.'
  return 'Something went wrong on the server. Please try again.'
}

function App() {
  // We track two separate statuses because they can overlap
  // serverStatus: the status of the server waking up
  // loading | ready | error
  const [serverStatus, setServerStatus] = useState('loading')
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  // classifyStatus: the status of the current classification request
  // ready | loading | done | error
  const [classifyStatus, setClassifyStatus] = useState('ready')
  const [predictions, setPredictions] = useState([])
  const [errorMessage, setErrorMessage] = useState('')

  // Runs once on page load. Calling /health starts waking the sleeping server
  // before the user has picked a photo.
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
    // We free the old preview from the browser's memory before making a new one
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

    // Don't set a Content-Type header on this request. The browser sets it
    // itself, including a boundary string that only the browser knows, and
    // setting it by hand breaks the upload.
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
      // A successful prediction means that the server is up, even if /health
      // hasn't answered yet
      setServerStatus('ready')
      setClassifyStatus('done')
    } catch {
      // The request never completed: the server is unreachable,
      // blocked by CORS, an ad blocker, or Brave Shields
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
        {classifyStatus === 'loading' && serverStatus === 'loading' && (
          <p className="note">The server is still waking up, so this may take a moment.</p>
        )}
      </section>

      {classifyStatus === 'error' && <p className="error">{errorMessage}</p>}
      {predictions.length > 0 && <Predictions predictions={predictions} />}
    </main>
  )
}

export default App