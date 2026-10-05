import AlertTable from "./components/AlertTable";
import StatsChart from "./components/StatsChart";
import LiveFeed from "./components/LiveFeed";

function App(){
        return (
    <div>
        <StatsChart />
        <AlertTable />
        <LiveFeed />
    </div>
    )
}

export default App