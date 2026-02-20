import { useState } from 'react'
import './index.css'
import FileUpload from './components/FileUpload'
import QueryInput from './components/QueryInput'
import PipelineStatus from './components/PipelineStatus'
import InsightPanel from './components/InsightPanel'
import ChartGallery from './components/ChartGallery'
import CodePanel from './components/CodePanel'

const API = ''  // Vite proxy handles /api → localhost:8000

export default function App() {
  const [fileData, setFileData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [nodeLog, setNodeLog] = useState([])

  const handleAnalyze = async (query) => {
    if (!fileData) return

    setIsLoading(true)
    setResult(null)
    setNodeLog([])

    // Simulate pipeline steps appearing one by one
    const fakeSteps = ['profiler', 'planner', 'generator', 'executor', 'insight']
    const delays = [500, 2000, 4000, 6000, 8000]

    delays.forEach((delay, i) => {
      setTimeout(() => {
        setNodeLog(prev => {
          if (prev.length <= i) {
            return [...prev, { node: fakeSteps[i], status: 'running' }]
          }
          return prev
        })
      }, delay)
    })

    try {
      const formData = new FormData()
      formData.append('filepath', fileData.filepath)
      formData.append('query', query)

      const res = await fetch(`${API}/api/analyze`, {
        method: 'POST',
        body: formData
      })

      const data = await res.json()

      // Replace fake log with real log from server
      if (data.node_log) {
        setNodeLog(data.node_log)
      }

      setResult(data)
    } catch (e) {
      setResult({ success: false, error: 'Cannot connect to server. Make sure FastAPI is running.' })
    }

    setIsLoading(false)
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1>🤖 Auto-Analyst AI</h1>
        <p>Upload a CSV • Ask in plain English • Get instant multi-chart analysis</p>
      </header>

      {/* Main Layout */}
      <div className="main-grid">
        {/* Sidebar */}
        <aside className="sidebar">
          <FileUpload onFileUploaded={setFileData} />
          <PipelineStatus nodeLog={nodeLog} isLoading={isLoading} />
        </aside>

        {/* Main Content */}
        <main className="content">
          {!fileData ? (
            <div className="glass-card empty-state">
              <div className="icon">📂</div>
              <h3>No Data Loaded</h3>
              <p>Upload a CSV file from the sidebar to get started</p>
            </div>
          ) : (
            <>
              <QueryInput
                onAnalyze={handleAnalyze}
                isLoading={isLoading}
                disabled={!fileData}
              />

              {result?.error && !result?.insight && (
                <div className="glass-card fade-in" style={{ borderColor: 'var(--error)' }}>
                  <div className="section-title" style={{ color: 'var(--error)' }}>❌ Error</div>
                  <div className="code-block">{result.error}</div>
                </div>
              )}

              <InsightPanel insight={result?.insight} />
              <ChartGallery charts={result?.charts} />
              <CodePanel code={result?.code} codeOutput={result?.code_output} />
            </>
          )}
        </main>
      </div>
    </div>
  )
}
