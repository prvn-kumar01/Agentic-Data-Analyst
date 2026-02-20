export default function ChartGallery({ charts }) {
    if (!charts || charts.length === 0) return null

    return (
        <div className="fade-in">
            <div className="section-title">📈 Generated Charts ({charts.length})</div>
            <div className="chart-gallery">
                {charts.map((url, i) => (
                    <div key={i} className="chart-card">
                        <img
                            src={`${url}?t=${Date.now()}`}
                            alt={`Chart ${i + 1}`}
                            loading="lazy"
                        />
                        <div className="chart-label">Chart {i + 1}</div>
                    </div>
                ))}
            </div>
        </div>
    )
}
