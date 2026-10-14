(() => {
  const dataNode = document.getElementById("chart-data");
  if (!dataNode || typeof Chart === "undefined") return;

  let data;
  try {
    data = JSON.parse(dataNode.textContent);
  } catch (error) {
    console.error("Unable to read dashboard chart data.", error);
    return;
  }

  const statusCanvas = document.getElementById("statusChart");
  if (statusCanvas) {
    const statusValues = data.status.values || [0, 0, 0];
    new Chart(statusCanvas, {
      type: "doughnut",
      data: {
        labels: data.status.labels,
        datasets: [{
          data: statusValues,
          backgroundColor: ["#25bd9a", "#6d5dfc", "#ffbd59"],
          borderWidth: 0,
          hoverOffset: 7,
          borderRadius: 5,
          spacing: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "76%",
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#202541",
            padding: 11,
            displayColors: true,
            callbacks: {
              label(context) {
                const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
                const percent = total ? Math.round(context.raw * 100 / total) : 0;
                return ` ${context.label}: ${context.raw} (${percent}%)`;
              }
            }
          }
        }
      }
    });
  }

  const priorityCanvas = document.getElementById("priorityChart");
  if (priorityCanvas) {
    new Chart(priorityCanvas, {
      type: "bar",
      data: {
        labels: data.priority.labels,
        datasets: [{
          label: "Tasks",
          data: data.priority.values,
          backgroundColor: ["#dcd8ff", "#c9c3ff", "#aca3ff", "#8d7fff", "#6654f5"],
          borderRadius: 7,
          borderSkipped: false,
          maxBarThickness: 35
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#202541",
            padding: 11,
            callbacks: { label: context => ` ${context.raw} task${context.raw === 1 ? "" : "s"}` }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            border: { display: false },
            ticks: { color: "#9299ad", font: { family: "DM Sans", size: 10 } }
          },
          y: {
            beginAtZero: true,
            ticks: { precision: 0, stepSize: 1, color: "#a0a6b7", font: { family: "DM Sans", size: 10 }, padding: 8 },
            grid: { color: "#f0f1f7", drawTicks: false },
            border: { display: false }
          }
        }
      }
    });
  }
})();
