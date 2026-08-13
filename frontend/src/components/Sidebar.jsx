function Sidebar({
  activePage,
  setActivePage,
  currentUser,
  onLogout
}) {

  // ==========================================
  // COMMON MENU ITEMS
  // These are visible to everyone
  // ==========================================

  const commonMenuItems = [
    {
      name: "Dashboard",
      key: "dashboard"
    },
    {
      name: "Deals",
      key: "deals"
    },
    {
      name: "Duplicates",
      key: "duplicates"
    }
  ];

  // ==========================================
  // ADMIN ONLY MENU ITEMS
  // ==========================================

  const adminMenuItems = [
    {
      name: "Scraping",
      key: "scraping"
    },
    {
      name: "Scraping Jobs",
      key: "jobs"
    },
    {
      name: "Statistics",
      key: "statistics"
    },
    {
      name: "Logs",
      key: "logs"
    },
    {
      name: "Users",
      key: "users"
    }
  ];

  // ==========================================
  // CHECK USER ROLE
  // ==========================================

  const isAdmin =
    currentUser?.role === "admin";

  // ==========================================
  // FINAL MENU
  // ==========================================

  const menuItems = isAdmin
    ? [...commonMenuItems, ...adminMenuItems]
    : commonMenuItems;

  // ==========================================
  // LOGOUT
  // ==========================================

  const handleLogout = () => {

    const confirmed = window.confirm(
      "Are you sure you want to logout?"
    );

    if (!confirmed) {
      return;
    }

    // Use parent logout function
    // so backend session is also cleared
    if (onLogout) {
      onLogout();
    } else {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
  };

  return (
    <aside className="sidebar">

      {/* ======================================
          SIDEBAR HEADER
      ====================================== */}

      <div className="sidebar-header">

        <h2>
          Telegram Deals
        </h2>

        <p>
          Scraper
        </p>

      </div>

      {/* ======================================
          NAVIGATION
      ====================================== */}

      <nav className="sidebar-nav">

        {menuItems.map((item) => (

          <button
            key={item.key}
            className={
              activePage === item.key
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage(item.key)
            }
          >
            {item.name}
          </button>

        ))}

      </nav>

      {/* ======================================
          FOOTER
      ====================================== */}

      <div className="sidebar-footer">

        {/* Current user */}

        {currentUser && (
          <div className="sidebar-user">

            <div className="sidebar-user-name">
              {currentUser.name}
            </div>

            <div className="sidebar-user-role">
              {currentUser.role === "admin"
                ? "Administrator"
                : "User"}
            </div>

          </div>
        )}

        <button
          className="logout-sidebar-btn"
          onClick={handleLogout}
        >
          Logout
        </button>

      </div>

    </aside>
  );
}

export default Sidebar;