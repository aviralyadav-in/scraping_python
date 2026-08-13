import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:5000";

function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [totalJobs, setTotalJobs] =
    useState(0);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  // ---------------------------------------------
  // FETCH JOBS
  // ---------------------------------------------

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_URL}/api/scraping-jobs/?page=1&limit=100`
      );

      const data =
        await response.json();

      if (!response.ok) {
        console.error(
          "Jobs API error:",
          data
        );

        setError(
          data.error ||
            "Unable to load scraping jobs."
        );

        return;
      }

      const results =
        data.results ||
        data.jobs ||
        [];

      setJobs(results);

      setTotalJobs(
        data.count ??
          data.total ??
          results.length
      );
    } catch (error) {
      console.error(
        "Jobs fetch error:",
        error
      );

      setError(
        "Unable to connect to backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();

    const interval =
      setInterval(
        fetchJobs,
        5000
      );

    return () =>
      clearInterval(interval);
  }, []);

  // ---------------------------------------------
  // GET JOB ID
  // ---------------------------------------------

  const getJobId = (job) => {
    return (
      job.id ??
      job.job_id ??
      job.scraping_job_id ??
      job.jobId ??
      "-"
    );
  };

  // ---------------------------------------------
  // FORMAT DATE
  // ---------------------------------------------

  const formatDate = (value) => {
    if (!value || value === "-") {
      return "-";
    }

    return String(value)
      .replace("T", " ")
      .split(".")[0];
  };

  // ---------------------------------------------
  // STATUS CLASS
  // ---------------------------------------------

  const getStatusClass = (
    jobStatus
  ) => {
    switch (
      String(jobStatus || "")
        .toLowerCase()
    ) {
      case "running":
        return "status-running";

      case "completed":
        return "status-completed";

      case "failed":
        return "status-failed";

      case "stopped":
        return "status-stopped";

      case "pending":
        return "status-pending";

      default:
        return "status-idle";
    }
  };

  return (
    <div className="page-container">

      {/* HEADER */}

      <div className="page-header">

        <div>
          <h1>
            Scraping Jobs
          </h1>

          <p>
            Manage and monitor Telegram
            scraping jobs.
          </p>
        </div>

        <button
          className="refresh-btn"
          onClick={fetchJobs}
          disabled={loading}
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>

      </div>

      {/* JOBS */}

      <section className="card">

        <div className="section-header">

          <div>
            <h2>
              Scraping Jobs
            </h2>

            <p>
              Total Jobs:{" "}
              <strong>
                {totalJobs}
              </strong>
            </p>
          </div>

        </div>

        {error && (

          <div className="error-message">
            {error}
          </div>

        )}

        <div className="table-container">

          <table>

            <thead>

              <tr>

                <th>
                  Job ID
                </th>

                <th>
                  Channel
                </th>

                <th>
                  Limit
                </th>

                <th>
                  Status
                </th>

                <th>
                  Started At
                </th>

                <th>
                  Completed At
                </th>

                <th>
                  Messages Scraped
                </th>

                <th>
                  Messages Saved
                </th>

              </tr>

            </thead>

            <tbody>

              {loading &&
              jobs.length === 0 ? (

                <tr>

                  <td
                    colSpan="8"
                    className="no-data"
                  >
                    Loading scraping
                    jobs...
                  </td>

                </tr>

              ) : jobs.length > 0 ? (

                jobs.map(
                  (job, index) => {

                    const jobId =
                      getJobId(job);

                    const jobStatus =
                      job.status ||
                      job.job_status ||
                      "pending";

                    const channel =
                      job.channel ||
                      job.channel_name ||
                      "-";

                    const limit =
                      job.limit ??
                      job.message_limit ??
                      "-";

                    const startedAt =
                      job.started_at ||
                      job.start_time ||
                      "-";

                    const completedAt =
                      job.completed_at ||
                      job.completed_time ||
                      "-";

                    const messagesScraped =
                      job.messages_scraped ??
                      job.scraped_count ??
                      0;

                    const messagesSaved =
                      job.messages_saved ??
                      job.saved_count ??
                      0;

                    return (

                      <tr
                        key={
                          `${jobId}-${index}`
                        }
                      >

                        <td>
                          <strong>
                            {jobId}
                          </strong>
                        </td>

                        <td>
                          {channel}
                        </td>

                        <td>
                          {limit}
                        </td>

                        <td>

                          <span
                            className={`status-badge ${getStatusClass(
                              jobStatus
                            )}`}
                          >
                            {jobStatus}
                          </span>

                        </td>

                        <td>
                          {formatDate(
                            startedAt
                          )}
                        </td>

                        <td>
                          {formatDate(
                            completedAt
                          )}
                        </td>

                        <td>
                          {messagesScraped}
                        </td>

                        <td>
                          {messagesSaved}
                        </td>

                      </tr>

                    );
                  }
                )

              ) : (

                <tr>

                  <td
                    colSpan="8"
                    className="no-data"
                  >
                    No scraping jobs
                    found.
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

      </section>

    </div>
  );
}

export default Jobs;