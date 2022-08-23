import React from 'react';
import {Bar} from 'react-chartjs-2';
import {Chart as ChartJS} from 'chart.js/auto'

function BarChart(prop){
    return <Bar data={prop.chartData} options={prop.options}></Bar>
}

export default BarChart