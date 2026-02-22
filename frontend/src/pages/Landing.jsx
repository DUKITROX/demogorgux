import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')

  const handleLaunch = () => {
    const targetUrl = url.trim()
    if (!targetUrl) return
    navigate(`/demo?url=${encodeURIComponent(targetUrl)}`)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && url.trim()) {
      handleLaunch()
    }
  }

  const unicorns = [
    { emoji: '🦄', top: '8%', left: '5%', size: '2.5rem', delay: '0s', duration: '6s' },
    { emoji: '🦄', top: '15%', right: '8%', size: '3rem', delay: '1s', duration: '7s' },
    { emoji: '🦄', top: '70%', left: '10%', size: '2rem', delay: '2s', duration: '5s' },
    { emoji: '🦄', top: '80%', right: '12%', size: '2.8rem', delay: '0.5s', duration: '8s' },
    { emoji: '🦄', top: '40%', left: '3%', size: '1.8rem', delay: '3s', duration: '6.5s' },
    { emoji: '🦄', top: '25%', right: '3%', size: '2.2rem', delay: '1.5s', duration: '7.5s' },
    { emoji: '🦄', top: '55%', right: '5%', size: '2rem', delay: '2.5s', duration: '5.5s' },
    { emoji: '🦄', top: '90%', left: '30%', size: '1.5rem', delay: '4s', duration: '6s' },
    { emoji: '🦄', top: '5%', left: '40%', size: '1.8rem', delay: '3.5s', duration: '7s' },
    { emoji: '🦄', top: '60%', left: '85%', size: '2.5rem', delay: '1.2s', duration: '8s' },
    { emoji: '🌈', top: '12%', left: '20%', size: '2rem', delay: '0.8s', duration: '9s' },
    { emoji: '🌈', top: '75%', right: '25%', size: '1.8rem', delay: '2.2s', duration: '7s' },
    { emoji: '✨', top: '30%', left: '15%', size: '1.2rem', delay: '1.8s', duration: '4s' },
    { emoji: '✨', top: '45%', right: '18%', size: '1rem', delay: '0.3s', duration: '3.5s' },
    { emoji: '✨', top: '85%', left: '50%', size: '1.3rem', delay: '2.8s', duration: '4.5s' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center relative overflow-hidden">
      {/* Unicornios flotantes */}
      {unicorns.map((u, i) => (
        <span
          key={i}
          className="absolute animate-float-unicorn select-none pointer-events-none"
          style={{
            top: u.top,
            left: u.left,
            right: u.right,
            fontSize: u.size,
            animationDelay: u.delay,
            animationDuration: u.duration,
            opacity: 0.5,
          }}
        >
          {u.emoji}
        </span>
      ))}

      <div className="relative z-10 text-center animate-fade-in">
        <h1 className="text-6xl font-bold text-gray-900 tracking-tight mb-3">
          DemoX
        </h1>
        <p className="text-xl text-gray-500 mb-10">
          Automating <span className="font-bold">demos</span> so you can focus on what actually matters
        </p>

        <div className="flex flex-col items-center gap-4 max-w-lg mx-auto">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter a website URL to demo (e.g. https://example.com)"
            className="w-full px-5 py-3.5 bg-gray-100 border border-black rounded text-gray-900 placeholder-gray-400 focus:outline-none focus:border-mint focus:ring-1 focus:ring-mint transition-colors text-base"
          />
          <div className="flex items-center gap-4 w-full">
            <button
              onClick={handleLaunch}
              disabled={!url.trim()}
              className="flex-1 px-8 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 text-base font-semibold rounded border border-gray-300 transition-all duration-200 hover:shadow-md disabled:opacity-40 disabled:hover:bg-gray-200 disabled:cursor-not-allowed"
            >
              Launch Demo
            </button>
            <button
              onClick={() => navigate('/demo?url=' + encodeURIComponent('https://monkeytype.com'))}
              className="flex-1 px-8 py-3 bg-gray-800 hover:bg-gray-700 text-white text-base font-semibold rounded transition-all duration-200 hover:shadow-md"
            >
              Demo Monkeytype
            </button>
          </div>

          <div className="w-full h-px bg-gray-200 mt-6" />

          <button
            onClick={() => navigate('/savings')}
            className="w-full px-8 py-3 bg-mint hover:bg-mint-hover text-white text-base font-semibold rounded transition-all duration-200 hover:shadow-md mt-4"
          >
            Calculate Savings
          </button>
        </div>
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.8s ease-out;
        }
        @keyframes float-unicorn {
          0% { transform: translateY(0px) rotate(0deg); }
          25% { transform: translateY(-15px) rotate(5deg); }
          50% { transform: translateY(-5px) rotate(-3deg); }
          75% { transform: translateY(-20px) rotate(3deg); }
          100% { transform: translateY(0px) rotate(0deg); }
        }
        .animate-float-unicorn {
          animation: float-unicorn 6s ease-in-out infinite;
        }
      `}</style>
    </div>
  )
}
