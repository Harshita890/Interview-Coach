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
