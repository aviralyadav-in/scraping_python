import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";

function App() {
  const [channel, setChannel] = useState("");
  const [limit, setLimit] = useState(10);

  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const [deals, setDeals] = useState([]);
  const [dealCount, setDealCount] = useState(0);
  const [dealPage, setDealPage] = useState(1);
  const [dealTotalPages, setDealTotalPages] = useState(1);

  const [filterChannel, setFilterChannel] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const [dealViewMode, setDealViewMode] = useState("latest");

  const [logs, setLogs] = useState([]);
  const [logPage, setLogPage] = useState(1);
  const [logCount, setLogCount] = useState(0);
  const [logTotalPages, setLogTotalPages] = useState(1);

  const [selectedDeals, setSelectedDeals] = useState([]);

  const [deleteConfirmation, setDeleteConfirmation] = useState(null);

  const [editDeal, setEditDeal] = useState(null);
  const [editContent, setEditContent] = useState("");
  const [editProductLink, setEditProductLink] = useState("");
  const [editImagePath, setEditImagePath] = useState("");
  const [editLoading, setEditLoading] = useState(false);

  const PAGE_LIMIT = 10;

  const fetchStatus = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/scrape/status/`
      );

      const data = await response.json();

      if (!response.ok) {
        console.error("Status API error:", data);
        return;
      }

      setStatus(data);
    } catch (error) {
      console.error("Status fetch error:", error);
      setStatus(null);
    }
  };

  const fetchDeals = async (page = dealPage) => {
    try {
      let displayLimit;

      if (dealViewMode === "latest") {
        const numericLimit = Number(limit);

        if (
          !Number.isInteger(numericLimit) ||
          numericLimit < 1 ||
          numericLimit > 100
        ) {
          displayLimit = 10;
        } else {
          displayLimit = numericLimit;
        }
      } else {
        displayLimit = PAGE_LIMIT;
      }

      let url =
        `${API_URL}/api/deals/?page=${page}&limit=${displayLimit}`;

      if (filterChannel.trim()) {
        url +=
          `&channel=${encodeURIComponent(
            filterChannel.trim()
          )}`;
      }

      if (fromDate) {
        url += `&from_date=${fromDate}`;
      }

      if (toDate) {
        url += `&to_date=${toDate}`;
      }

      const response = await fetch(url);

      const data = await response.json();

      if (!response.ok) {
        console.error("Deals API error:", data);
        return;
      }

      setDeals(data.results || []);
      setDealCount(data.count || 0);

      if (dealViewMode === "latest") {
        setDealTotalPages(1);
        setDealPage(1);
      } else {
        const totalPages = Math.max(
          1,
          Math.ceil(
            (data.count || 0) / PAGE_LIMIT
          )
        );

        setDealTotalPages(totalPages);

        if (page > totalPages) {
          setDealPage(totalPages);
        }
      }
    } catch (error) {
      console.error("Deals fetch error:", error);
    }
  };

  const fetchLogs = async (page = logPage) => {
    try {
      const response = await fetch(
        `${API_URL}/api/logs/?page=${page}&limit=${PAGE_LIMIT}`
      );

      const data = await response.json();

      if (!response.ok) {
        console.error("Logs API error:", data);
        return;
      }

      setLogs(data.results || []);
      setLogCount(data.count || 0);

      const totalPages = Math.max(
        1,
        Math.ceil(
          (data.count || 0) / PAGE_LIMIT
        )
      );

      setLogTotalPages(totalPages);

      if (page > totalPages) {
        setLogPage(totalPages);
      }
    } catch (error) {
      console.error("Logs fetch error:", error);
    }
  };

  const startScraping = async () => {
    if (!channel.trim()) {
      alert("Please enter channel name.");
      return;
    }

    const numericLimit = Number(limit);

    if (
      !Number.isInteger(numericLimit) ||
      numericLimit < 1 ||
      numericLimit > 100
    ) {
      alert("Limit must be an integer between 1 and 100.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/scrape/start/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            channel: channel.trim(),
            limit: numericLimit,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(
          data.error ||
          "Failed to start scraping."
        );
        return;
      }

      alert(
        data.message ||
        "Scraping started successfully."
      );

      setDealPage(1);
      setLogPage(1);

      await fetchStatus();
      await fetchDeals(1);
      await fetchLogs(1);
    } catch (error) {
      console.error(
        "Start scraping error:",
        error
      );

      alert(
        "Unable to connect to Flask backend. Make sure Flask is running on port 5000."
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
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      const data = await response.json();

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
      await fetchLogs(logPage);
    } catch (error) {
      console.error(
        "Stop scraping error:",
        error
      );

      alert(
        "Unable to connect to Flask backend. Make sure Flask is running."
      );
    }
  };

  const clearFilters = () => {
    setFilterChannel("");
    setFromDate("");
    setToDate("");
    setDealPage(1);
    setSelectedDeals([]);
   setDealViewMode("latest");

    // Force clear date inputs
    const dateInputs = document.querySelectorAll(
    '.filters input[type="date"]'
    );

    dateInputs.forEach((input) => {
    input.value = "";
   });
  };
  

  const selectLatestMode = () => {
    setDealViewMode("latest");
    setDealPage(1);
    setSelectedDeals([]);
  };

  const selectViewAllMode = () => {
    setDealViewMode("all");
    setDealPage(1);
    setSelectedDeals([]);
  };

  const goToDealPage = (page) => {
    if (
      dealViewMode !== "all"
    ) {
      return;
    }

    if (
      page < 1 ||
      page > dealTotalPages
    ) {
      return;
    }

    setDealPage(page);
    setSelectedDeals([]);

    fetchDeals(page);
  };

  const goToLogPage = (page) => {
    if (
      page < 1 ||
      page > logTotalPages
    ) {
      return;
    }

    setLogPage(page);

    fetchLogs(page);
  };

  useEffect(() => {
    fetchStatus();
    fetchDeals(1);
    fetchLogs(1);
  }, []);

  useEffect(() => {
    setDealPage(1);
    setSelectedDeals([]);

    fetchDeals(1);
  }, [
    filterChannel,
    fromDate,
    toDate,
    dealViewMode,
    limit,
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      fetchStatus();
      fetchDeals(dealViewMode === "latest" ? 1 : dealPage);
    }, 3000);

    return () => {
      clearInterval(interval);
    };
  }, [
    dealPage,
    filterChannel,
    fromDate,
    toDate,
    dealViewMode,
    limit,
  ]);

  const toggleDealSelection = (messageId) => {
    setSelectedDeals((previous) => {
      if (
        previous.includes(messageId)
      ) {
        return previous.filter(
          (id) =>
            id !== messageId
        );
      }

      return [
        ...previous,
        messageId,
      ];
    });
  };

  const toggleSelectAll = () => {
    const currentPageIds = deals.map(
      (deal) => deal.message_id
    );

    const allSelected =
      currentPageIds.length > 0 &&
      currentPageIds.every((id) =>
        selectedDeals.includes(id)
      );

    if (allSelected) {
      setSelectedDeals((previous) =>
        previous.filter(
          (id) =>
            !currentPageIds.includes(id)
        )
      );
    } else {
      setSelectedDeals((previous) => {
        const newIds =
          currentPageIds.filter(
            (id) =>
              !previous.includes(id)
          );

        return [
          ...previous,
          ...newIds,
        ];
      });
    }
  };

  const isAllCurrentPageSelected =
    deals.length > 0 &&
    deals.every((deal) =>
      selectedDeals.includes(
        deal.message_id
      )
    );

  const openDeleteConfirmation = (
    deal
  ) => {
    setDeleteConfirmation({
      type: "single",
      deal: deal,
    });
  };

  const openMultipleDeleteConfirmation =
    () => {
      if (
        selectedDeals.length === 0
      ) {
        alert(
          "Please select at least one deal to delete."
        );
        return;
      }

      setDeleteConfirmation({
        type: "multiple",
        count: selectedDeals.length,
      });
    };

  const closeDeleteConfirmation = () => {
    setDeleteConfirmation(null);
  };

  const deleteSingleDeal = async (
    deal
  ) => {
    try {
      const dealChannel = String(
        deal.channel || ""
      ).trim();

      if (!dealChannel) {
        alert(
          "Channel is missing for this deal."
        );
        return;
      }

      const response = await fetch(
        `${API_URL}/api/deals/${deal.message_id}/?channel=${encodeURIComponent(
          dealChannel
        )}`,
        {
          method: "DELETE",
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.error ||
          "Failed to delete deal."
        );
        return;
      }

      setSelectedDeals(
        (previous) =>
          previous.filter(
            (id) =>
              id !== deal.message_id
          )
      );

      closeDeleteConfirmation();

      await fetchDeals(
        dealViewMode === "latest"
          ? 1
          : dealPage
      );

      await fetchLogs(logPage);

      alert(
        data.message ||
        "Deal deleted successfully."
      );
    } catch (error) {
      console.error(
        "Delete deal error:",
        error
      );

      alert(
        "Unable to connect to Flask backend."
      );
    }
  };

  const deleteMultipleDeals = async () => {
    if (
      selectedDeals.length === 0
    ) {
      closeDeleteConfirmation();
      return;
    }

    try {
      const selectedDealObjects =
        deals.filter((deal) =>
          selectedDeals.includes(
            deal.message_id
          )
        );

      let deletedCount = 0;
      let failedCount = 0;

      for (
        const deal of selectedDealObjects
      ) {
        const dealChannel =
          String(
            deal.channel || ""
          ).trim();

        if (!dealChannel) {
          failedCount++;
          continue;
        }

        const response =
          await fetch(
            `${API_URL}/api/deals/${deal.message_id}/?channel=${encodeURIComponent(
              dealChannel
            )}`,
            {
              method: "DELETE",
            }
          );

        if (response.ok) {
          deletedCount++;
        } else {
          failedCount++;
        }
      }

      setSelectedDeals([]);

      closeDeleteConfirmation();

      await fetchDeals(
        dealViewMode === "latest"
          ? 1
          : dealPage
      );

      await fetchLogs(logPage);

      if (failedCount > 0) {
        alert(
          `${deletedCount} deal(s) deleted successfully. ${failedCount} deal(s) could not be deleted.`
        );
      } else {
        alert(
          `${deletedCount} deal(s) deleted successfully.`
        );
      }
    } catch (error) {
      console.error(
        "Multiple delete error:",
        error
      );

      alert(
        "Unable to connect to Flask backend."
      );
    }
  };

  const confirmDelete = async () => {
    if (!deleteConfirmation) {
      return;
    }

    if (
      deleteConfirmation.type ===
      "single"
    ) {
      await deleteSingleDeal(
        deleteConfirmation.deal
      );
    }

    if (
      deleteConfirmation.type ===
      "multiple"
    ) {
      await deleteMultipleDeals();
    }
  };

  const openEditModal = (deal) => {
    setEditDeal(deal);

    setEditContent(
      deal.content || ""
    );

    setEditProductLink(
      deal.product_link || ""
    );

    setEditImagePath(
      deal.image_path || ""
    );
  };

  const closeEditModal = () => {
    if (editLoading) {
      return;
    }

    setEditDeal(null);
    setEditContent("");
    setEditProductLink("");
    setEditImagePath("");
  };

  const updateDeal = async () => {
    if (!editDeal) {
      return;
    }

    if (!editContent.trim()) {
      alert(
        "Content cannot be empty."
      );
      return;
    }

    if (
      !editProductLink.trim()
    ) {
      alert(
        "Product link cannot be empty."
      );
      return;
    }

    const dealChannel = String(
      editDeal.channel || ""
    ).trim();

    if (!dealChannel) {
      alert(
        "Channel is missing for this deal."
      );
      return;
    }

    setEditLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/deals/${editDeal.message_id}/update/?channel=${encodeURIComponent(
          dealChannel
        )}`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            content:
              editContent.trim(),
            product_link:
              editProductLink.trim(),
            image_path:
              editImagePath.trim(),
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.error ||
          "Failed to update deal."
        );
        return;
      }

      closeEditModal();

      await fetchDeals(
        dealViewMode === "latest"
          ? 1
          : dealPage
      );

      await fetchLogs(logPage);

      alert(
        data.message ||
        "Deal updated successfully."
      );
    } catch (error) {
      console.error(
        "Update deal error:",
        error
      );

      alert(
        "Unable to connect to Flask backend."
      );
    } finally {
      setEditLoading(false);
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) {
      return "";
    }

    let cleanPath =
      String(imagePath)
        .replaceAll("\\", "/");

    cleanPath =
      cleanPath.replace(
        /^images\//,
        ""
      );

    return `${API_URL}/images/${cleanPath
      .split("/")
      .map((part) =>
        encodeURIComponent(part)
      )
      .join("/")}`;
  };

  return (
    <div className="app">

      <header className="header">
        <h1>
          Telegram Deals Scraper
        </h1>

        <p>
          Scraper Control Panel
        </p>
      </header>

      <section className="card">

        <h2>
          Scraper Control
        </h2>

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
            type="button"
            className="start-btn"
            onClick={startScraping}
            disabled={loading}
          >
            {loading
              ? "Starting..."
              : "Start Scraping"}
          </button>

          <button
            type="button"
            className="stop-btn"
            onClick={stopScraping}
          >
            Stop Scraping
          </button>

        </div>

      </section>

      <section className="card">

        <h2>
          Scraping Status
        </h2>

        {status ? (

          <div className="status-grid">

            <div>
              <strong>
                Status
              </strong>

              <span>
                {status.status || "-"}
              </span>
            </div>

            <div>
              <strong>
                Channel
              </strong>

              <span>
                {status.channel || "-"}
              </span>
            </div>

            <div>
              <strong>
                Limit
              </strong>

              <span>
                {status.limit ?? "-"}
              </span>
            </div>

            <div>
              <strong>
                Messages Scraped
              </strong>

              <span>
                {status.messages_scraped ?? 0}
              </span>
            </div>

            <div>
              <strong>
                Messages Saved
              </strong>

              <span>
                {status.messages_saved ?? 0}
              </span>
            </div>

            <div>
              <strong>
                Started At
              </strong>

              <span>
                {status.started_at || "-"}
              </span>
            </div>

            <div>
              <strong>
                Completed At
              </strong>

              <span>
                {status.completed_at || "-"}
              </span>
            </div>

            <div>
              <strong>
                Current Deal
              </strong>

              <span>
                {status.current_deal || "-"}
              </span>
            </div>

            <div>
              <strong>
                Stop Requested
              </strong>

              <span>
                {status.stop_requested
                  ? "Yes"
                  : "No"}
              </span>
            </div>

            <div>
              <strong>
                Error
              </strong>

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

      <section className="card">

        <div className="section-header">

          <div>

            <h2>
              All Scraped Deals
            </h2>

            <p>
              Total Deals:{" "}
              {dealCount}
            </p>

          </div>

          {selectedDeals.length > 0 && (

            <button
              type="button"
              className="delete-selected-btn"
              onClick={
                openMultipleDeleteConfirmation
              }
            >
              Delete Selected (
              {selectedDeals.length})
            </button>

          )}

        </div>

        <div className="filters">

          <div className="form-group">

            <label>
              Channel Filter
            </label>

            <input
              type="text"
              value={filterChannel}
              onChange={(e) =>
                setFilterChannel(
                  e.target.value
                )
              }
              placeholder="Channel name"
            />

          </div>

          <div className="form-group">

            <label>
              From Date
            </label>

            <input
              type="date"
              value={fromDate}
              onChange={(e) =>
                setFromDate(
                  e.target.value
                )
              }
            />

          </div>

          <div className="form-group">

            <label>
              To Date
            </label>

            <input
              
              type="date"
              value={toDate}
              onChange={(e) =>
                setToDate(
                  e.target.value
                )
              }
            />

          </div>

          <div className="filter-buttons">

            <button
              type="button"
              className={
                dealViewMode === "latest"
                  ? "view-mode-btn active"
                  : "view-mode-btn"
              }
              onClick={selectLatestMode}
            >
              Latest {limit}
            </button>

            <button
              type="button"
              className={
                dealViewMode === "all"
                  ? "view-mode-btn active"
                  : "view-mode-btn"
              }
              onClick={selectViewAllMode}
            >
              View All
            </button>

            <button
              type="button"
              className="clear-btn"
              onClick={clearFilters}
            >
              Clear Filters
            </button>

          </div>

        </div>

        <p className="deal-view-info">

          {dealViewMode === "latest"
            ? `Showing latest ${limit} matching deal(s), newest to oldest`
            : "Showing all matching deals, 10 deals per page, newest to oldest"}

        </p>

        <div className="table-container">

          <table>

            <thead>

              <tr>

                <th>
                  <input
                    type="checkbox"
                    checked={
                      isAllCurrentPageSelected
                    }
                    onChange={
                      toggleSelectAll
                    }
                  />
                </th>

                <th>
                  Message ID
                </th>

                <th>
                  Channel
                </th>

                <th>
                  Date
                </th>

                <th>
                  Content
                </th>

                <th>
                  Product Link
                </th>

                <th>
                  Image
                </th>

                <th>
                  Action
                </th>

              </tr>

            </thead>

            <tbody>

              {deals.length > 0 ? (

                deals.map((deal) => (

                  <tr
                    key={
                      deal.message_id
                    }
                  >

                    <td>

                      <input
                        type="checkbox"
                        checked={selectedDeals.includes(
                          deal.message_id
                        )}
                        onChange={() =>
                          toggleDealSelection(
                            deal.message_id
                          )
                        }
                      />

                    </td>

                    <td>
                      {deal.message_id}
                    </td>

                    <td>
                      {deal.channel || "-"}
                    </td>

                    <td>
                      {deal.date || "-"}
                    </td>

                    <td className="content-cell">
                      {deal.content || "-"}
                    </td>

                    <td>

                      {deal.product_link ? (

                        <a
                          href={
                            deal.product_link
                          }
                          target="_blank"
                          rel="noreferrer"
                        >
                          Open Link
                        </a>

                      ) : (
                        "-"
                      )}

                    </td>

                    <td>

                      {deal.image_path ? (

                        <img
                          src={getImageUrl(
                            deal.image_path
                          )}
                          alt="Product"
                          className="deal-image"
                          onError={(e) => {
                            e.currentTarget.style.display =
                              "none";
                          }}
                        />

                      ) : (
                        "-"
                      )}

                    </td>

                    <td>

                      <div className="action-buttons">

                        <button
                          type="button"
                          className="edit-btn"
                          onClick={() =>
                            openEditModal(
                              deal
                            )
                          }
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          className="delete-btn"
                          onClick={() =>
                            openDeleteConfirmation(
                              deal
                            )
                          }
                        >
                          Delete
                        </button>

                      </div>

                    </td>

                  </tr>

                ))

              ) : (

                <tr>

                  <td
                    colSpan="8"
                    className="no-data"
                  >
                    No deals found
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

        {dealViewMode === "all" &&
          dealCount > 0 && (

            <div className="pagination">

              <button
                type="button"
                onClick={() =>
                  goToDealPage(
                    dealPage - 1
                  )
                }
                disabled={
                  dealPage === 1
                }
              >
                Previous
              </button>

              <span>
                Page {dealPage} of{" "}
                {dealTotalPages}
              </span>

              <button
                type="button"
                onClick={() =>
                  goToDealPage(
                    dealPage + 1
                  )
                }
                disabled={
                  dealPage ===
                  dealTotalPages
                }
              >
                Next
              </button>

            </div>

          )}

      </section>

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

                <th>
                  Time
                </th>

                <th>
                  Status
                </th>

                <th>
                  Message
                </th>

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
              type="button"
              onClick={() =>
                goToLogPage(
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
              type="button"
              onClick={() =>
                goToLogPage(
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

      {deleteConfirmation && (

        <div className="confirmation-overlay">

          <div className="confirmation-popup">

            <h3>
              Confirm Delete
            </h3>

            {deleteConfirmation.type ===
            "single" ? (

              <p>
                Are you sure you want
                to delete this deal?
              </p>

            ) : (

              <p>
                Are you sure you want
                to delete{" "}
                <strong>
                  {
                    deleteConfirmation.count
                  }
                </strong>{" "}
                selected deal(s)?
              </p>

            )}

            <div className="confirmation-buttons">

              <button
                type="button"
                className="cancel-delete-btn"
                onClick={
                  closeDeleteConfirmation
                }
              >
                No
              </button>

              <button
                type="button"
                className="confirm-delete-btn"
                onClick={
                  confirmDelete
                }
              >
                Yes, Delete
              </button>

            </div>

          </div>

        </div>

      )}

      {editDeal && (

        <div className="confirmation-overlay">

          <div className="edit-modal">

            <h2>
              Edit Deal
            </h2>

            <div className="form-group">

              <label>
                Message ID
              </label>

              <input
                type="text"
                value={
                  editDeal.message_id
                }
                disabled
              />

            </div>

            <div className="form-group">

              <label>
                Channel
              </label>

              <input
                type="text"
                value={
                  editDeal.channel ||
                  ""
                }
                disabled
              />

            </div>

            <div className="form-group">

              <label>
                Content
              </label>

              <textarea
                value={editContent}
                onChange={(e) =>
                  setEditContent(
                    e.target.value
                  )
                }
                rows="8"
              />

            </div>

            <div className="form-group">

              <label>
                Product Link
              </label>

              <input
                type="text"
                value={
                  editProductLink
                }
                onChange={(e) =>
                  setEditProductLink(
                    e.target.value
                  )
                }
              />

            </div>

            <div className="form-group">

              <label>
                Image Path
              </label>

              <input
                type="text"
                value={
                  editImagePath
                }
                onChange={(e) =>
                  setEditImagePath(
                    e.target.value
                  )
                }
              />

            </div>

            <div className="confirmation-buttons">

              <button
                type="button"
                className="cancel-delete-btn"
                onClick={
                  closeEditModal
                }
                disabled={
                  editLoading
                }
              >
                Cancel
              </button>

              <button
                type="button"
                className="save-btn"
                onClick={
                  updateDeal
                }
                disabled={
                  editLoading
                }
              >
                {editLoading
                  ? "Saving..."
                  : "Save Changes"}
              </button>

            </div>

          </div>

        </div>

      )}

    </div>
  );
}

export default App;