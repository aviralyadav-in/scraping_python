import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:5000";

function Scraping() {

  const [channel, setChannel] = useState("");
  const [limit, setLimit] = useState(10);

  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {

    try {

      const response = await fetch(
        `${API_URL}/api/scrape/status/`
      );

      const data =
        await response.json();

      if (response.ok) {
        setStatus(data);
      }

    } catch (error) {

      console.error(
        "Status error:",
        error
      );

    }
  };

  const startScraping = async () => {

    if (!channel.trim()) {

      alert(
        "Please enter channel name."
      );

      return;
    }

    const numericLimit =
      Number(limit);

    if (
      !Number.isInteger(numericLimit) ||
      numericLimit < 1 ||
      numericLimit > 100
    ) {

      alert(
        "Limit must be between 1 and 100."
      );

      return;
    }

    setLoading(true);

    try {

      const response = await fetch(
        `${API_URL}/api/scrape/start/`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json"
          },
          body: JSON.stringify({
            channel:
              channel.trim(),
            limit:
              numericLimit
          })
        }
      );

      const data =
        await response.json();

      if (!response.ok) {

        alert(
          data.error ||
          "Failed to start scraping."
        );

        return;
      }

      alert(
        data.message ||
        "Scraping started."
      );

      await fetchStatus();

    } catch (error) {

      console.error(
        "Start scraping error:",
        error
      );

      alert(
        "Unable to connect to Flask backend."
      );

    } finally {

      setLoading(false);

    }
  };

  const stopScraping = async () => {

    try {

      const response = await fetch(
        `${API_URL}/api/scrape/stop/`,
        {
          method: "POST"
        }
      );

      const data =
        await response.json();

      if (!response.ok) {

        alert(
          data.error ||
          "Failed to stop scraper."
        );

        return;
      }

      alert(
        data.message ||
        "Stop request received."
      );

      await fetchStatus();

    } catch (error) {

      console.error(
        "Stop scraping error:",
        error
      );

      alert(
        "Unable to connect to Flask backend."
      );
    }
  };

  useEffect(() => {

    fetchStatus();

    const interval =
      setInterval(
        fetchStatus,
        3000
      );

    return () =>
      clearInterval(interval);

  }, []);

  return (
    <div className="page-container">

      <div className="page-header">

        <div>

          <h1>Scraping</h1>

          <p>
            Start and monitor Telegram deal scraping.
          </p>

        </div>

      </div>

      <section className="card">

        <h2>Scraper Control</h2>

        <div className="form-row">

          <div className="form-group">

            <label>
              Channel Name
            </label>

            <input
              type="text"
              value={channel}
              onChange={(e) =>
                setChannel(
                  e.target.value
                )
              }
              placeholder="e.g. allpackbypiyush"
            />

          </div>

          <div className="form-group">

            <label>
              Limit
            </label>

            <input
              type="number"
              min="1"
              max="100"
              value={limit}
              onChange={(e) =>
                setLimit(
                  e.target.value
                )
              }
            />

          </div>

        </div>

        <div className="button-row">

          <button
            className="start-btn"
            onClick={startScraping}
            disabled={loading}
          >
            {loading
              ? "Starting..."
              : "Start Scraping"}
          </button>

          <button
            className="stop-btn"
            onClick={stopScraping}
          >
            Stop Scraping
          </button>

        </div>

      </section>

      <section className="card">

        <h2>Scraping Status</h2>

        {status ? (

          <div className="status-grid">

            <div>
              <strong>Status</strong>
              <span>
                {status.status || "-"}
              </span>
            </div>

            <div>
              <strong>Channel</strong>
              <span>
                {status.channel || "-"}
              </span>
            </div>

            <div>
              <strong>Limit</strong>
              <span>
                {status.limit ?? "-"}
              </span>
            </div>

            <div>
              <strong>Messages Scraped</strong>
              <span>
                {status.messages_scraped ?? 0}
              </span>
            </div>

            <div>
              <strong>Messages Saved</strong>
              <span>
                {status.messages_saved ?? 0}
              </span>
            </div>

            <div>
              <strong>Started At</strong>
              <span>
                {status.started_at || "-"}
              </span>
            </div>

            <div>
              <strong>Completed At</strong>
              <span>
                {status.completed_at || "-"}
              </span>
            </div>

            <div>
              <strong>Current Deal</strong>
              <span>
                {status.current_deal || "-"}
              </span>
            </div>

            <div>
              <strong>Stop Requested</strong>
              <span>
                {status.stop_requested
                  ? "Yes"
                  : "No"}
              </span>
            </div>

            <div>
              <strong>Error</strong>
              <span className="error-text">
                {status.error || "-"}
              </span>
            </div>

          </div>

        ) : (

          <p>
            Loading status...
          </p>

        )}

      </section>

    </div>
  );
}

export default Scraping;