import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:5000";

function Statistics() {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/api/deals/statistics/`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Failed to fetch statistics."
        );
      }

      setStatistics(data);
    } catch (err) {
      console.error("Statistics error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics();
  }, []);

  if (loading) {
    return (
      <div className="page">
        <h1>Statistics</h1>
        <p>Loading statistics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <h1>Statistics</h1>

        <div className="error-box">
          <p>{error}</p>

          <button onClick={fetchStatistics}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Statistics</h1>
          <p>Deal statistics and scraping summary.</p>
        </div>

        <button
          className="refresh-btn"
          onClick={fetchStatistics}
        >
          Refresh
        </button>
      </div>

      <div className="stats-grid">

        <div className="stat-card">
          <h3>Total Deals</h3>
          <strong>
            {statistics?.total_deals ?? 0}
          </strong>
        </div>

        <div className="stat-card">
          <h3>Unique Deals</h3>
          <strong>
            {statistics?.unique_deals ?? 0}
          </strong>
        </div>

        <div className="stat-card">
          <h3>Duplicate Deals</h3>
          <strong>
            {statistics?.duplicate_deals ?? 0}
          </strong>
        </div>

        <div className="stat-card">
          <h3>Total Channels</h3>
          <strong>
            {statistics?.total_channels ?? 0}
          </strong>
        </div>

      </div>

      <div className="card">
        <h2>Statistics Summary</h2>

        <div className="statistics-list">

          <div className="statistics-row">
            <span>Total Deals</span>
            <strong>
              {statistics?.total_deals ?? 0}
            </strong>
          </div>

          <div className="statistics-row">
            <span>Unique Deals</span>
            <strong>
              {statistics?.unique_deals ?? 0}
            </strong>
          </div>

          <div className="statistics-row">
            <span>Duplicate Deals</span>
            <strong>
              {statistics?.duplicate_deals ?? 0}
            </strong>
          </div>

          <div className="statistics-row">
            <span>Total Channels</span>
            <strong>
              {statistics?.total_channels ?? 0}
            </strong>
          </div>

        </div>
      </div>
    </div>
  );
}

export default Statistics;