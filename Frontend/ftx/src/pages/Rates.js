import React, { useState, useEffect } from "react";
import LineChart from "../components/LineChart.js";
import Navbar from "../components/Nav.js";
import CoinSelect from "../components/CoinSelect.js";

import "./Rates.css";

function Rates() {
  const [coin, setCoin] = useState("BTC");
  const [data, setData] = useState({
    labels: [],
    datasets: [
      {
        label: "",
        data: [],
        backgroundColor: ["red"],
        borderColor: "black",
        borderWidth: 1,
      },
    ],
  });
  const [table, setTable] = useState({ data: [], key: "name" });
  const negativeSorts = [
    "name",
    "negative",
    "current_borrow",
    "estimated_borrow",
  ];

  function compare(a, b, key) {
    if (negativeSorts.includes(key)) {
      if (a[key] < b[key]) {
        return -1;
      }
      if (a[key] > b[key]) {
        return 1;
      }
    } else {
      if (a[key] < b[key]) {
        return 1;
      }
      if (a[key] > b[key]) {
        return -1;
      }
    }
    return 0;
  }

  useEffect(() => {
    fetch("/API/tabledata", { method: "GET" })
      .then((res) => res.json())
      .then((data) => {
        setTable((prev) => ({
          data: data.sort((a, b) => compare(a, b, "name")),
          key: prev.key,
        }));
      });
  }, []);

  useEffect(() => {
    fetch("/API", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "graph_rates", coin: coin }),
    })
      .then((res) => res.json())
      .then((data) =>
        setData({
          labels: data["xvalues"],
          datasets: [
            {
              label: coin + " rates (20 days)",
              data: data["yvalues"],
              backgroundColor: data["colors"],
              borderColor: "black",
              borderWidth: 1,
            },
          ],
        })
      );
  }, [coin]);

  const tableHeaders = [
    "name",
    "rate",
    "positive",
    "negative",
    "future_volume",
    "spot_volume",
    "current_borrow",
    "estimated_borrow",
    "7 Average",
    "20 Average",
    "40 Average",
    "100 Average",
  ];

  return (
    <>
      <Navbar location="Rates"></Navbar>
      <div
        style={{
          width: "95%",
          marginBottom: "3%",
          marginTop: "3%",
        }}
      >
        <LineChart chartData={data}></LineChart>
      </div>
      <table style={{ fontSize: "90%" }}>
        <tr>
          {tableHeaders.map((x) => {
            return x === table.key ? (
              <th>
                <input
                  type="button"
                  value={x}
                  className="tableHeader--sorted"
                />
              </th>
            ) : (
              <th>
                <input
                  type="button"
                  className="tableHeader"
                  value={x}
                  onClick={(event) => {
                    setTable((prev) => ({
                      data: prev.data.sort((a, b) =>
                        compare(a, b, event.target.value)
                      ),
                      key: event.target.value,
                    }));
                  }}
                />
              </th>
            );
          })}
        </tr>
        {table.data.map((dataRow) => (
          <tr className="dataRow" onClick={(event) => setCoin(dataRow["name"])}>
            <td>{dataRow["name"]}</td>
            <td>{dataRow["rate"]}</td>
            <td>{dataRow["positive"]}</td>
            <td>{dataRow["negative"]}</td>
            <td>{dataRow["future_volume"]}</td>
            <td>{dataRow["spot_volume"]}</td>
            <td>{dataRow["current_borrow"]}</td>
            <td>{dataRow["estimated_borrow"]}</td>
            <td>{dataRow["7 Average"]}</td>
            <td>{dataRow["20 Average"]}</td>
            <td>{dataRow["40 Average"]}</td>
            <td>{dataRow["100 Average"]}</td>
          </tr>
        ))}
      </table>
    </>
  );
}

export default Rates;
