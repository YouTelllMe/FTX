import React, { useState, useEffect} from 'react';


export default function CoinSelect(props) {


    const [loc, setloc] = useState([])

    useEffect(() => {
        fetch('/API', {method: 'POST', headers:{'Content-Type': 'application/json'},body:JSON.stringify({type: 
          'get_coins'})}).then(res=>res.json()).then(data => {
            setloc(data.sort())
        })}, []);

    const locbuttons = loc.map((n) => {
        if (n==="BTC"){
          return <option selected>{n}</option>
        } else {
          return <option>{n}</option>
        }})

    return(<select onChange = {(event)=>props.handlefunc(event.target.value)} 
    style={{'marginLeft':'0.8%', 'marginRight':'0.8%','marginBottom':'0.8%'}}>{locbuttons}</select>
    )

};
