import { useState, useEffect } from "react";
import Footer from "../components/Footer";
import { api_endpoint } from "../library/constants";
import { withAuthenticator } from "@aws-amplify/ui-react";
import { Link } from "react-router-dom";
import EditModal from "../components/EditModal";

import { EquipmentLog } from "../library/types";

const EquipmentUsage = () => {
  const [searchUsername, setSearchUsername] = useState("");
  const [equipmentLogs, setEquipmentLogs] = useState<EquipmentLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedLog, setSelectedLog] = useState<EquipmentLog | null>(null);

  useEffect(() => {
    const fetchEquipmentLogs = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${api_endpoint}/equipment?limit=50`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "X-Api-Key": import.meta.env.VITE_BACKEND_KEY,
          },
        });

        if (!response.ok) {
          throw new Error(
            `Error fetching equipment logs: ${response.statusText}`
          );
        }

        const data = await response.json();
        console.log(`Data received:\n${JSON.stringify(data, null, 2)}`);
        const logs: EquipmentLog[] = Array.isArray(data.equipment_logs)
          ? data.equipment_logs
          : [];

        setEquipmentLogs(logs);
      } catch (error) {
        console.error("Error fetching equipment logs:", error);
        setEquipmentLogs([]);
      } finally {
        setLoading(false);
      }
    };

    fetchEquipmentLogs();
  }, []);

  const handleEditClick = (log: EquipmentLog) => {
    setSelectedLog(log);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setSelectedLog(null);
  };

  const handleSave = async (updatedLog: EquipmentLog) => {
    setEquipmentLogs((prevLogs) =>
      prevLogs.map((log) =>
        log.timestamp === updatedLog.timestamp &&
        log.user_id === updatedLog.user_id
          ? updatedLog
          : log
      )
    );

    console.log(JSON.stringify(updatedLog, null, 2));

    try {
      const { user_id, ...updatedLogWithoutUserId } = updatedLog;

      const response = await fetch(
        `${api_endpoint}/equipment/${updatedLog.user_id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            "X-Api-Key": import.meta.env.VITE_BACKEND_KEY,
          },
          body: JSON.stringify(updatedLogWithoutUserId),
        }
      );

      if (response.ok) {
        const responseData = await response.json();
        console.log("Data successfully sent to the API:", responseData);
      } else {
        const errorText = await response.text();
        console.error(
          "Failed to send data to the API:",
          response.status,
          errorText
        );
        console.log("Failed to update the equipment log.");
      }
    } catch (error) {
      console.error(
        "An error occurred while updating the equipment log:",
        error
      );
    }
  };

  const appendLogs = (logs: EquipmentLog[]) => {
    setEquipmentLogs((prevLogs) => {
      // Create a Map to ensure unique logs based on user_id and timestamp
      const logMap = new Map();

      // Add previous logs to the Map
      prevLogs.forEach((log) => {
        const key = `${log.user_id}-${log.timestamp}`; // Composite key
        logMap.set(key, log); // Add the log to the Map
      });

      // Add new logs from the fetched data to the Map
      logs.forEach((log) => {
        const key = `${log.user_id}-${log.timestamp}`; // Composite key
        logMap.set(key, log); // Add the log to the Map
      });

      // Convert the Map back to an array and return it
      return Array.from(logMap.values());
    });
  };

  const handleSearch = async (user_id: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${api_endpoint}/equipment/${user_id}?limit=50`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "X-Api-Key": import.meta.env.VITE_BACKEND_KEY,
          },
        }
      );

      if (!response.ok) {
        throw new Error(
          `Error fetching equipment logs for ${user_id}: ${response.statusText}`
        );
      }

      const data = await response.json();
      console.log(`Data received:\n${JSON.stringify(data, null, 2)}`);
      const logs: EquipmentLog[] = Array.isArray(data.equipment_logs)
        ? data.equipment_logs
        : [];

      appendLogs(logs);
    } catch (error) {
      console.error("Error fetching equipment logs:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${api_endpoint}/equipment?limit=50`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "X-Api-Key": import.meta.env.VITE_BACKEND_KEY,
        },
      });

      if (!response.ok) {
        throw new Error(
          `Error fetching equipment logs: ${response.statusText}`
        );
      }

      const data = await response.json();
      console.log(`Data received:\n${JSON.stringify(data, null, 2)}`);
      const logs: EquipmentLog[] = Array.isArray(data.equipment_logs)
        ? data.equipment_logs
        : [];

      appendLogs(logs);
    } catch (error) {
      console.error("Error fetching equipment logs:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredLogs = equipmentLogs.filter((log) =>
    searchUsername ? log.user_id.includes(searchUsername) : true
  );

  return (
    <div
      className="container bg-primary p-5 rounded d-flex flex-column"
      style={{ minHeight: "30%", maxWidth: "95%" }}
    >
      <div className="mb-4 text-center">
        <h1 className="text-secondary fw-bold mb-1">Equipment Usage</h1>
      </div>
      <div className="d-flex flex-column align-items-center justify-content-center text-white">
        <div className="d-flex align-items-end justify-content-between w-100">
          <div className="mb-3">
            <div>
              <button
                onClick={() => handleRefresh()}
                className="btn btn-secondary"
                type="button"
              >
                Refresh Logs
              </button>
            </div>
          </div>
          <div className="mb-3">
            <label htmlFor="username" className="form-label">
              Search by Username:
            </label>
            <div className="input-group">
              <input
                type="text"
                className="form-control"
                id="username"
                value={searchUsername}
                onChange={(e) => setSearchUsername(e.target.value)}
              />
              <button
                onClick={() => handleSearch(searchUsername)}
                className="btn btn-secondary"
                type="button"
              >
                Search
              </button>
            </div>
          </div>
        </div>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <table className="table table-bordered table-primary">
            <thead>
              <tr>
                <th className="text-center align-middle">Location</th>
                <th className="text-center align-middle">Username</th>
                <th className="text-center align-middle">Equipment Type</th>
                <th className="text-center align-middle">Project Name</th>
                <th className="text-center align-middle">Project Type</th>
                <th className="text-center align-middle">Timestamp</th>
                <th className="text-center align-middle"></th>
              </tr>
            </thead>
            <tbody>
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log, index) => (
                  <tr key={index}>
                    <td className="text-center align-middle">{log.location}</td>
                    <td className="text-center align-middle">{log.user_id}</td>
                    <td className="text-center align-middle">
                      {log.equipment_type}
                    </td>
                    <td className="text-center align-middle">
                      {log.project_name}
                    </td>
                    <td className="text-center align-middle">
                      {log.project_type}
                    </td>
                    <td className="text-center align-middle">
                      {log.timestamp}
                    </td>
                    <td className="text-center align-middle">
                      <button
                        className="btn btn-dark"
                        onClick={() => handleEditClick(log)}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center">
                    No records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      <EditModal
        show={showModal}
        handleClose={handleModalClose}
        log={selectedLog}
        handleSave={handleSave}
      />

      <div className="d-flex flex-wrap justify-content-center">
        <div className="m-5">
          <Link to={"/admin"} key={"Admin"}>
            <button className="btn btn-pastel-purple">Back</button>
          </Link>
        </div>
      </div>
      <div className="flex-grow-1"></div>
      <Footer />
    </div>
  );
};

export default withAuthenticator(EquipmentUsage, {
  hideSignUp: true,
});
