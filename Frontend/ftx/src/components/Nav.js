import React from "react";
import "./Nav.css";
import { Link } from "react-router-dom";

function Nav(props) {
  const nav = ["Rates", "Profile", "Order", "Settings"];

  return (
    <div style={{ marginBottom: "0.1%" }}>
      {nav.map((x) => {
        return props.location === x ? (
          <Link to={{ pathname: "/" + x.toLowerCase() }}>
            <button className="navbutton--current">{x}</button>
          </Link>
        ) : (
          <Link to={{ pathname: "/" + x.toLowerCase() }}>
            <button className="navbutton">{x}</button>
          </Link>
        );
      })}
    </div>
  );
}

export default Nav;
