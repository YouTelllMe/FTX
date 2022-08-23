import React, { useState, useEffect } from "react";
import Navbar from "../components/Nav.js";
import "./Settings.css";

function Settings() {
  const [balance, setBalance] = useState([]);
  const [total, setTotal] = useState(0);
  const [user, setUser] = useState("");
  const [config, setConfig] = useState({
    api_key: "",
    api_secret: "",
    subaccount: "",
  });
  const [subaccount, setSubAccount] = useState([]);

  useEffect(() => {
    fetch("/API", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "get_balance" }),
    })
      .then((res) => res.json())
      .then((data) => {
        setBalance(data["positions"]);
        setTotal(data["totalAccountValue"]);
        setUser(data["username"]);
      });
  }, []);

  useEffect(() => {
    fetch("/API", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "get_subaccounts" }),
    })
      .then((res) => res.json())
      .then((data) => {
        setSubAccount(data);
      });
  }, []);

  useEffect(() => {
    fetch("/API", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "get_config" }),
    })
      .then((res) => res.json())
      .then((data) => {
        setConfig(data);
      });
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const postConfig = await fetch("/API", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "post_config", data: config }),
    })
      .then((response) => response.json())
      .then((x) => {
        if (x === "failure") {
          alert("Failure: Account Credentials Incorrect");
        }
      });
    const reGetBalance = await fetch("/API", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "get_balance" }),
    })
      .then((res) => res.json())
      .then((data) => {
        setBalance(data["positions"]);
        setTotal(data["totalAccountValue"]);
        setUser(data["username"]);
      });
  };

  return (
    <>
      <Navbar location="Settings"></Navbar>
      <form class="settings-form" onSubmit={handleSubmit}>
        <label class="OrderBox--label">API Key:</label>
        <br />
        <input
          type="text"
          value={config["api_key"]}
          onChange={(event) => {
            setConfig((prev) => {
              return { ...prev, api_key: event.target.value };
            });
          }}
        ></input>
        <br />
        <label class="OrderBox--label">API Secret:</label>
        <br />
        <input
          type="password"
          value={config["api_secret"]}
          onChange={(event) => {
            setConfig((prev) => {
              return { ...prev, api_secret: event.target.value };
            });
          }}
        ></input>
        <br />
        <label class="OrderBox--label">Subaccount:</label>
        <br />
        <input
          type="text"
          value={config["subaccount"]}
          onChange={(event) => {
            setConfig((prev) => {
              return { ...prev, subaccount: event.target.value };
            });
          }}
        ></input>
        <br />
        <br />
        <input type="submit" value="Edit"></input>
      </form>
      <div
        style={{
          display: "flex",
          fontSize: "smaller",
          margin: "1%",
          gap: "3%",
          textAlign: "center",
        }}
      >
        <div>
          <p style={{ fontWeight: "bold" }}>Account Info/Balance</p>
          <p>User: {user}</p>
          <p>Total: {total}</p>
          {balance.map((x) => {
            return (
              <p>
                [{x["future"]}][{x["cost"]}]
              </p>
            );
          })}
        </div>
        <br></br>
        <div>
          <p style={{ fontWeight: "bold" }}>Subaccount List</p>
          {subaccount.map((x) => (
            <p>{x["nickname"]}</p>
          ))}
        </div>
      </div>
      <br></br>
    </>
  );
}

export default Settings;
