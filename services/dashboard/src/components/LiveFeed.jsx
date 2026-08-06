import { useState, useEffect } from "react";


function getRowColor(classification) {
  if (classification === 'CRITICAL') return '#ff5252'
  if (classification === 'WARNING') return '#fef9c3'
  return '#dcfce7'
}


function liveFeed(){

    const [alerts, setAlerts] = useState([])

    useEffect(() => {

        const source = new EventSource('http://localhost:8000/stream')

        source.onmessage = (event) => {
            const alert = JSON.parse(event.data)
            setAlerts(prev => [alert, ...prev])
        }

        source.onerror = () => {
            console.log('SSE Connection Lost')
            source.close()
        }

        return () => source.close()

    },[])

    return(
        <div>
            <h2>Live Feed</h2>
            <table style = {{width: '100%', borderCollapse: 'collapse'}}>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Message</th>
                        <th>Classfication</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {alerts.map((alert, index) => (
                        <tr key = {index} style = {{ background: getRowColor(alert.classification) }}>
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

