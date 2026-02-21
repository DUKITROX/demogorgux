import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function isValidWebUrl(value) {
  const trimmed = value.trim()
  if (!trimmed) return false
  try {
    const u = new URL(trimmed)
    return u.protocol === 'http:' || u.protocol === 'https:'
  } catch {
    return false
  }
}

export default function HomePage() {
  const [url, setUrl] = useState('')
  const [urlError, setUrlError] = useState('')
  const [initializing, setInitializing] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (!initializing) return
    const timer = setTimeout(() => {
      setInitializing(false)
      navigate('/demo', { state: { url: url.trim() || undefined } })
    }, 2000)
    return () => clearTimeout(timer)
  }, [initializing, url, navigate])

  function handleLaunch() {
    setUrlError('')
    if (!isValidWebUrl(url)) {
      setUrlError('Please enter a valid web address (e.g. https://example.com)')
      return
    }
    setInitializing(true)
  }

  return (
    <div className="homepage">
      <div className="homepage__orb homepage__orb--cyan" aria-hidden />
      <div className="homepage__orb homepage__orb--indigo" aria-hidden />
      <div className="homepage__inner">
        <header className="homepage__hero">
          <h1 className="homepage__headline">
            AI Sales Agents that Demo while you Sleep.
          </h1>
          <p className="homepage__subheadline">
            Stop booking setup calls. Our autonomous Sales Engineers join your dashboard,
            narrate your value, and close B2C leads 24/7 for 1/1000th the cost of a human rep.
          </p>
        </header>

        <div className="homepage__card-wrap">
          <div className="homepage__card">
          <div className="homepage__scanner-label">
            <span className="homepage__scanner-badge">Secure Link Scanner</span>
            <p className="homepage__scanner-desc">
              Deploy your Agent. Paste your dashboard or landing page URL to begin the live demo experience.
            </p>
          </div>
          <div className="homepage__input-wrap">
            <input
              type="url"
              className={`homepage__input${urlError ? ' homepage__input--error' : ''}`}
              placeholder="https://your-dashboard.example.com"
              value={url}
              onChange={(e) => { setUrl(e.target.value); setUrlError('') }}
              onKeyDown={(e) => e.key === 'Enter' && handleLaunch()}
              aria-invalid={!!urlError}
              aria-describedby={urlError ? 'homepage-url-error' : undefined}
            />
            {urlError && (
              <p id="homepage-url-error" className="homepage__input-error" role="alert">
                {urlError}
              </p>
            )}
            <button type="button" className="homepage__button" onClick={handleLaunch} disabled={initializing}>
              Launch Demo
            </button>
          </div>
          </div>
        </div>

        <section className="homepage__features" aria-label="Features">
          <div className="homepage__feature">
            <span className="homepage__feature-icon" aria-hidden>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                <path d="M2 12h20" />
              </svg>
            </span>
            <h3 className="homepage__feature-title">Autonomous Navigation</h3>
            <p className="homepage__feature-desc">Agent explores your UI naturally.</p>
          </div>
          <div className="homepage__feature">
            <span className="homepage__feature-icon" aria-hidden>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="23" />
                <line x1="8" y1="23" x2="16" y2="23" />
              </svg>
            </span>
            <h3 className="homepage__feature-title">Voice Synthesis</h3>
            <p className="homepage__feature-desc">Natural human-like demo narration.</p>
          </div>
          <div className="homepage__feature">
            <span className="homepage__feature-icon" aria-hidden>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="20" x2="12" y2="10" />
                <line x1="18" y1="20" x2="18" y2="4" />
                <line x1="6" y1="20" x2="6" y2="16" />
              </svg>
            </span>
            <h3 className="homepage__feature-title">Paid.ai Economics</h3>
            <p className="homepage__feature-desc">Real-time ROI tracking for every session.</p>
          </div>
        </section>

        <section className="homepage__financial" aria-label="Financial Impact">
          <h2 className="homepage__financial-title">Financial Impact</h2>
          <div className="homepage__comparison">
            <div className="homepage__compare-card homepage__compare-card--human">
              <h3 className="homepage__compare-label">Human Sales Engineer</h3>
              <dl className="homepage__compare-dl">
                <div className="homepage__compare-row">
                  <dt>Cost</dt>
                  <dd>$150/hr</dd>
                </div>
                <div className="homepage__compare-row">
                  <dt>Capacity</dt>
                  <dd>Limited to 8/day</dd>
                </div>
                <div className="homepage__compare-row">
                  <dt>Latency</dt>
                  <dd>High Latency</dd>
                </div>
              </dl>
            </div>
            <div className="homepage__compare-card homepage__compare-card--agent">
              <h3 className="homepage__compare-label">Demogorgux Agent</h3>
              <dl className="homepage__compare-dl">
                <div className="homepage__compare-row">
                  <dt>Cost</dt>
                  <dd>$0.05/demo</dd>
                </div>
                <div className="homepage__compare-row">
                  <dt>Capacity</dt>
                  <dd>Infinite Scale</dd>
                </div>
                <div className="homepage__compare-row">
                  <dt>Latency</dt>
                  <dd>0s Wait Time</dd>
                </div>
              </dl>
            </div>
          </div>
        </section>
      </div>

      {initializing && (
        <div className="homepage__init-overlay" role="status" aria-live="polite" aria-label="Initializing agent">
          <div className="homepage__init-card">
            <p className="homepage__init-text">Initializing Agent...</p>
            <div className="homepage__init-progress-wrap">
              <div className="homepage__init-progress-bar" />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
