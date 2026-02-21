import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const location = useLocation()
  const isDemo = location.pathname === '/demo'

  return (
    <nav className="navbar" aria-label="Main">
      <div className="navbar__inner">
        <Link to="/" className="navbar__logo" aria-label="Demogorgon home">
          DEMOGORGON
        </Link>

        <div className="navbar__links">
          {isDemo ? (
            <Link to="/" className="navbar__link">
              Back to Home
            </Link>
          ) : (
            <>
              <Link to="/#product" className="navbar__link">
                Product
              </Link>
              <Link to="/#agent-economics" className="navbar__link">
                Agent Economics
              </Link>
              <Link to="/#case-studies" className="navbar__link">
                Case Studies
              </Link>
            </>
          )}
          <a href="/docs" className="navbar__docs" rel="noopener noreferrer">
            Docs
          </a>
        </div>
      </div>
    </nav>
  )
}
