import React from 'react';
import {Line} from 'react-chartjs-2';
import {Chart as ChartJS} from 'chart.js/auto'

function LineChart(prop){
    return <Line data={prop.chartData}></Line>
}

export default LineChart