import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Profile({ currentUser }) {
  const navigate = useNavigate();

  const [showEdit, setShowEdit] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const [name, setName] = useState(currentUser?.name || "");
  const [savedName, setSavedName] = useState(currentUser?.name || "");

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const isAdmin = currentUser?.role === "admin";

  const getInitials = () => {
    const userName = savedName || currentUser?.name || "User";

    return userName
      .split(" ")
      .filter(Boolean)
      .map((word) => word.charAt(0))
      .join("")
      .slice(0, 2)
      .toUpperCase();
  };

  const openEditProfile = () => {
    setName(savedName);
    setShowEdit(true);
  };

  const closeEditProfile = () => {
    setName(savedName);
    setShowEdit(false);
  };

  const handleSaveProfile = () => {
    if (!name.trim()) {
      alert("Name cannot be empty.");
      return;
    }

    setSavedName(name.trim());
    setShowEdit(false);
  };

  const openPasswordModal = () => {
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setShowPassword(true);
  };

  const closePasswordModal = () => {
    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setShowPassword(false);
  };

  const handleChangePassword = () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      alert("Please fill all password fields.");
      return;
    }

    if (newPassword.length < 6) {
      alert("New password must contain at least 6 characters.");
      return;
    }

    if (newPassword !== confirmPassword) {
      alert("New password and confirm password do not match.");
      return;
    }

    alert("Password changed successfully.");

    closePasswordModal();
  };

  return (
    <div className="profile-page">
      <div className="profile-page-container">
        <div className="profile-topbar">
          <button
            type="button"
            className="profile-back-btn"
            onClick={() => navigate("/dashboard")}
          >
            <span>←</span>
            Back to Dashboard
          </button>
        </div>

        <div className="profile-heading">
          <div>
            <span className="profile-heading-label">
              ACCOUNT
            </span>

            <h1>My Profile</h1>

            <p>
              View and manage your personal account information.
            </p>
          </div>
        </div>

        <div className="profile-layout">
          <div className="profile-main-card">
            <div className="profile-card-header">
              <div className="profile-large-avatar">
                {getInitials()}
              </div>

              <div className="profile-identity-info">
                <h2>{savedName || "User"}</h2>

                <p>
                  {currentUser?.email || "No email available"}
                </p>

                <span
                  className={`profile-role-badge ${
                    isAdmin ? "admin" : "user"
                  }`}
                >
                  <span className="role-dot"></span>
                  {isAdmin ? "Administrator" : "User"}
                </span>
              </div>
            </div>

            <div className="profile-divider"></div>

            <div className="profile-section-header">
              <div>
                <h3>Personal Information</h3>

                <p>
                  Your basic account information
                </p>
              </div>

              <button
                type="button"
                className="profile-edit-btn"
                onClick={openEditProfile}
              >
                <span>✎</span>
                Edit Profile
              </button>
            </div>

            <div className="profile-info-grid">
              <div className="profile-info-box">
                <span className="profile-info-label">
                  FULL NAME
                </span>

                <strong>
                  {savedName || "-"}
                </strong>
              </div>

              <div className="profile-info-box">
                <span className="profile-info-label">
                  EMAIL ADDRESS
                </span>

                <strong>
                  {currentUser?.email || "-"}
                </strong>
              </div>

              <div className="profile-info-box">
                <span className="profile-info-label">
                  ACCOUNT ROLE
                </span>

                <strong>
                  {isAdmin ? "Administrator" : "User"}
                </strong>
              </div>

              <div className="profile-info-box">
                <span className="profile-info-label">
                  ACCOUNT STATUS
                </span>

                <strong className="active-status">
                  <span className="status-dot"></span>
                  Active
                </strong>
              </div>
            </div>
          </div>

          <div className="profile-security-card">
            <div className="security-card-top">
              <div className="security-card-icon">
                🔒
              </div>

              <div>
                <h3>Password & Security</h3>

                <p>
                  Keep your account secure by updating
                  your password regularly.
                </p>
              </div>
            </div>

            <div className="security-card-divider"></div>

            <div className="security-status">
              <div className="security-check">
                ✓
              </div>

              <div>
                <strong>Account Protected</strong>

                <span>
                  Your account is currently active.
                </span>
              </div>
            </div>

            <button
              type="button"
              className="change-password-btn"
              onClick={openPasswordModal}
            >
              <span>🔒</span>
              Change Password
            </button>
          </div>
        </div>
      </div>

      {showEdit && (
        <div
          className="profile-modal-overlay"
          onMouseDown={closeEditProfile}
        >
          <div
            className="profile-modal"
            onMouseDown={(e) => e.stopPropagation()}
          >
            <div className="profile-modal-header">
              <div>
                <span className="modal-label">
                  PROFILE
                </span>

                <h2>Edit Profile</h2>

                <p>
                  Update your personal information.
                </p>
              </div>

              <button
                type="button"
                className="profile-modal-close"
                onClick={closeEditProfile}
              >
                ×
              </button>
            </div>

            <div className="profile-form">
              <div className="profile-form-field">
                <label htmlFor="profile-name">
                  Full Name
                </label>

                <input
                  id="profile-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your name"
                  autoFocus
                />
              </div>

              <div className="profile-form-field">
                <label htmlFor="profile-email">
                  Email Address
                </label>

                <input
                  id="profile-email"
                  type="email"
                  value={currentUser?.email || ""}
                  disabled
                />

                <small>
                  Email address cannot be changed here.
                </small>
              </div>
            </div>

            <div className="profile-modal-actions">
              <button
                type="button"
                className="profile-cancel-btn"
                onClick={closeEditProfile}
              >
                Cancel
              </button>

              <button
                type="button"
                className="profile-save-btn"
                onClick={handleSaveProfile}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {showPassword && (
        <div
          className="profile-modal-overlay"
          onMouseDown={closePasswordModal}
        >
          <div
            className="profile-modal"
            onMouseDown={(e) => e.stopPropagation()}
          >
            <div className="profile-modal-header">
              <div>
                <span className="modal-label">
                  SECURITY
                </span>

                <h2>Change Password</h2>

                <p>
                  Create a new password for your account.
                </p>
              </div>

              <button
                type="button"
                className="profile-modal-close"
                onClick={closePasswordModal}
              >
                ×
              </button>
            </div>

            <div className="profile-form">
              <div className="profile-form-field">
                <label htmlFor="current-password">
                  Current Password
                </label>

                <input
                  id="current-password"
                  type="password"
                  value={currentPassword}
                  onChange={(e) =>
                    setCurrentPassword(e.target.value)
                  }
                  placeholder="Enter current password"
                  autoFocus
                />
              </div>

              <div className="profile-form-field">
                <label htmlFor="new-password">
                  New Password
                </label>

                <input
                  id="new-password"
                  type="password"
                  value={newPassword}
                  onChange={(e) =>
                    setNewPassword(e.target.value)
                  }
                  placeholder="Enter new password"
                />

                <small>
                  Password must contain at least 6 characters.
                </small>
              </div>

              <div className="profile-form-field">
                <label htmlFor="confirm-password">
                  Confirm New Password
                </label>

                <input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) =>
                    setConfirmPassword(e.target.value)
                  }
                  placeholder="Confirm new password"
                />
              </div>
            </div>

            <div className="profile-modal-actions">
              <button
                type="button"
                className="profile-cancel-btn"
                onClick={closePasswordModal}
              >
                Cancel
              </button>

              <button
                type="button"
                className="profile-save-btn"
                onClick={handleChangePassword}
              >
                Update Password
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;