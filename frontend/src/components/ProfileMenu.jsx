import { useState } from "react";
import { useNavigate } from "react-router-dom";

function ProfileMenu({ currentUser, onLogout }) {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  if (!currentUser) {
    return null;
  }

  const isAdmin = currentUser.role === "admin";

  const getInitials = () => {
    const name = currentUser.name || "User";

    return name
      .split(" ")
      .map((word) => word.charAt(0))
      .join("")
      .slice(0, 2)
      .toUpperCase();
  };

  const handleProfile = () => {
    setIsOpen(false);
    navigate("/profile");
  };

  const handleLogout = () => {
    setIsOpen(false);

    if (onLogout) {
      onLogout();
    }
  };

  return (
    <div className="profile-menu">
      <button
        type="button"
        className="profile-menu-button"
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <div className="profile-avatar">
          {getInitials()}
        </div>

        <div className="profile-user-info">
          <span className="profile-user-name">
            {currentUser.name || "User"}
          </span>

          <span className="profile-user-role">
            {isAdmin ? "Administrator" : "User"}
          </span>
        </div>

        <span className="profile-arrow">
          {isOpen ? "▲" : "▼"}
        </span>
      </button>

      {isOpen && (
        <div className="profile-dropdown">
          <div className="profile-dropdown-header">
            <div className="profile-dropdown-avatar">
              {getInitials()}
            </div>

            <div className="profile-dropdown-user">
              <strong>
                {currentUser.name || "User"}
              </strong>

              <span>
                {currentUser.email || "No email"}
              </span>
            </div>
          </div>

          <div className="profile-dropdown-divider"></div>

          <button
            type="button"
            className="profile-dropdown-item"
            onClick={handleProfile}
          >
            <span className="profile-item-icon">👤</span>
            <span>My Profile</span>
          </button>

          <div className="profile-dropdown-divider"></div>

          <button
            type="button"
            className="profile-dropdown-item logout-item"
            onClick={handleLogout}
          >
            <span className="profile-item-icon">↪</span>
            <span>Logout</span>
          </button>
        </div>
      )}
    </div>
  );
}

export default ProfileMenu;