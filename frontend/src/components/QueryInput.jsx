import { useState } from 'react'

const QUICK_PROMPTS = [
    "Complete data overview with charts",
    "Show distributions and patterns",
    "Top trends and comparisons",
    "Correlation analysis",
    "Summary statistics"
]

export default function QueryInput({ onAnalyze, isLoading, disabled }) {
    const [query, setQuery] = useState('')

    const handleSubmit = () => {
        if (!query.trim()) return
        onAnalyze(query.trim())
    }

    const handleChip = (prompt) => {
        setQuery(prompt)
        onAnalyze(prompt)
    }

    return (
        <div className="glass-card query-section">
            <div className="section-title">💬 Ask Your Question</div>

            <div className="quick-prompts">
                {QUICK_PROMPTS.map((p, i) => (
                    <button
                        key={i}
                        className="quick-chip"
                        onClick={() => handleChip(p)}
                        disabled={isLoading || disabled}
                    >
                        {p}
                    </button>
                ))}
            </div>

            <div className="query-input-row">
                <input
                    type="text"
                    placeholder="e.g., Analyze trends and show key insights with charts..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                    disabled={isLoading || disabled}
                />
                <button
                    className={`btn-analyze ${isLoading ? 'loading' : ''}`}
                    onClick={handleSubmit}
                    disabled={isLoading || disabled || !query.trim()}
                >
                    {isLoading ? <><div className="spinner"></div> Analyzing...</> : '🚀 Analyze'}
                </button>
            </div>
        </div>
    )
}
