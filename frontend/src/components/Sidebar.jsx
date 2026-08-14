import { NavLink } from "react-router-dom";

function Sidebar({
  currentUser,
  onLogout
}) {
  const commonMenuItems = [
    {
      name: "Dashboard",
      path: "/dashboard"
    },
    {
      name: "Deals",
      path: "/deals"
    },
    {
      name: "Duplicates",
      path: "/duplicates"
    }
  ];

  const adminMenuItems = [
    {
      name: "Scraping",
      path: "/scraping"
    },
    {
      name: "Scraping Jobs",
      path: "/jobs"
    },
    {
      name: "Statistics",
      path: "/statistics"
    },
    {
      name: "Logs",
      path: "/logs"
    },
    {
      name: "Users",
      path: "/users"
    }
  ];

  const isAdmin =
    currentUser?.role === "admin";

  const menuItems = isAdmin
    ? [...commonMenuItems, ...adminMenuItems]
    : commonMenuItems;

  const handleLogout = () => {
    const confirmed = window.confirm(
      "Are you sure you want to logout?"
    );

    if (!confirmed) {
      return;
    }

    if (onLogout) {
      onLogout();
    } else {
      localStorage.removeItem("token");
      window.location.href = "/";
    }
  };

  return (
    <aside className="sidebar">

      <div className="sidebar-header">
        <h2>
          Telegram Deals
        </h2>

        <p>
          Scraper
        </p>
      </div>

      <nav className="sidebar-nav">

        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              isActive
                ? "nav-item active"
                : "nav-item"
            }
          >
            {item.name}
          </NavLink>
        ))}

      </nav>

      <div className="sidebar-footer">

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