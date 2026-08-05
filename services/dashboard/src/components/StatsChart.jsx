import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts'

function StatsChart(){

    const [stats, setStats] = useState([])

    useEffect(() => {
        fetch('http://localhost:8000/stats')
        .then(res => res.json())
        .then(data => setStats(data.stats))
    }, [])

    return(
        <div>
            <h2>Alert Counts</h2>
            <BarChart width={400} height={300} datat = {stats}>
                <XAxis dataKey = "classification" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#6366f1" />
            </BarChart>
        </div>
    )
}

export default StatsChart