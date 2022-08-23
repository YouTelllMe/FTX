
import React, { useState, useEffect} from 'react';
import BarChart from '../components/BarChart.js';
import Navbar from '../components/Nav.js'



function Profile() {
  
  const [data, setData] = useState({
    labels: [],
    datasets: [{
      label: "",
      data: [],
    }]
  })
  const [coin, setCoin] = useState("ALL")
  const [loc, setLoc] = useState([])
  const [borrowData, setBorrowData] = useState({
    labels: [],
    datasets: [{
      label: "",
      data: [],
    }]
  })


  useEffect(() => {
    fetch('/API', {method: 'POST', headers:{'Content-Type': 'application/json'},body:JSON.stringify({type: 
      'payments-list'})}).then(res=>res.json()).then(data => {
        setLoc(data['futures'].sort())
    })}, []);

  useEffect(()=>{
    const colors = ['red','green','orange','blue','yellow','purple','pink','grey','peach','beige','brown','violet','tan','magenta']

    if (coin === 'ALL'){
    fetch('/API', {method: 'POST', headers:{'Content-Type': 'application/json'},body:JSON.stringify({type: 
      'graph_all'})}).then(res=>res.json()).then(totaldata=>{
        var xvalues
        var length = 0
        var x_yvalues = []
        var y_yvalues = []
        var valueindex = -1
        const data_coins = totaldata['coins']
        var data_x
        var data_y
        for (let i = 0; i<data_coins.length;i++)
          {
            data_x = totaldata[totaldata['coins'][i]]['xvalues']
            data_y = totaldata[totaldata['coins'][i]]['yvalues']
            if(data_x.length>length){
            xvalues = data_x
            length = data_x.length
          }
          x_yvalues.push(data_y[0])
          y_yvalues.push(data_y[1])
        }
        setData({
          labels: xvalues,
          datasets: data_coins.map(
            (coin,i) => 
            {valueindex = -1
              return {
              label: coin,
              data: xvalues.map(
              x => {
                if (x_yvalues[i].includes(x)){
                  valueindex+=1
                  return (y_yvalues[i][valueindex])
                }else{return (0)}}
              ),
              backgroundColor: colors[i%15],
              borderColor:'black',
              borderWidth: 1
            }}
          )}
        )
      })}
    
    else{
    fetch('/API', {method: 'POST', headers:{'Content-Type': 'application/json'},body:JSON.stringify({type: 
      'graph_payments', coin: coin})}).then(res=>res.json()).then(data=>{
        if (coin === 'ALL'){
          console.log(data)
        }
        else{
          setData({
          labels: data['xvalues'],
          datasets: [{
            label: coin+" payments (20 days)",
            data: data['yvalues'],
            backgroundColor: data['colors'],
            borderColor:'black',
            borderWidth: 1
          }]
        })}})
  }},[coin])

  useEffect(()=>{
    if (coin !== 'ALL'){
    fetch('/API', {method: 'POST', headers:{'Content-Type': 'application/json'},body:JSON.stringify({type: 
      'graph_borrow', coin: coin})}).then(res=>res.json()).then(data=>{
          setBorrowData({
          labels: data['xvalues'],
          datasets: [{
            label: coin+" borrow (20 days)",
            data: data['yvalues'],
            backgroundColor: ['red'],
            borderColor:'black',
            borderWidth: 1
          }]
        })})}
  },[coin])


  const options = loc.map((n) => {
      return <option>{n}</option>
    })

  return (
    <>
      <Navbar location='Profile'></Navbar>
      <br></br>
      <select onChange = {(event)=>setCoin(event.target.value)} style={{'marginLeft':'0.8%', 'marginRight':'0.8%'}}>
        <option>ALL</option>
        {options}
        </select>
      <br></br>
      <div style={{'margin':'3%', 'width':'94%'}}>
        <BarChart chartData={data} options={{scales:{xAxes:{stacked:true},yAxes:{stacked:true}}}}></BarChart>
      </div>
      {(coin !== 'ALL') ?
      <div style={{'margin':'3%','width':'94%'}}>
        <BarChart chartData={borrowData}></BarChart>
      </div>:<></>}
    </>
  );
}

export default Profile;
