export default function InsightPanel({ insight }) {
    if (!insight) return null

    return (
        <div className="fade-in">
            <div className="section-title">📝 Analysis Insight</div>
            <div className="insight-panel">{insight}</div>
        </div>
    )
}
