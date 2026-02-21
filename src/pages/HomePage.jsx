import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function HomePage() {
  const [url, setUrl] = useState('')
  const navigate = useNavigate()

  function handleLaunch() {
    navigate('/demo', { state: { url: url || undefined } })
  }

  return (
    <div className="homepage">
      <div className="homepage__card">
        <h1 className="homepage__title">Homepage</h1>
        <input
          type="url"
          className="homepage__input"
          placeholder="paste the URL here"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleLaunch()}
        />
        <button type="button" className="homepage__button" onClick={handleLaunch}>
          Launch demo
        </button>
      </div>
    </div>
  )
}
