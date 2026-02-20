import { useState } from 'react'

export default function CodePanel({ code, codeOutput }) {
    const [showCode, setShowCode] = useState(false)
    const [showOutput, setShowOutput] = useState(false)

    if (!code && !codeOutput) return null

    return (
        <div className="fade-in">
            {code && (
                <div className="collapsible">
                    <div
                        className={`collapsible-header ${showCode ? 'open' : ''}`}
                        onClick={() => setShowCode(!showCode)}
                    >
                        <span>💻 Generated Python Code ({code.length} chars)</span>
                        <span className="arrow">▼</span>
                    </div>
                    {showCode && (
                        <div className="collapsible-content">
                            <div className="code-block">{code}</div>
                        </div>
                    )}
                </div>
            )}

            {codeOutput && (
                <div className="collapsible" style={{ marginTop: '0.5rem' }}>
                    <div
                        className={`collapsible-header ${showOutput ? 'open' : ''}`}
                        onClick={() => setShowOutput(!showOutput)}
                    >
                        <span>⚙️ Code Output</span>
                        <span className="arrow">▼</span>
                    </div>
                    {showOutput && (
                        <div className="collapsible-content">
                            <div className="code-block">{codeOutput}</div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
