import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:5000";

function Logs() {

  const PAGE_LIMIT = 10;

  const [logs, setLogs] =
    useState([]);

  const [logPage, setLogPage] =
    useState(1);

  const [logCount, setLogCount] =
    useState(0);

  const [logTotalPages, setLogTotalPages] =
    useState(1);

  const fetchLogs = async (
    page = logPage
  ) => {

    try {

      const response =
        await fetch(
          `${API_URL}/api/logs/?page=${page}&limit=${PAGE_LIMIT}`
        );

      const data =
        await response.json();

      if (!response.ok) {

        console.error(
          "Logs API error:",
          data
        );

        return;
      }

      setLogs(
        data.results || []
      );

      setLogCount(
        data.count || 0
      );

      setLogTotalPages(
        Math.max(
          1,
          Math.ceil(
            (data.count || 0) /
            PAGE_LIMIT
          )
        )
      );

    } catch (error) {

      console.error(
        "Logs error:",
        error
      );

    }
  };

  useEffect(() => {

    fetchLogs(1);

  }, []);

  const goToPage =
    (page) => {

      if (
        page < 1 ||
        page > logTotalPages
      ) {
        return;
      }

      setLogPage(page);

      fetchLogs(page);
    };

  return (
    <div className="page-container">

      <div className="page-header">

        <div>

          <h1>
            Logs
          </h1>

          <p>
            View Telegram scraper activity and system logs.
          </p>

        </div>

        <button
          className="refresh-btn"
          onClick={() =>
            fetchLogs(logPage)
          }
        >
          Refresh
        </button>

      </div>

      <section className="card">

        <div className="section-header">

          <div>

            <h2>
              Scraping Logs
            </h2>

            <p>
              Total Logs: {logCount}
            </p>

          </div>

        </div>

        <div className="table-container">

          <table>

            <thead>

              <tr>
                <th>Time</th>
                <th>Status</th>
                <th>Message</th>
              </tr>

            </thead>

            <tbody>

              {logs.length > 0 ? (

                logs.map(
                  (log, index) => (

                    <tr
                      key={index}
                    >

                      <td>
                        {log.time ||
                          log.date ||
                          "-"}
                      </td>

                      <td>
                        <span className="log-status">
                          {log.status ||
                            "-"}
                        </span>
                      </td>

                      <td>
                        {log.message ||
                          "-"}
                      </td>

                    </tr>

                  )
                )

              ) : (

                <tr>

                  <td
                    colSpan="3"
                    className="no-data"
                  >
                    No logs found
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

        {logCount > 0 && (

          <div className="pagination">

            <button
              onClick={() =>
                goToPage(
                  logPage - 1
                )
              }
              disabled={
                logPage === 1
              }
            >
              Previous
            </button>

            <span>
              Page {logPage} of{" "}
              {logTotalPages}
            </span>

            <button
              onClick={() =>
                goToPage(
                  logPage + 1
                )
              }
              disabled={
                logPage ===
                logTotalPages
              }
            >
              Next
            </button>

          </div>

        )}

      </section>

    </div>
  );
}

export default Logs;