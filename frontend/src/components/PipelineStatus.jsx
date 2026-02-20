const STEPS = [
    { key: 'profiler', icon: '🕵️', label: 'Profiler — Reading data' },
    { key: 'planner', icon: '🧠', label: 'Planner — Creating strategy' },
    { key: 'generator', icon: '⌨️', label: 'Generator — Writing code' },
    { key: 'executor', icon: '⚙️', label: 'Executor — Running code' },
    { key: 'insight', icon: '📊', label: 'Insight — Summarizing results' },
]

export default function PipelineStatus({ nodeLog, isLoading }) {
    if (!nodeLog.length && !isLoading) return null

    const completedNodes = nodeLog.map(n => n.node)

    // Find current active step
    let activeIdx = -1
    if (isLoading) {
        activeIdx = completedNodes.length  // next step is active
    }

    return (
        <div className="glass-card fade-in">
            <div className="section-title">⚡ Pipeline Progress</div>
            <div className="pipeline-steps">
                {STEPS.map((step, i) => {
                    const isCompleted = completedNodes.includes(step.key)
                    const isActive = i === activeIdx
                    const logEntry = nodeLog.find(n => n.node === step.key)
                    const hasError = logEntry?.error

                    let cls = ''
                    if (isCompleted) cls = hasError ? 'error' : 'completed'
                    else if (isActive) cls = 'active'

                    return (
                        <div key={step.key} className={`pipeline-step ${cls}`}>
                            <span className="step-icon">
                                {isCompleted ? (hasError ? '⚠️' : '✅') : isActive ? '🔄' : '⭕'}
                            </span>
                            <span className="step-label">{step.label}</span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
