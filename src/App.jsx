import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import DemoView from './pages/DemoView'

export default function App() {
  return (
    <div className="app-layout">
      <div className="mesh-bg" aria-hidden="true" />
      <div className="grain-overlay" aria-hidden="true" />
      <Navbar />
      <div className="app-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/demo" element={<DemoView />} />
        </Routes>
      </div>
      <Footer />
    </div>
  )
}
