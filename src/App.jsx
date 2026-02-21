import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DemoView from './pages/DemoView'

export default function App() {
  return (
    <div className="app-layout">
      <div className="mesh-bg" aria-hidden="true" />
      <div className="grain-overlay" aria-hidden="true" />
      <div className="app-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/demo" element={<DemoView />} />
        </Routes>
      </div>
    </div>
  )
}
