import { useState, useEffect } from "react";

function getRowColor(classification){
    if(classification === 'CRITICAL') return '#ff5252'
    if(classification === 'WARNING') return '#fef9c3'
    return '#dcfce7'
    
}

function AlertTable(){

    const[alerts,setAlerts] = useState([])
    useEffect(() => {
        fetch('http://localhost:8000/alerts')
        .then(res => res.json())
        .then(data => setAlerts(data.alerts))
    }, [])


    return(
        <div>
            <h2>Alerts</h2>
            <table style = {{ width: '100%', borderCollapse: 'collapse'}}>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Message</th>
                        <th>Classification</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {alerts.map(alert => (
                        <tr key={alert.id} style={{ background: getRowColor(alert.classification) }}>
                            <td>{alert.service}</td>
                            <td>{alert.message}</td>
                            <td>{alert.classification}</td>
                            <td>{alert.timestamp}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default AlertTable