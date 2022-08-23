
import CoinSelect from './CoinSelect';
import './OrderBox.css'
import React, { useState, useEffect} from 'react';



function OrderBox(props) {

    const[future,setFuture] = useState('BTC')
    const[target,setTarget] = useState('')
    const[tolerance,setTolerance] = useState('')
    const[speed,setSpeed] = useState(1)

    const formData = (event) => {
      event.preventDefault()
      props.orderlist['orderlist'].push({future: future,target: target,tolerance: tolerance,speed: speed
      ,status:'initiating'})
        props.handle(
          {orderlist: props.orderlist['orderlist']}
        )
      
    }

    return (
      <form className="OrderBox" onSubmit={formData}>
        <label className='OrderBox--label'>Future:</label><br/>
        <CoinSelect handlefunc={setFuture}></CoinSelect><br/>
        <label className='OrderBox--label'>Target(USD):</label><br/>
        <input type='number' value={target} onChange={x=>setTarget(x.target.value)} required/><br/>
        <label className='OrderBox--label'>Tolerance(%):</label><br/>
        <input type='number' value={tolerance} onChange={x=>setTolerance(x.target.value)} required/><br/>
        <label className='OrderBox--label'>Speed(x):</label><br/>
        <input type='number' value={speed} onChange={x=>setSpeed(x.target.value)} required/><br/>
        <input className='OrderBox--button' type="submit" value="order"/>
      </form>
    );
  }
  
  export default OrderBox;
