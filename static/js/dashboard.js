const chartNode = document.getElementById("scoreChart");

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
          backgroundColor: ["#2563eb", "#0f9f6e", "#d97706", "#7c3aed"],
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
