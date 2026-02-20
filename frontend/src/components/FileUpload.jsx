import { useState, useRef, useEffect } from 'react'

const API = ''  // Vite proxy handles /api → localhost:8000

export default function FileUpload({ onFileUploaded }) {
    const [dragOver, setDragOver] = useState(false)
    const [uploading, setUploading] = useState(false)
    const [fileData, setFileData] = useState(null)
    const [serverStatus, setServerStatus] = useState('checking') // 'checking' | 'online' | 'offline'
    const [errorMsg, setErrorMsg] = useState('')
    const inputRef = useRef()

    // Check server connection on mount
    useEffect(() => {
        const checkServer = async () => {
            try {
                const res = await fetch(`${API}/api/health`, { mode: 'cors' })
                if (res.ok) {
                    setServerStatus('online')
                } else {
                    setServerStatus('offline')
                }
            } catch {
                setServerStatus('offline')
            }
        }
        checkServer()
        // Re-check every 5 seconds if offline
        const interval = setInterval(() => {
            if (serverStatus === 'offline') checkServer()
        }, 5000)
        return () => clearInterval(interval)
    }, [serverStatus])

    const handleFile = async (file) => {
        if (!file || !file.name.toLowerCase().endsWith('.csv')) {
            setErrorMsg('Please upload a .csv file')
            return
        }

        setUploading(true)
        setErrorMsg('')

        const formData = new FormData()
        formData.append('file', file)

        try {
            const res = await fetch(`${API}/api/upload`, {
                method: 'POST',
                body: formData
            })
            const data = await res.json()

            if (data.success) {
                setFileData(data)
                onFileUploaded(data)
                setServerStatus('online')
            } else {
                setErrorMsg('Upload failed: ' + data.error)
            }
        } catch (e) {
            console.error('Upload error:', e)
            setErrorMsg(`Server unreachable: ${e.message}. Is FastAPI running on port 8000?`)
            setServerStatus('offline')
        }
        setUploading(false)
    }

    return (
        <div className="glass-card">
            <div className="section-title">
                📂 Data Upload
                <span style={{
                    marginLeft: 'auto',
                    fontSize: '0.7rem',
                    color: serverStatus === 'online' ? 'var(--success)' :
                        serverStatus === 'offline' ? 'var(--error)' : 'var(--text-muted)'
                }}>
                    {serverStatus === 'online' ? '🟢 Server Online' :
                        serverStatus === 'offline' ? '🔴 Server Offline' : '⏳ Checking...'}
                </span>
            </div>

            {serverStatus === 'offline' && (
                <div style={{
                    background: 'rgba(239, 83, 80, 0.1)',
                    border: '1px solid rgba(239, 83, 80, 0.3)',
                    borderRadius: '8px', padding: '0.7rem', marginBottom: '0.8rem',
                    fontSize: '0.8rem', color: 'var(--error)'
                }}>
                    ⚠️ Cannot reach FastAPI server. Run <code>python server.py</code> in a terminal first.
                </div>
            )}

            <div
                className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
                onClick={() => inputRef.current.click()}
            >
                <input ref={inputRef} type="file" accept=".csv" onChange={(e) => handleFile(e.target.files[0])} />
                <div className="icon">{uploading ? '⏳' : '📁'}</div>
                <div className="label">
                    {uploading ? 'Uploading...' : <>Drag & drop CSV or <span>browse</span></>}
                </div>
            </div>

            {errorMsg && (
                <div style={{
                    color: 'var(--error)', fontSize: '0.8rem',
                    marginTop: '0.5rem', padding: '0.5rem 0.8rem',
                    background: 'rgba(239, 83, 80, 0.08)', borderRadius: '6px'
                }}>
                    {errorMsg}
                </div>
            )}

            {fileData && (
                <>
                    <div className="file-info">
                        <div className="file-icon">📊</div>
                        <div className="file-details">
                            <h4>{fileData.filename}</h4>
                            <p>{fileData.rows.toLocaleString()} rows × {fileData.cols} columns</p>
                        </div>
                    </div>

                    <div className="data-preview">
                        <table>
                            <thead>
                                <tr>
                                    {fileData.column_names.map(col => <th key={col}>{col}</th>)}
                                </tr>
                            </thead>
                            <tbody>
                                {fileData.preview.slice(0, 6).map((row, i) => (
                                    <tr key={i}>
                                        {fileData.column_names.map(col => (
                                            <td key={col}>{row[col] != null ? String(row[col]) : '—'}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}
        </div>
    )
}
