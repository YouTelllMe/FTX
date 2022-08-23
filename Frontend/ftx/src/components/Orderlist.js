import CoinSelect from "./CoinSelect";
import "./OrderBox.css";
import React, { useState, useEffect } from "react";

function Orderlist(props) {
  const deleteData = (event) => {
    event.preventDefault();
    const newlist = props.orderlist["orderlist"].filter((x) => {
      return !(
        x["future"] === props.future &&
        x["target"] === props.target &&
        x["subaccount"] === props.config["subaccount"] &&
        x["api_key"] === props.config["api_key"]
      );
    });
    props.handle({ orderlist: newlist });
  };

  return (
    <form className="OrderBox" onSubmit={deleteData}>
      <p className="OrderBox--status">Future:{props.future}</p>
      <p className="OrderBox--status">Target(USD): {props.target}</p>
      <p className="OrderBox--status">Tolerance(%): {props.tolerance}</p>
      <p className="OrderBox--status">Speed: {props.speed}</p>
      <p className="OrderBox--status">Current(USD):{props.current}</p>
      <p className="OrderBox--status">Status: {props.status}</p>
      <input type="submit" value="delete" />
    </form>
  );
}

export default Orderlist;
