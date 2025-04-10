import Plotly from 'plotly.js-dist';

window.renderPlotlyChart = function(containerId, dataJson) {
    const data = JSON.parse(dataJson);
    data.forEach(trace => {
        trace.mode = 'lines';
    });
    const layout = {
        title: 'Q-value Convergence',
        xaxis: { title: 'Episodes' },
        yaxis: { title: 'Average Q-value' }

    };
    const config = {
        responsive: true,
        displayModeBar: true,
        scrollZoom: true,
    };
    Plotly.newPlot(containerId, data, layout,config);
};

window.renderMutationChart = function(containerId, dataJson) {

    const data = JSON.parse(dataJson);

    const traces = data.mutationMethods.map((method) => {
        const counts = data.mutationCounts[method];
        if (!counts) {
            console.error("Mutation counts not found for method:", method); // Debugging
            return null;
        }
        const dataTypes = Object.keys(counts);
        const values = Object.values(counts);

        return {
            x: dataTypes,
            y: values,
            type: 'bar',
            name: method,
            marker: {
                color: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.6)`
            }
        };
    }).filter(trace => trace !== null); // Filter out null traces

    const layout = {
        title: 'Mutation Method Counts',
        barmode: 'group',
        xaxis: { title: 'Data Types' },
        yaxis: { title: 'Counts' },
        showlegend: true,
        legend: {
            x: 1,
            xanchor: 'left',
            y: 1
        }
    };

    Plotly.newPlot(containerId, traces, layout);
};

window.renderStateVisitsChart = function(containerId, dataJson) {

    const data = JSON.parse(dataJson);

    const states = data.states;
    const visitCounts = data.visitCounts;

    const colors = ['lightblue', 'green', 'yellow', 'orange', 'red'];

    const trace = {
        x: states,
        y: visitCounts,
        type: 'bar',
        marker: {
            color: colors
        },
        text: visitCounts.map(String),
        textposition: 'auto'
    };

    const layout = {
        title: 'Number of Visits to Each HTTP Status Code Range',
        xaxis: { title: 'HTTP Status Code Ranges' },
        yaxis: { title: 'Number of Visits' }
    };

    Plotly.newPlot(containerId, [trace], layout);
};

window.renderLearningCurveChart = function(containerId, dataJson) {

    const data = JSON.parse(dataJson);
    console.log(data)
    const xValues = Array.from({length: data.averageRewards.length}, (v, k) => k *data.windowSize/10);
    const yValues = data.averageRewards;

    const trace = {
        x: xValues,
        y: yValues,
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: 'blue' },
        line: { shape: 'spline' }

    };

    const layout = {
        title: 'Learning Curve',
        xaxis: { title: 'Episodes' },
        yaxis: { title: 'Average Reward' }
    };

    Plotly.newPlot(containerId, [trace], layout);
};

window.renderEpisodeDurationsChart = function(containerId, dataJson) {
    const data = JSON.parse(dataJson);
    const xValues = Array.from({length: data.episodeDurations.length}, (v, k) => k + 1);
    const yValues = data.episodeDurations;

    const trace = {
        x: xValues,
        y: yValues,
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: 'red' },
        line: { shape: 'spline' }
    };

    const layout = {
        title: 'Episode Durations',
        xaxis: { title: 'Episode' },
        yaxis: { title: 'Duration (seconds)' }
    };

    Plotly.newPlot(containerId, [trace], layout);
};

window.renderExplorationExploitationRatioChart = function(containerId, dataJson) {
    const data = JSON.parse(dataJson);
    const xValues = Array.from({length: data.explorationRates.length}, (v, k) => k + 1);
    const explorationTrace = {
        x: xValues,
        y: data.explorationRates,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Exploration Rate',
        marker: { color: 'blue' }
    };

    const exploitationTrace = {
        x: xValues,
        y: data.exploitationRates,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Exploitation Rate',
        marker: { color: 'red' }
    };

    const layout = {
        title: 'Exploration vs. Exploitation Ratio',
        xaxis: { title: 'Episodes' },
        yaxis: { title: 'Rate' }
    };

    Plotly.newPlot(containerId, [explorationTrace, exploitationTrace], layout);
};
