document.addEventListener('DOMContentLoaded', () => {
    // Utilities
    const random = (min, max) => Math.random() * (max - min) + min;
    const formatNumber = (num) => Math.floor(num).toLocaleString('en-US');

    // DOM Elements
    const throughputVal = document.getElementById('throughput-val');
    const latencyVal = document.getElementById('latency-val');
    const errorVal = document.getElementById('error-val');
    
    const throughputSpark = document.getElementById('throughput-spark');
    const latencySpark = document.getElementById('latency-spark');
    const errorSpark = document.getElementById('error-spark');
    
    const ingestionChart = document.getElementById('ingestion-chart');
    const terminal = document.getElementById('event-terminal');

    // Initialize Sparklines
    const initSparklines = (container, count) => {
        container.innerHTML = '';
        for(let i=0; i<count; i++) {
            const bar = document.createElement('div');
            bar.className = 'spark-bar';
            bar.style.height = `${random(20, 100)}%`;
            container.appendChild(bar);
        }
    };

    const updateSparklines = (container) => {
        if(container.children.length > 0) {
            container.removeChild(container.firstChild);
            const bar = document.createElement('div');
            bar.className = 'spark-bar';
            bar.style.height = `${random(20, 100)}%`;
            container.appendChild(bar);
        }
    };

    initSparklines(throughputSpark, 20);
    initSparklines(latencySpark, 20);
    initSparklines(errorSpark, 20);

    // Initialize Bar Chart
    const initChart = (container, count) => {
        container.innerHTML = '';
        for(let i=0; i<count; i++) {
            const wrapper = document.createElement('div');
            wrapper.className = 'chart-bar-container';
            const bar = document.createElement('div');
            bar.className = 'chart-bar';
            bar.style.height = `${random(10, 100)}%`;
            wrapper.appendChild(bar);
            container.appendChild(wrapper);
        }
    }
    initChart(ingestionChart, 24);

    const updateChart = () => {
        if(ingestionChart.children.length > 0) {
            ingestionChart.removeChild(ingestionChart.firstChild);
            const wrapper = document.createElement('div');
            wrapper.className = 'chart-bar-container';
            const bar = document.createElement('div');
            bar.className = 'chart-bar';
            bar.style.height = `${random(30, 100)}%`;
            wrapper.appendChild(bar);
            ingestionChart.appendChild(wrapper);
        }
    };

    // Update Metrics
    let currentThroughput = 12450;
    setInterval(() => {
        currentThroughput = currentThroughput + random(-500, 500);
        if(currentThroughput < 8000) currentThroughput = 8000;
        throughputVal.innerText = formatNumber(currentThroughput);
        
        latencyVal.innerText = Math.floor(random(35, 65));
        
        const err = random(0.001, 0.05).toFixed(3);
        errorVal.innerText = err;

        updateSparklines(throughputSpark);
        updateSparklines(latencySpark);
        updateSparklines(errorSpark);
    }, 1000);

    // Update Chart
    setInterval(updateChart, 1500);

    // Event Terminal Stream
    const logEvents = [
        "Partition [2] rebalance completed",
        "Kafka batch processed: 4500 records",
        "Spark job 'aggregate_events' finished in 1.2s",
        "Consumer group 'analytics_group' joined",
        "Committed offset 8490231",
        "Heartbeat received from node-04",
        "Schema validation passed for topic 'user_actions'"
    ];

    const generateLog = () => {
        const isError = Math.random() < 0.05;
        const msg = isError ? "ERROR: Connection timeout to broker-2" : logEvents[Math.floor(random(0, logEvents.length))];
        const logLine = document.createElement('div');
        logLine.className = `log-entry ${isError ? 'error' : ''}`;
        
        const timestamp = new Date().toISOString().split('T')[1].substring(0,8);
        logLine.innerText = `[${timestamp}] ${msg}`;
        
        terminal.prepend(logLine);

        if(terminal.children.length > 15) {
            terminal.removeChild(terminal.lastChild);
        }
    };

    setInterval(generateLog, 800);
});
