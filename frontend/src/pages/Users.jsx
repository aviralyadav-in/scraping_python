import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:5000";

function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const [showAddForm, setShowAddForm] = useState(false);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [editingUser, setEditingUser] = useState(null);
  const [editName, setEditName] = useState("");
  const [editRole, setEditRole] = useState("user");

  const token = localStorage.getItem("token");

  const fetchUsers = async () => {
    try {
      setLoading(true);

      const response = await fetch(`${API_URL}/api/users/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || "Failed to fetch users");
        return;
      }

      setUsers(data.results || []);
    } catch (error) {
      console.error("Fetch users error:", error);
      alert("Unable to connect to server");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();

    if (!name.trim() || !email.trim() || !password.trim()) {
      alert("All fields are required");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/users/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || "Failed to create user");
        return;
      }

      alert("User created successfully");

      setName("");
      setEmail("");
      setPassword("");
      setShowAddForm(false);

      fetchUsers();
    } catch (error) {
      console.error("Create user error:", error);
      alert("Unable to connect to server");
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setEditName(user.name || "");
    setEditRole(user.role || "user");
  };

  const closeEditModal = () => {
    setEditingUser(null);
    setEditName("");
    setEditRole("user");
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();

    if (!editName.trim()) {
      alert("Name is required");
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/users/${editingUser.id}/`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name: editName.trim(),
            role: editRole,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || "Failed to update user");
        return;
      }

      alert("User updated successfully");

      closeEditModal();
      fetchUsers();
    } catch (error) {
      console.error("Update user error:", error);
      alert("Unable to connect to server");
    }
  };

  const handleDeleteUser = async (userId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this user?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/users/${userId}/`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || "Failed to delete user");
        return;
      }

      alert("User deleted successfully");

      fetchUsers();
    } catch (error) {
      console.error("Delete user error:", error);
      alert("Unable to connect to server");
    }
  };

  return (
    <div className="page-container">

      <div className="page-header">

        <div>
          <h1>Users</h1>
          <p>Manage system users</p>
        </div>

        <div className="users-header-actions">

          <button
            className="refresh-btn"
            onClick={fetchUsers}
          >
            Refresh
          </button>

          <button
            className="start-btn"
            onClick={() => {
              setShowAddForm(!showAddForm);

              if (!showAddForm) {
                closeEditModal();
              }
            }}
          >
            {showAddForm ? "Cancel" : "Add User"}
          </button>

        </div>

      </div>

      {showAddForm && (
        <div className="card user-form-card">

          <div className="section-header">
            <div>
              <h2>Add User</h2>
              <p>Create a new system user</p>
            </div>
          </div>

          <form onSubmit={handleCreateUser}>

            <div className="form-row">

              <div className="form-group">
                <label>Name</label>

                <input
                  type="text"
                  value={name}
                  onChange={(e) =>
                    setName(e.target.value)
                  }
                  placeholder="Enter name"
                />
              </div>

              <div className="form-group">
                <label>Email</label>

                <input
                  type="email"
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                  placeholder="Enter email"
                />
              </div>

              <div className="form-group">
                <label>Password</label>

                <input
                  type="password"
                  value={password}
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                  placeholder="Enter password"
                />
              </div>

            </div>

            <div className="button-row">

              <button
                type="submit"
                className="save-btn"
              >
                Create User
              </button>

              <button
                type="button"
                className="clear-btn"
                onClick={() => {
                  setName("");
                  setEmail("");
                  setPassword("");
                  setShowAddForm(false);
                }}
              >
                Cancel
              </button>

            </div>

          </form>

        </div>
      )}

      {editingUser && (
        <div
          className="confirmation-overlay"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              closeEditModal();
            }
          }}
        >

          <div className="edit-modal">

            <div className="bulk-update-header">

              <div>
                <h2>Edit User</h2>
                <p>Update user information</p>
              </div>

              <button
                type="button"
                className="clear-btn"
                onClick={closeEditModal}
              >
                ✕
              </button>

            </div>

            <form onSubmit={handleUpdateUser}>

              <div className="form-group">
                <label>Name</label>

                <input
                  type="text"
                  value={editName}
                  onChange={(e) =>
                    setEditName(e.target.value)
                  }
                  placeholder="Enter name"
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label>Email</label>

                <input
                  type="email"
                  value={editingUser.email}
                  disabled
                />
              </div>

              <div className="form-group">
                <label>Role</label>

                <select
                  value={editRole}
                  onChange={(e) =>
                    setEditRole(e.target.value)
                  }
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div className="confirmation-buttons">

                <button
                  type="button"
                  className="clear-btn"
                  onClick={closeEditModal}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="save-btn"
                >
                  Save Changes
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

      <div className="card users-card">

        <div className="section-header">

          <div>
            <h2>All Users</h2>
            <p>View and manage registered users</p>
          </div>

          <span className="status-badge">
            Total: {users.length}
          </span>

        </div>

        {loading ? (
          <div className="no-data">
            Loading users...
          </div>
        ) : users.length === 0 ? (
          <div className="no-data">
            No users found.
          </div>
        ) : (

          <div className="table-container">

            <table>

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Created At</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>

                {users.map((user) => (

                  <tr key={user.id}>

                    <td>{user.id}</td>

                    <td>{user.name}</td>

                    <td>{user.email}</td>

                    <td>
                      <span className="status-badge">
                        {user.role}
                      </span>
                    </td>

                    <td>{user.created_at}</td>

                    <td>

                      <div className="action-buttons">

                        <button
                          className="edit-btn"
                          onClick={() =>
                            handleEditUser(user)
                          }
                        >
                          Edit
                        </button>

                        <button
                          className="delete-btn"
                          onClick={() =>
                            handleDeleteUser(user.id)
                          }
                        >
                          Delete
                        </button>

                      </div>

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        )}

      </div>

    </div>
  );
}

export default Users;