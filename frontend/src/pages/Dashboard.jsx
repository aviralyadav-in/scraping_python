import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:5000";

function Dashboard() {

  const [status, setStatus] = useState(null);
  const [dealCount, setDealCount] = useState(0);
  const [logCount, setLogCount] = useState(0);

  const fetchDashboardData = async () => {

    try {

      const statusResponse = await fetch(
        `${API_URL}/api/scrape/status/`
      );

      if (statusResponse.ok) {
        const statusData =
          await statusResponse.json();

        setStatus(statusData);
      }

      const dealsResponse = await fetch(
        `${API_URL}/api/deals/?page=1&limit=1`
      );

      if (dealsResponse.ok) {

        const dealsData =
          await dealsResponse.json();

        setDealCount(
          dealsData.count || 0
        );
      }

      const logsResponse = await fetch(
        `${API_URL}/api/logs/?page=1&limit=1`
      );

      if (logsResponse.ok) {

        const logsData =
          await logsResponse.json();

        setLogCount(
          logsData.count || 0
        );
      }

    } catch (error) {

      console.error(
        "Dashboard error:",
        error
      );

    }
  };

  useEffect(() => {

    fetchDashboardData();

    const interval =
      setInterval(
        fetchDashboardData,
        5000
      );

    return () =>
      clearInterval(interval);

  }, []);

  return (
    <div className="page-container">

      <div className="page-header">

        <div>

          <h1>Dashboard</h1>

          <p>
            Telegram Deals Scraper Overview
          </p>

        </div>

        <button
          className="refresh-btn"
          onClick={fetchDashboardData}
        >
          Refresh
        </button>

      </div>

      <div className="stats-grid">

        <div className="stat-card">

          <h3>Total Deals</h3>

          <strong>
            {dealCount}
          </strong>

          <p>
            Scraped deals stored in database
          </p>

        </div>

        <div className="stat-card">

          <h3>Scraper Status</h3>

          <strong>
            {status?.status || "idle"}
          </strong>

          <p>
            Current scraper state
          </p>

        </div>

        <div className="stat-card">

          <h3>Messages Saved</h3>

          <strong>
            {status?.messages_saved ?? 0}
          </strong>

          <p>
            Deals saved during current job
          </p>

        </div>

        <div className="stat-card">

          <h3>Total Logs</h3>

          <strong>
            {logCount}
          </strong>

          <p>
            Scraping system logs
          </p>

        </div>

      </div>

      <section className="card">

        <h2>Current Scraping Status</h2>

        <div className="status-grid">

          <div>
            <strong>Status</strong>
            <span>
              {status?.status || "-"}
            </span>
          </div>

          <div>
            <strong>Channel</strong>
            <span>
              {status?.channel || "-"}
            </span>
          </div>

          <div>
            <strong>Limit</strong>
            <span>
              {status?.limit ?? "-"}
            </span>
          </div>

          <div>
            <strong>Current Deal</strong>
            <span>
              {status?.current_deal || "-"}
            </span>
          </div>

          <div>
            <strong>Messages Scraped</strong>
            <span>
              {status?.messages_scraped ?? 0}
            </span>
          </div>

          <div>
            <strong>Messages Saved</strong>
            <span>
              {status?.messages_saved ?? 0}
            </span>
          </div>

        </div>

      </section>

    </div>
  );
}

export default Dashboard;