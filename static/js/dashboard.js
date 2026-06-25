const chartNode = document.getElementById("scoreChart");
const historyChartNode = document.getElementById("historyChart");

if (chartNode && window.Chart) {
  const scores = [
    Number(chartNode.dataset.confidence),
    Number(chartNode.dataset.communication),
    Number(chartNode.dataset.sentiment),
    Number(chartNode.dataset.quality),
  ];

  new Chart(chartNode, {
    type: "bar",
    data: {
      labels: ["Confidence", "Communication", "Sentiment", "Response Quality"],
      datasets: [
        {
          label: "Score",
          data: scores,
          backgroundColor: ["#facc15", "#22c55e", "#fde68a", "#15803d"],
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            stepSize: 20,
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });
}

if (historyChartNode && window.Chart) {
  const labels = JSON.parse(historyChartNode.dataset.labels || "[]");
  const scores = JSON.parse(historyChartNode.dataset.scores || "[]");

  new Chart(historyChartNode, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Overall Score",
          data: scores,
          borderColor: "#facc15",
          backgroundColor: "rgba(250, 204, 21, 0.18)",
          tension: 0.25,
          fill: true,
          pointBackgroundColor: "#22c55e",
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
        },
      },
    },
  });
}
