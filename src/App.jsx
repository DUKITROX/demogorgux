import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DemoView from './pages/DemoView'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/demo" element={<DemoView />} />
    </Routes>
  )
}
