import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:5000";

function Duplicates() {
  const [duplicates, setDuplicates] = useState([]);
  const [duplicateCount, setDuplicateCount] = useState(0);
  const [loading, setLoading] = useState(true);

  // =========================================================
  // FETCH DUPLICATES
  // =========================================================

  const fetchDuplicates = async () => {
    try {
      setLoading(true);

      const response = await fetch(
        `${API_URL}/api/deals/duplicates/`
      );

      const data = await response.json();

      console.log("Duplicates API Response:", data);

      if (!response.ok) {
        console.error(
          "Duplicates API error:",
          data
        );

        setDuplicates([]);
        setDuplicateCount(0);
        return;
      }

      /*
        Backend may return:

        {
          results: [...]
        }

        OR

        {
          duplicates: [...]
        }

        OR

        {
          data: [...]
        }
      */

      let duplicateData = [];

      if (Array.isArray(data.results)) {
        duplicateData = data.results;
      } else if (
        Array.isArray(data.duplicates)
      ) {
        duplicateData = data.duplicates;
      } else if (Array.isArray(data.data)) {
        duplicateData = data.data;
      } else if (Array.isArray(data)) {
        duplicateData = data;
      }

      setDuplicates(duplicateData);

      setDuplicateCount(
        data.count ??
          data.total ??
          duplicateData.length
      );

    } catch (error) {
      console.error(
        "Duplicates fetch error:",
        error
      );

      setDuplicates([]);
      setDuplicateCount(0);

    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // LOAD ON PAGE OPEN
  // =========================================================

  useEffect(() => {
    fetchDuplicates();
  }, []);

  // =========================================================
  // GET FIELD VALUE
  // =========================================================

  const getMessageId = (deal) => {
    return (
      deal.message_id ??
      deal.messageId ??
      deal.id ??
      "-"
    );
  };

  const getChannel = (deal) => {
    return (
      deal.channel ??
      deal.channel_name ??
      deal.channelName ??
      "-"
    );
  };

  const getContent = (deal) => {
    return (
      deal.content ??
      deal.message ??
      deal.text ??
      "-"
    );
  };

  const getProductLink = (deal) => {
    return (
      deal.product_link ??
      deal.productLink ??
      deal.link ??
      deal.url ??
      ""
    );
  };

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="page-container">

      {/* PAGE HEADER */}

      <div className="page-header">

        <div>

          <h1>
            Duplicate Deals
          </h1>

          <p>
            Detect duplicate deals stored in the database.
          </p>

        </div>

        <button
          className="refresh-btn"
          onClick={fetchDuplicates}
          disabled={loading}
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>

      </div>

      {/* DUPLICATES CARD */}

      <section className="card">

        <div className="section-header">

          <div>

            <h2>
              Duplicate Deals
            </h2>

            <p>
              Total Duplicate Deals:{" "}
              {duplicateCount}
            </p>

          </div>

        </div>

        {/* LOADING */}

        {loading ? (

          <div className="loading-state">
            <p>
              Loading duplicate deals...
            </p>
          </div>

        ) : (

          <div className="table-container">

            <table>

              <thead>

                <tr>

                  <th>
                    Message ID
                  </th>

                  <th>
                    Channel
                  </th>

                  <th>
                    Content
                  </th>

                  <th>
                    Product Link
                  </th>

                </tr>

              </thead>

              <tbody>

                {duplicates.length > 0 ? (

                  duplicates.map(
                    (deal, index) => {

                      const messageId =
                        getMessageId(
                          deal
                        );

                      const channel =
                        getChannel(
                          deal
                        );

                      const content =
                        getContent(
                          deal
                        );

                      const productLink =
                        getProductLink(
                          deal
                        );

                      return (

                        <tr
                          key={`${messageId}-${index}`}
                        >

                          {/* MESSAGE ID */}

                          <td>
                            {messageId}
                          </td>

                          {/* CHANNEL */}

                          <td>
                            {channel}
                          </td>

                          {/* CONTENT */}

                          <td className="content-cell">

                            {content}

                          </td>

                          {/* PRODUCT LINK */}

                          <td>

                            {productLink ? (

                              <a
                                href={
                                  productLink
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

                        </tr>

                      );

                    }
                  )

                ) : (

                  <tr>

                    <td
                      colSpan="4"
                      className="no-data"
                    >
                      No duplicate deals found
                    </td>

                  </tr>

                )}

              </tbody>

            </table>

          </div>

        )}

      </section>

    </div>
  );
}

export default Duplicates;