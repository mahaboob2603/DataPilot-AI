import React from 'react';
import ReactPlotly from 'react-plotly.js';

// Vite CommonJS interop: sometimes default exports are nested in a .default property
const Plot = ReactPlotly.default || ReactPlotly;

function PlotlyChart({ chartJsonStr }) {
  if (!chartJsonStr) return null;

  try {
    const chartData = typeof chartJsonStr === 'string' ? JSON.parse(chartJsonStr) : chartJsonStr;
    
    // Ensure responsive layout
    const layout = {
      ...(chartData.layout || {}),
      autosize: true,
      margin: { t: 40, r: 20, l: 40, b: 40 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: '#e3e2e8', family: 'Inter, sans-serif' }
    };

    return (
      <div className="chart-wrapper" style={{ width: '100%', minHeight: '300px', padding: '16px 0' }}>
        <Plot
          data={chartData.data || []}
          layout={layout}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%', height: '100%' }}
          useResizeHandler={true}
        />
      </div>
    );
  } catch (err) {
    console.error("Failed to parse Plotly JSON or render", err);
    return <div className="error-text">Failed to render chart: {err.message}</div>;
  }
}

export default PlotlyChart;
