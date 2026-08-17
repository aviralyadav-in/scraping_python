import { useCallback, useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:5000";
const PAGE_LIMIT = 10;

function Deals({ currentUser }) {

  const isAdmin = currentUser?.role === "admin";

  const [deals, setDeals] = useState([]);
  const [dealCount, setDealCount] = useState(0);

  const [dealPage, setDealPage] = useState(1);
  const [dealTotalPages, setDealTotalPages] = useState(1);

  const [filterChannel, setFilterChannel] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const [dealViewMode, setDealViewMode] = useState("latest");

  const [selectedDeals, setSelectedDeals] = useState([]);

  const [loading, setLoading] = useState(false);

  const [deleteConfirmation, setDeleteConfirmation] =
    useState(null);

  const [editDeal, setEditDeal] = useState(null);

  const [editContent, setEditContent] = useState("");
  const [editProductLink, setEditProductLink] = useState("");
  const [editImagePath, setEditImagePath] = useState("");

  const [editLoading, setEditLoading] = useState(false);

  const [bulkUpdateMode, setBulkUpdateMode] = useState(false);

  const [bulkEdits, setBulkEdits] = useState({});

  const [sameBulkUpdateMode, setSameBulkUpdateMode] =
    useState(false);

  const [sameBulkContent, setSameBulkContent] =
    useState("");

  const [sameBulkProductLink, setSameBulkProductLink] =
    useState("");

  const [sameBulkImagePath, setSameBulkImagePath] =
    useState("");

  const [sameBulkStatus, setSameBulkStatus] =
    useState("");

  const fetchDeals = useCallback(
    async (page = 1) => {
      try {
        setLoading(true);

        const displayLimit =
          dealViewMode === "latest"
            ? 10
            : PAGE_LIMIT;

        let url =
          `${API_URL}/api/deals/?page=${page}&limit=${displayLimit}`;

        const channel = filterChannel.trim();

        if (channel) {
          url +=
            `&channel=${encodeURIComponent(channel)}`;
        }

        const completeFromDate =
          /^\d{4}-\d{2}-\d{2}$/.test(fromDate)
            ? fromDate
            : "";

        const completeToDate =
          /^\d{4}-\d{2}-\d{2}$/.test(toDate)
            ? toDate
            : "";

        if (completeFromDate) {
          url +=
            `&from_date=${completeFromDate}`;
        }

        if (completeToDate) {
          url +=
            `&to_date=${completeToDate}`;
        }

        const response = await fetch(url);

        const data = await response.json();

        if (!response.ok) {
          console.error(
            "Deals API error:",
            data
          );
          return;
        }

        setDeals(data.results || []);

        setDealCount(
          Number(data.count || 0)
        );

        if (dealViewMode === "latest") {
          setDealTotalPages(1);
          setDealPage(1);
        } else {
          const totalPages = Math.max(
            1,
            Math.ceil(
              Number(data.count || 0) /
                PAGE_LIMIT
            )
          );

          setDealTotalPages(totalPages);
        }
      } catch (error) {
        console.error(
          "Deals fetch error:",
          error
        );
      } finally {
        setLoading(false);
      }
    },
    [
      filterChannel,
      fromDate,
      toDate,
      dealViewMode,
    ]
  );

  useEffect(() => {
    setDealPage(1);
    setSelectedDeals([]);

    fetchDeals(1);
  }, [
    filterChannel,
    fromDate,
    toDate,
    dealViewMode,
    fetchDeals,
  ]);

  const toggleDealSelection = (messageId) => {
    setSelectedDeals((previous) => {
      if (previous.includes(messageId)) {
        return previous.filter(
          (id) => id !== messageId
        );
      }

      return [
        ...previous,
        messageId,
      ];
    });
  };

  const toggleSelectAll = () => {
    const ids = deals.map(
      (deal) => deal.message_id
    );

    const allSelected =
      ids.length > 0 &&
      ids.every((id) =>
        selectedDeals.includes(id)
      );

    if (allSelected) {
      setSelectedDeals((previous) =>
        previous.filter(
          (id) => !ids.includes(id)
        )
      );
    } else {
      setSelectedDeals((previous) => [
        ...previous,
        ...ids.filter(
          (id) => !previous.includes(id)
        ),
      ]);
    }
  };

  const deleteSingleDeal = async (deal) => {
    const channel = String(
      deal.channel || ""
    ).trim();

    if (!channel) {
      alert("Channel is missing.");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        `${API_URL}/api/deals/${deal.message_id}/?channel=${encodeURIComponent(
          channel
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
            "Delete failed."
        );
        return;
      }

      setDeleteConfirmation(null);

      setSelectedDeals((previous) =>
        previous.filter(
          (id) =>
            id !== deal.message_id
        )
      );

      await fetchDeals(
        dealViewMode === "latest"
          ? 1
          : dealPage
      );

      alert(
        data.message ||
          "Deal deleted successfully."
      );
    } catch (error) {
      console.error(
        "Delete error:",
        error
      );

      alert(
        "Unable to connect to backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const deleteMultipleDeals = async () => {
    if (
      selectedDeals.length === 0
    ) {
      setDeleteConfirmation(null);
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        `${API_URL}/api/deals/bulk-delete/`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            message_ids:
              selectedDeals,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.error ||
            "Bulk delete failed."
        );
        return;
      }

      setSelectedDeals([]);

      setDeleteConfirmation(null);

      await fetchDeals(
        dealViewMode === "latest"
          ? 1
          : dealPage
      );

      alert(
        data.message ||
          "Selected deals deleted successfully."
      );
    } catch (error) {
      console.error(
        "Bulk delete error:",
        error
      );

      alert(
        "Unable to connect to backend."
      );
    } finally {
      setLoading(false);
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

    const channel = String(
      editDeal.channel || ""
    ).trim();

    if (!channel) {
      alert("Channel is missing.");
      return;
    }

    setEditLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/deals/${editDeal.message_id}/update/?channel=${encodeURIComponent(
          channel
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
            "Update failed."
        );
        return;
      }

      closeEditModal();

      await fetchDeals(
        dealViewMode === "latest"
          ? 1
          : dealPage
      );

      alert(
        data.message ||
          "Deal updated successfully."
      );
    } catch (error) {
      console.error(
        "Update error:",
        error
      );

      alert(
        "Unable to connect to backend."
      );
    } finally {
      setEditLoading(false);
    }
  };

  const startBulkUpdate = () => {
    if (
      selectedDeals.length === 0
    ) {
      alert(
        "Select at least one deal first."
      );
      return;
    }

    const initialValues = {};

    deals
      .filter((deal) =>
        selectedDeals.includes(
          deal.message_id
        )
      )
      .forEach((deal) => {
        initialValues[
          deal.message_id
        ] = {
          content:
            deal.content || "",

          product_link:
            deal.product_link || "",

          image_path:
            deal.image_path || "",

          status:
            deal.status || "",
        };
      });

    setBulkEdits(initialValues);

    setBulkUpdateMode(true);
  };

  const closeBulkUpdate = () => {
    if (loading) {
      return;
    }

    setBulkUpdateMode(false);
    setBulkEdits({});
  };

  const updateBulkField = (
    messageId,
    field,
    value
  ) => {
    setBulkEdits((previous) => ({
      ...previous,

      [messageId]: {
        ...(previous[messageId] || {}),
        [field]: value,
      },
    }));
  };

  const saveBulkUpdates = async () => {
    const ids =
      Object.keys(bulkEdits);

    if (ids.length === 0) {
      setBulkUpdateMode(false);
      return;
    }

    try {
      setLoading(true);

      for (const messageId of ids) {
        const deal = deals.find(
          (item) =>
            String(
              item.message_id
            ) ===
            String(messageId)
        );

        if (!deal) {
          continue;
        }

        const values =
          bulkEdits[messageId] || {};

        const channel = String(
          deal.channel || ""
        ).trim();

        if (!channel) {
          continue;
        }

        const updateResponse =
          await fetch(
            `${API_URL}/api/deals/${messageId}/update/?channel=${encodeURIComponent(
              channel
            )}`,
            {
              method: "POST",
              headers: {
                "Content-Type":
                  "application/json",
              },
              body: JSON.stringify({
                content:
                  values.content || "",

                product_link:
                  values.product_link ||
                  "",

                image_path:
                  values.image_path ||
                  "",
              }),
            }
          );

        if (!updateResponse.ok) {
          const errorData =
            await updateResponse.json();

          throw new Error(
            errorData.error ||
              `Failed to update deal ${messageId}`
          );
        }

        if (
          values.status &&
          values.status !==
            deal.status
        ) {
          const statusResponse =
            await fetch(
              `${API_URL}/api/deals/${messageId}/status/?channel=${encodeURIComponent(
                channel
              )}`,
              {
                method: "POST",
                headers: {
                  "Content-Type":
                    "application/json",
                },
                body: JSON.stringify({
                  status:
                    values.status,
                }),
              }
            );

          if (!statusResponse.ok) {
            const errorData =
              await statusResponse.json();

            throw new Error(
              errorData.error ||
                `Failed to update status for deal ${messageId}`
            );
          }
        }
      }

      setBulkUpdateMode(false);
      setBulkEdits({});
      setSelectedDeals([]);

      await fetchDeals(
        dealViewMode === "latest"
          ? 1
          : dealPage
      );

      alert(
        "All selected deal changes saved successfully."
      );
    } catch (error) {
      console.error(
        "Bulk update error:",
        error
      );

      alert(
        error.message ||
          "Bulk update failed."
      );
    } finally {
      setLoading(false);
    }
  };

  const startSameBulkUpdate = () => {
    if (
      selectedDeals.length === 0
    ) {
      alert(
        "Select at least one deal first."
      );
      return;
    }

    setSameBulkContent("");
    setSameBulkProductLink("");
    setSameBulkImagePath("");
    setSameBulkStatus("");

    setSameBulkUpdateMode(true);
  };

  const closeSameBulkUpdate = () => {
    if (loading) {
      return;
    }

    setSameBulkUpdateMode(false);

    setSameBulkContent("");
    setSameBulkProductLink("");
    setSameBulkImagePath("");
    setSameBulkStatus("");
  };

  const saveSameBulkUpdate = async () => {
    if (
      selectedDeals.length === 0
    ) {
      alert(
        "No deals selected."
      );
      return;
    }

    if (
      !sameBulkContent.trim()
    ) {
      alert(
        "Content cannot be empty."
      );
      return;
    }

    try {
      setLoading(true);

      const selectedCount =
        selectedDeals.length;

      const payload = {
        message_ids: selectedDeals,
        content:
          sameBulkContent.trim(),
        product_link:
          sameBulkProductLink.trim(),
        image_path:
          sameBulkImagePath.trim(),
      };

      if (sameBulkStatus) {
        payload.status =
          sameBulkStatus;
      }

      const response = await fetch(
        `${API_URL}/api/deals/bulk-update/`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(
            payload
          ),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        alert(
          data.error ||
            "Bulk update failed."
        );
        return;
      }

      closeSameBulkUpdate();

      setSelectedDeals([]);

      await fetchDeals(
        dealViewMode === "latest"
          ? 1
          : dealPage
      );

      alert(
        data.message ||
          `${selectedCount} selected deals updated successfully with the same data.`
      );
    } catch (error) {
      console.error(
        "Same data bulk update error:",
        error
      );

      alert(
        error.message ||
          "Bulk update failed."
      );
    } finally {
      setLoading(false);
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) {
      return "";
    }

    let cleanPath = String(
      imagePath
    ).replaceAll("\\", "/");

    cleanPath =
      cleanPath.replace(
        /^images\//,
        ""
      );

    return (
      `${API_URL}/images/` +
      cleanPath
        .split("/")
        .map((part) =>
          encodeURIComponent(part)
        )
        .join("/")
    );
  };

  const goToPage = (page) => {
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

  const clearFilters = () => {
    setFilterChannel("");
    setFromDate("");
    setToDate("");

    setDealViewMode("latest");
    setDealPage(1);

    setSelectedDeals([]);
  };

  const allSelected =
    deals.length > 0 &&
    deals.every((deal) =>
      selectedDeals.includes(
        deal.message_id
      )
    );

  // ESC KEY CLOSE FOR UPDATE MODALS
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key !== "Escape") {
        return;
      }

      if (editDeal && !editLoading) {
        closeEditModal();
        return;
      }

      if (
        sameBulkUpdateMode &&
        !loading
      ) {
        closeSameBulkUpdate();
        return;
      }

      if (
        bulkUpdateMode &&
        !loading
      ) {
        closeBulkUpdate();
      }
    };

    document.addEventListener(
      "keydown",
      handleEscape
    );

    return () => {
      document.removeEventListener(
        "keydown",
        handleEscape
      );
    };
  }, [
    editDeal,
    editLoading,
    sameBulkUpdateMode,
    bulkUpdateMode,
    loading,
  ]);

  return (
    <div className="page-container">

      <div className="page-header">

        <div>
          <h1>Deals</h1>

          <p>
            Manage all scraped Telegram
            deals.
          </p>
        </div>

        <button
          className="refresh-btn"
          onClick={() =>
            fetchDeals(
              dealViewMode ===
                "latest"
                ? 1
                : dealPage
            )
          }
          disabled={loading}
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>

      </div>

      <section className="card">

        <div className="section-header">

          <div>
            <h2>
              All Scraped Deals
            </h2>

            <p>
              Total Deals:{" "}
              <strong>
                {dealCount}
              </strong>
            </p>
          </div>

          <div
            style={{
              display: "flex",
              gap: "10px",
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >

            {isAdmin && selectedDeals.length >
              0 && (
              <>

                <button
                  className="edit-btn"
                  onClick={
                    startBulkUpdate
                  }
                >
                  Bulk Update (
                  {
                    selectedDeals.length
                  }
                  )
                </button>

                <button
                  className="save-btn"
                  onClick={
                    startSameBulkUpdate
                  }
                >
                  Apply Same Update (
                  {
                    selectedDeals.length
                  }
                  )
                </button>

                <button
                  className="delete-selected-btn"
                  onClick={() =>
                    setDeleteConfirmation(
                      {
                        type:
                          "multiple",
                        count:
                          selectedDeals.length,
                      }
                    )
                  }
                >
                  Delete Selected (
                  {
                    selectedDeals.length
                  }
                  )
                </button>

              </>
            )}

          </div>

        </div>

        <div className="filters">

          <div className="form-group">

            <label>
              Channel Filter
            </label>

            <input
              type="text"
              value={
                filterChannel
              }
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

        </div>

        <div className="filter-buttons">

          <button
            className={
              dealViewMode ===
              "latest"
                ? "view-mode-btn active"
                : "view-mode-btn"
            }
            onClick={() => {
              setDealViewMode(
                "latest"
              );
              setDealPage(1);
            }}
          >
            Latest 10
          </button>

          <button
            className={
              dealViewMode ===
              "all"
                ? "view-mode-btn active"
                : "view-mode-btn"
            }
            onClick={() => {
              setDealViewMode(
                "all"
              );
              setDealPage(1);
            }}
          >
            View All
          </button>

          <button
            type="button"
            className="clear-btn"
            onClick={
              clearFilters
            }
          >
            Clear Filters
          </button>

        </div>

        <p className="deal-view-info">

          {dealViewMode ===
          "latest"
            ? "Showing latest 10 matching deal(s), newest to oldest"
            : "Showing all matching deals, 10 deals per page, newest to oldest"}

        </p>

        <div className="table-container">

          <table>

            <thead>

              <tr>
              {isAdmin && (
                <th>
                  <input
                    type="checkbox"
                    checked={
                      allSelected
                    }
                    onChange={
                      toggleSelectAll
                    }
                  />
                </th>
              )}

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
                  Status
                </th>
                {isAdmin && (
                <th>
                  Action
                </th>
                
               )}              </tr>

            </thead>

            <tbody>

              {loading &&
              deals.length ===
                0 ? (

                <tr>

                  <td
                    colSpan="9"
                    className="no-data"
                  >
                    Loading deals...
                  </td>

                </tr>

              ) : deals.length >
                0 ? (

                deals.map(
                  (deal) => (

                    <tr
                      key={
                        `${deal.channel}-${deal.message_id}`
                      }
                    >

                    {isAdmin && (
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
                    )}

                      <td>
                        {deal.message_id ||
                          "-"}
                      </td>

                      <td>
                        {deal.channel ||
                          "-"}
                      </td>

                      <td>
                        {deal.date ||
                          "-"}
                      </td>

                      <td className="content-cell">
                        {deal.content ||
                          "-"}
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
                          />

                        ) : (
                          "-"
                        )}

                      </td>

                      <td>

                        <span className="status-badge">
                          {deal.status ||
                            "N/A"}
                        </span>

                      </td>
                      {isAdmin && (
                      <td>

                        <div className="action-buttons">

                          <button
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
                            className="delete-btn"
                            onClick={() =>
                              setDeleteConfirmation(
                                {
                                  type:
                                    "single",
                                  deal,
                                }
                              )
                            }
                          >
                            Delete
                          </button>

                        </div>

                      </td>
                      )}
                    </tr>

                  )
                )

              ) : (

                <tr>

                  <td
                    colSpan={isAdmin ? 9 : 7}
                    className="no-data"
                  >
                    No deals found
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

        {dealViewMode ===
          "all" &&
          dealCount > 0 && (

            <div className="pagination">

              <button
                onClick={() =>
                  goToPage(
                    dealPage - 1
                  )
                }
                disabled={
                  dealPage === 1 ||
                  loading
                }
              >
                Previous
              </button>

              <span>
                Page{" "}
                {dealPage} of{" "}
                {
                  dealTotalPages
                }
              </span>

              <button
                onClick={() =>
                  goToPage(
                    dealPage + 1
                  )
                }
                disabled={
                  dealPage ===
                    dealTotalPages ||
                  loading
                }
              >
                Next
              </button>

            </div>

          )}

      </section>

      {/* ==================================================
          APPLY SAME UPDATE MODAL
      ================================================== */}

      {sameBulkUpdateMode && (

        <div
          className="confirmation-overlay"
          onMouseDown={(e) => {
            if (
              e.target === e.currentTarget &&
              !loading
            ) {
              closeSameBulkUpdate();
            }
          }}
        >

          <div
            className="edit-modal"
            onMouseDown={(e) =>
              e.stopPropagation()
            }
            style={{
              width: "95%",
              maxWidth: "720px",
              maxHeight: "90vh",
              overflowY: "auto",
              padding: "28px",
            }}
          >

            <div
              style={{
                display: "flex",
                justifyContent:
                  "space-between",
                alignItems: "flex-start",
                gap: "20px",
                marginBottom: "24px",
                paddingBottom: "18px",
                borderBottom:
                  "1px solid #e5e7eb",
              }}
            >

              <div>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    marginBottom: "7px",
                  }}
                >

                  <h2
                    style={{
                      margin: 0,
                    }}
                  >
                    Apply Same Update
                  </h2>

                  <span
                    style={{
                      background:
                        "#e8f0fe",
                      color:
                        "#2563eb",
                      padding:
                        "5px 10px",
                      borderRadius:
                        "20px",
                      fontSize:
                        "12px",
                      fontWeight:
                        "600",
                    }}
                  >
                    {
                      selectedDeals.length
                    }{" "}
                    Selected
                  </span>

                </div>

                <p
                  style={{
                    margin: 0,
                    color: "#6b7280",
                    fontSize: "14px",
                  }}
                >
                  Apply the same information
                  to all selected deals.
                </p>

              </div>

              <button
                type="button"
                onClick={
                  closeSameBulkUpdate
                }
                disabled={loading}
                title="Close"
                style={{
                  width: "36px",
                  height: "36px",
                  border: "none",
                  borderRadius: "8px",
                  background:
                    "#f3f4f6",
                  color: "#374151",
                  fontSize: "20px",
                  cursor: loading
                    ? "not-allowed"
                    : "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent:
                    "center",
                  flexShrink: 0,
                }}
              >
                ×
              </button>

            </div>

            <div
              style={{
                background: "#f8fafc",
                border:
                  "1px solid #e2e8f0",
                borderRadius: "10px",
                padding: "16px",
                marginBottom: "22px",
              }}
            >

              <div
                style={{
                  fontSize: "13px",
                  fontWeight: "600",
                  color: "#475569",
                  marginBottom: "10px",
                }}
              >
                Selected Message IDs
              </div>

              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "7px",
                  maxHeight: "90px",
                  overflowY: "auto",
                }}
              >

                {selectedDeals.map(
                  (id) => (
                    <span
                      key={id}
                      style={{
                        background:
                          "#e2e8f0",
                        color:
                          "#334155",
                        padding:
                          "5px 9px",
                        borderRadius:
                          "6px",
                        fontSize:
                          "12px",
                      }}
                    >
                      {id}
                    </span>
                  )
                )}

              </div>

            </div>

            <div className="form-group">

              <label>
                Common Content
              </label>

              <textarea
                rows="7"
                value={
                  sameBulkContent
                }
                onChange={(e) =>
                  setSameBulkContent(
                    e.target.value
                  )
                }
                placeholder="Enter the same content for all selected deals..."
              />

            </div>

            <div className="form-group">

              <label>
                Common Product Link
              </label>

              <input
                type="text"
                value={
                  sameBulkProductLink
                }
                onChange={(e) =>
                  setSameBulkProductLink(
                    e.target.value
                  )
                }
                placeholder="https://..."
              />

            </div>

            <div className="form-group">

              <label>
                Common Image Path
              </label>

              <input
                type="text"
                value={
                  sameBulkImagePath
                }
                onChange={(e) =>
                  setSameBulkImagePath(
                    e.target.value
                  )
                }
                placeholder="images/product.jpg"
              />

            </div>

            <div className="form-group">

              <label>
                Common Status
              </label>

              <select
                value={
                  sameBulkStatus
                }
                onChange={(e) =>
                  setSameBulkStatus(
                    e.target.value
                  )
                }
              >

                <option value="">
                  Keep Current Status
                </option>
                 
                 <option value="new">
                  New
                </option>

                <option value="processed">
                  Processed
                </option>

                <option value="published">
                  Published
                </option>

                <option value="expired">
                  Expired
                </option>

                <option value="rejected">
                  Rejected
                </option>
               
              </select>

            </div>

            <div
              style={{
                background:
                  "#fff7ed",
                border:
                  "1px solid #fed7aa",
                color: "#9a3412",
                borderRadius: "8px",
                padding: "12px 14px",
                marginTop: "16px",
                fontSize: "13px",
              }}
            >

              <strong>
                Important:
              </strong>{" "}
              This will apply the entered
              data to all{" "}
              <strong>
                {selectedDeals.length}
              </strong>{" "}
              selected deals.

            </div>

            <div
              className="confirmation-buttons"
              style={{
                marginTop: "25px",
                paddingTop: "18px",
                borderTop:
                  "1px solid #e5e7eb",
              }}
            >

              <button
                className="cancel-delete-btn"
                onClick={
                  closeSameBulkUpdate
                }
                disabled={loading}
              >
                Cancel
              </button>

              <button
                className="save-btn"
                onClick={
                  saveSameBulkUpdate
                }
                disabled={loading}
              >
                {loading
                  ? "Updating..."
                  : `Apply to ${selectedDeals.length} Deals`}
              </button>

            </div>

          </div>

        </div>

      )}

      {/* ==================================================
          BULK UPDATE MODAL
      ================================================== */}

      {bulkUpdateMode && (

        <div
          className="confirmation-overlay"
          onMouseDown={(e) => {
            if (
              e.target === e.currentTarget &&
              !loading
            ) {
              closeBulkUpdate();
            }
          }}
        >

          <div
            className="edit-modal"
            onMouseDown={(e) =>
              e.stopPropagation()
            }
            style={{
              width: "96%",
              maxWidth: "1200px",
              maxHeight: "90vh",
              overflowY: "auto",
              padding: "28px",
            }}
          >

            <div
              style={{
                display: "flex",
                justifyContent:
                  "space-between",
                alignItems: "flex-start",
                gap: "20px",
                marginBottom: "24px",
                paddingBottom: "18px",
                borderBottom:
                  "1px solid #e5e7eb",
              }}
            >

              <div>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    marginBottom: "7px",
                  }}
                >

                  <h2
                    style={{
                      margin: 0,
                    }}
                  >
                    Bulk Update Deals
                  </h2>

                  <span
                    style={{
                      background:
                        "#e8f0fe",
                      color:
                        "#2563eb",
                      padding:
                        "5px 10px",
                      borderRadius:
                        "20px",
                      fontSize:
                        "12px",
                      fontWeight:
                        "600",
                    }}
                  >
                    {
                      selectedDeals.length
                    }{" "}
                    Selected
                  </span>

                </div>

                <p
                  style={{
                    margin: 0,
                    color: "#6b7280",
                    fontSize: "14px",
                  }}
                >
                  Edit each selected deal
                  independently.
                </p>

              </div>

              <button
                type="button"
                onClick={
                  closeBulkUpdate
                }
                disabled={loading}
                title="Close"
                style={{
                  width: "36px",
                  height: "36px",
                  border: "none",
                  borderRadius: "8px",
                  background:
                    "#f3f4f6",
                  color: "#374151",
                  fontSize: "20px",
                  cursor: loading
                    ? "not-allowed"
                    : "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent:
                    "center",
                  flexShrink: 0,
                }}
              >
                ×
              </button>

            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "16px",
              }}
            >

              {selectedDeals.map(
                (messageId, index) => {

                  const deal =
                    deals.find(
                      (item) =>
                        String(
                          item.message_id
                        ) ===
                        String(
                          messageId
                        )
                    );

                  if (!deal) {
                    return null;
                  }

                  const values =
                    bulkEdits[
                      messageId
                    ] || {};

                  return (

                    <div
                      key={
                        messageId
                      }
                      style={{
                        border:
                          "1px solid #e2e8f0",
                        borderRadius:
                          "12px",
                        padding:
                          "20px",
                        background:
                          "#f8fafc",
                      }}
                    >

                      <div
                        style={{
                          display:
                            "flex",
                          justifyContent:
                            "space-between",
                          alignItems:
                            "center",
                          marginBottom:
                            "18px",
                          paddingBottom:
                            "12px",
                          borderBottom:
                            "1px solid #e2e8f0",
                        }}
                      >

                        <div>

                          <strong
                            style={{
                              fontSize:
                                "15px",
                            }}
                          >
                            Deal #
                            {index +
                              1}
                          </strong>

                          <div
                            style={{
                              marginTop:
                                "5px",
                              fontSize:
                                "12px",
                              color:
                                "#64748b",
                            }}
                          >
                            Message ID:{" "}
                            {
                              deal.message_id
                            }
                          </div>

                        </div>

                        <span
                          style={{
                            background:
                              "#e8f0fe",
                            color:
                              "#2563eb",
                            padding:
                              "6px 12px",
                            borderRadius:
                              "20px",
                            fontSize:
                              "12px",
                            fontWeight:
                              "600",
                          }}
                        >
                          {
                            deal.channel ||
                            "Unknown Channel"
                          }
                        </span>

                      </div>

                      <div
                        style={{
                          display:
                            "grid",
                          gridTemplateColumns:
                            "repeat(2, minmax(0, 1fr))",
                          gap: "18px",
                        }}
                      >

                        <div
                          className="form-group"
                          style={{
                            gridColumn:
                              "1 / -1",
                          }}
                        >

                          <label>
                            Content
                          </label>

                          <textarea
                            rows="5"
                            value={
                              values.content ||
                              ""
                            }
                            onChange={(
                              e
                            ) =>
                              updateBulkField(
                                messageId,
                                "content",
                                e
                                  .target
                                  .value
                              )
                            }
                            placeholder="Enter deal content..."
                            style={{
                              width:
                                "100%",
                              resize:
                                "vertical",
                            }}
                          />

                        </div>

                        <div className="form-group">

                          <label>
                            Product Link
                          </label>

                          <input
                            type="text"
                            value={
                              values.product_link ||
                              ""
                            }
                            onChange={(
                              e
                            ) =>
                              updateBulkField(
                                messageId,
                                "product_link",
                                e
                                  .target
                                  .value
                              )
                            }
                            placeholder="https://..."
                          />

                        </div>

                        <div className="form-group">

                          <label>
                            Image Path
                          </label>

                          <input
                            type="text"
                            value={
                              values.image_path ||
                              ""
                            }
                            onChange={(
                              e
                            ) =>
                              updateBulkField(
                                messageId,
                                "image_path",
                                e
                                  .target
                                  .value
                              )
                            }
                            placeholder="images/product.jpg"
                          />

                        </div>

                        <div className="form-group">

                          <label>
                            Status
                          </label>

                          <select
                            value={
                              values.status ||
                              ""
                            }
                            onChange={(
                              e
                            ) =>
                              updateBulkField(
                                messageId,
                                "status",
                                e
                                  .target
                                  .value
                              )
                            }
                          >

                            <option value="">
                              Keep Current status
                            </option>

                            <option value="new">
                              New
                            </option>

                            <option value="processed">
                              Processed
                            </option>
                            <option value="published">
                              Published
                            </option>

                            <option value="expired">
                              Expired
                            </option>

                            <option value="rejected">
                              Rejected
                            </option>
                                                    
                          </select>

                        </div>

                        <div
                          style={{
                            display:
                              "flex",
                            alignItems:
                              "center",
                            gap: "8px",
                            paddingTop:
                              "25px",
                          }}
                        >

                          <span
                            style={{
                              fontSize:
                                "13px",
                              color:
                                "#64748b",
                            }}
                          >
                            Current:
                          </span>

                          <strong>
                            {deal.status ||
                              "N/A"}
                          </strong>

                        </div>

                      </div>

                    </div>

                  );
                }
              )}

            </div>

            <div
              className="confirmation-buttons"
              style={{
                marginTop: "24px",
                paddingTop: "20px",
                borderTop:
                  "1px solid #e5e7eb",
              }}
            >

              <button
                className="cancel-delete-btn"
                onClick={
                  closeBulkUpdate
                }
                disabled={loading}
              >
                Cancel
              </button>

              <button
                className="save-btn"
                onClick={
                  saveBulkUpdates
                }
                disabled={loading}
              >
                {loading
                  ? "Saving Changes..."
                  : "Save All Changes"}
              </button>

            </div>

          </div>

        </div>

      )}

      {/* ==================================================
          DELETE CONFIRMATION
      ================================================== */}

      {deleteConfirmation && (

        <div className="confirmation-overlay">

          <div className="confirmation-popup">

            <h3>
              Confirm Delete
            </h3>

            <p>

              {deleteConfirmation.type ===
              "single"
                ? "Are you sure you want to delete this deal?"
                : `Are you sure you want to delete ${deleteConfirmation.count} selected deal(s)?`}

            </p>

            <div className="confirmation-buttons">

              <button
                className="cancel-delete-btn"
                onClick={() =>
                  setDeleteConfirmation(
                    null
                  )
                }
              >
                No
              </button>

              <button
                className="confirm-delete-btn"
                onClick={() => {

                  if (
                    deleteConfirmation.type ===
                    "single"
                  ) {
                    deleteSingleDeal(
                      deleteConfirmation.deal
                    );
                  } else {
                    deleteMultipleDeals();
                  }

                }}
                disabled={loading}
              >
                {loading
                  ? "Deleting..."
                  : "Yes, Delete"}
              </button>

            </div>

          </div>

        </div>

      )}

          SINGLE EDIT MODAL
      {editDeal && (

        <div
          className="confirmation-overlay"
          onMouseDown={(e) => {
            if (
              e.target === e.currentTarget &&
              !editLoading
            ) {
              closeEditModal();
            }
          }}
        >

          <div
            className="edit-modal"
            onMouseDown={(e) =>
              e.stopPropagation()
            }
            style={{
              maxWidth: "680px",
              width: "95%",
              maxHeight: "90vh",
              overflowY: "auto",
              padding: "28px",
            }}
          >

            <div
              style={{
                display: "flex",
                justifyContent:
                  "space-between",
                alignItems: "flex-start",
                gap: "20px",
                marginBottom: "24px",
                paddingBottom: "18px",
                borderBottom:
                  "1px solid #e5e7eb",
              }}
            >

              <div>

                <h2
                  style={{
                    margin: 0,
                    marginBottom: "7px",
                  }}
                >
                  Edit Deal
                </h2>

                <p
                  style={{
                    margin: 0,
                    color: "#6b7280",
                    fontSize: "14px",
                  }}
                >
                  Update the selected
                  deal information.
                </p>

              </div>

              <button
                type="button"
                onClick={
                  closeEditModal
                }
                disabled={
                  editLoading
                }
                title="Close"
                style={{
                  width: "36px",
                  height: "36px",
                  border: "none",
                  borderRadius: "8px",
                  background:
                    "#f3f4f6",
                  color: "#374151",
                  fontSize: "20px",
                  cursor:
                    editLoading
                      ? "not-allowed"
                      : "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent:
                    "center",
                  flexShrink: 0,
                }}
              >
                ×
              </button>

            </div>

            <div className="form-group">

              <label>
                Message ID
              </label>

              <input
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
                rows="8"
                value={
                  editContent
                }
                onChange={(e) =>
                  setEditContent(
                    e.target.value
                  )
                }
                placeholder="Enter deal content..."
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
                placeholder="https://..."
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
                placeholder="images/product.jpg"
              />

            </div>

            <div
              className="confirmation-buttons"
              style={{
                marginTop: "24px",
                paddingTop: "18px",
                borderTop:
                  "1px solid #e5e7eb",
              }}
            >

              <button
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

export default Deals;