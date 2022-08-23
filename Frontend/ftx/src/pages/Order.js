import React, { useState, useEffect } from "react";
import Navbar from "../components/Nav.js";
import OrderBox from "../components/OrderBox.js";
import Orderlist from "../components/Orderlist.js";

function Order() {
  const [clientOrder, setClientOrder] = useState({ orderlist: [] });
  const [initial, setInitial] = useState(true);
  const [config, setConfig] = useState({
    api_key: "",
    api_secret: "",
    subaccount: "",
  });

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

  useEffect(() => {
    if (initial) {
      fetch("/API", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: "read_client_orders" }),
      })
        .then((res) => res.json())
        .then((data) => {
          setClientOrder(JSON.parse(data));
          setInitial(false);
        });
    } else {
      const newList = clientOrder["orderlist"].map((x) => {
        if (x.hasOwnProperty("api_key")) {
          return x;
        } else {
          return { ...x, ...config };
        }
      });
      fetch("/API", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "post_client_orders",
          data: { orderlist: newList },
        }),
      });
    }
  }, [clientOrder]);

  function refreshPage() {
    window.location.reload(false);
  }

  return (
    <>
      <Navbar location="Order"></Navbar>
      <OrderBox
        handle={(x) => setClientOrder(x)}
        orderlist={clientOrder}
      ></OrderBox>
      <button onClick={refreshPage} style={{ marginLeft: "1%" }}>
        Refresh
      </button>

      <div style={{ display: "flex", flexWrap: "wrap" }}>
        {clientOrder["orderlist"].map((x) => {
          if (
            config["api_key"] === x["api_key"] &&
            config["subaccount"] === x["subaccount"]
          ) {
            return (
              <Orderlist
                status={x["status"]}
                current={x["cost"]}
                future={x["future"]}
                tolerance={x["tolerance"]}
                speed={x["speed"]}
                target={x["target"]}
                orderlist={clientOrder}
                config={config}
                handle={(x) => setClientOrder(x)}
              />
            );
          } else {
            return <></>;
          }
        })}
      </div>
    </>
  );
}

export default Order;
