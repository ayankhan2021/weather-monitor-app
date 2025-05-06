// Global variables to store chart instances
let tempChart, humidityChart, airQualityChart;

// Initialize charts
function initCharts() {
  const tempCtx = document.getElementById('tempChart').getContext('2d');
  const humidityCtx = document.getElementById('humidityChart').getContext('2d');
  const airQualityCtx = document.getElementById('airQualityChart').getContext('2d');
  
  tempChart = new Chart(tempCtx, {
    type: 'line',
    data: { 
      labels: [], 
      datasets: [{
        label: 'Temperature (°C)',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        borderWidth: 2,
        tension: 0.1,
        fill: true
      }]
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Temperature (°C)'
          }
        }
      }
    }
  });
  
  humidityChart = new Chart(humidityCtx, {
    type: 'line',
    data: { 
      labels: [], 
      datasets: [{
        label: 'Humidity (%)',
        data: [],
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        borderWidth: 2,
        tension: 0.1,
        fill: true
      }]
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Humidity (%)'
          }
        }
      }
    }
  });
  
  airQualityChart = new Chart(airQualityCtx, {
    type: 'line',
    data: { 
      labels: [], 
      datasets: [{
        label: 'Air Quality (PPM)',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        borderWidth: 2,
        tension: 0.1,
        fill: true
      }]
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Time'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Air Quality (PPM)'
          }
        }
      }
    }
  });
}

// // Update current sensor readings
// async function updateCurrentReadings() {
//   try {
//     const response = await axios.get('/get-latest');
//     const data = response.data;
    
//     document.getElementById('temperature').textContent = data.temperature?.toFixed(1) || '--';
//     document.getElementById('humidity').textContent = data.humidity?.toFixed(1) || '--';
//     document.getElementById('airQuality').textContent = data.air_quality?.toFixed(1) || '--';
//     document.getElementById('timestamp').textContent = 
//       data.timestamp ? new Date(data.timestamp).toLocaleString() : '--';
//   } catch (error) {
//     console.error('Error fetching current data:', error);
//     document.getElementById('temperature').textContent = 'Error';
//     document.getElementById('humidity').textContent = 'Error';
//     document.getElementById('airQuality').textContent = 'Error';
//     document.getElementById('timestamp').textContent = 'Error';
//   }
// }



// async function updateCurrentReadings() {
//     try {
//       const response = await axios.get('/get-latest');
//       const data = response.data;
      
//       // Update sensor values
//       document.getElementById('temperature').textContent = data.temperature?.toFixed(1) || '--';
//       document.getElementById('humidity').textContent = data.humidity?.toFixed(1) || '--';
//       document.getElementById('airQuality').textContent = data.air_quality?.toFixed(1) || '--';
      
//       // Add this timestamp formatting code:
//       if (data.timestamp) {
//         const formattedDate = new Date(data.timestamp).toLocaleString();
//         document.getElementById('timestamp').textContent = formattedDate;
//       } else {
//         document.getElementById('timestamp').textContent = '--';
//       }
      
//     } catch (error) {
//       console.error('Error fetching current data:', error);
//       document.getElementById('temperature').textContent = 'Error';
//       document.getElementById('humidity').textContent = 'Error';
//       document.getElementById('airQuality').textContent = 'Error';
//       document.getElementById('timestamp').textContent = 'Error';
//     }
//   }

async function updateCurrentReadings() {
    try {
      const response = await axios.get('/get-latest');
      const data = response.data;
      
      document.getElementById('temperature').textContent = data.temperature?.toFixed(1) || '--';
      document.getElementById('humidity').textContent = data.humidity?.toFixed(1) || '--';
      document.getElementById('airQuality').textContent = data.air_quality?.toFixed(1) || '--';
      
      // Updated timestamp formatting to match your graph format
      if (data.timestamp) {
        const date = new Date(data.timestamp);
        // Format as "YYYY-MM-DD HH:MM:SS" to match graphs
        // const formattedDate = date.toISOString().replace('T', ' ').split('.')[0];
        const formattedDate = date.toLocaleString('en-GB', { timeZone: 'Asia/Karachi' });

        document.getElementById('timestamp').textContent = formattedDate;
      } else {
        document.getElementById('timestamp').textContent = '--';
      }
    } catch (error) {
      console.error('Error fetching current data:', error);
      document.getElementById('temperature').textContent = 'Error';
      document.getElementById('humidity').textContent = 'Error';
      document.getElementById('airQuality').textContent = 'Error';
      document.getElementById('timestamp').textContent = 'Error';
    }
  }

//   function formatRelativeTime(timestamp) {
//     const now = new Date();
//     const recordTime = new Date(timestamp);
//     const diffMinutes = Math.round((now - recordTime) / 60000);
    
//     if (diffMinutes < 1) return "Just now";
//     if (diffMinutes === 1) return "1 minute ago";
//     return `${diffMinutes} minutes ago`;
//   }
  
//   // Usage in updateCharts():
//   const relativeTimes = data.timestamps.map(formatRelativeTime);
//   tempChart.data.labels = relativeTimes;
// Update historical data charts
async function updateCharts() {
  try {
    const response = await axios.get('/get-history');
    const data = response.data;

    console.log("Current time:", new Date().toLocaleTimeString());
    console.log("API response times:", data.timestamps.map(t => new Date(t).toLocaleTimeString()));
    console.log("Time difference:", 
      (new Date() - new Date(data.timestamps[data.timestamps.length-1]))/60000, "minutes");
    
    // const adjustedTimestamps = data.timestamps.map(timestamp => {
    //     const date = new Date(timestamp);
    //     date.setMinutes(date.getMinutes() + 1);  // Add 1 minute
    //     return date.toLocaleTimeString();  // Or your preferred format
    //   });

    // Update temperature chart
    if (data.timestamps && data.temperatures) {
      tempChart.data.labels = data.timestamps;
      tempChart.data.datasets[0].data = data.temperatures;
      tempChart.update();
    }
    
    // Update humidity chart
    if (data.timestamps && data.humidities) {
      humidityChart.data.labels = data.timestamps;
      humidityChart.data.datasets[0].data = data.humidities;
      humidityChart.update();
    }
    
    // Update air quality chart
    if (data.timestamps && data.air_qualities) {
      airQualityChart.data.labels = data.timestamps;
      airQualityChart.data.datasets[0].data = data.air_qualities;
      airQualityChart.update();
    }
  } catch (error) {
    console.error('Error fetching historical data:', error);
  }
}

      
      // Add 1 minute to each timestamp to compensate
     
      
// Refresh all data
async function refreshData() {
  await updateCurrentReadings();
  await updateCharts();
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  refreshData();
  
  // Set up auto-refresh every 30 seconds
  setInterval(refreshData, 30000);
  
  // Manual refresh button
  document.getElementById('refreshBtn').addEventListener('click', refreshData);
});


