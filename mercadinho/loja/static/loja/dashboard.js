const canvas = document.getElementById("pedidos-mes");
const dados = JSON.parse(document.getElementById("dados-pedidos-mes").textContent);

if (canvas && window.Chart) {
  new window.Chart(canvas, {
    type: "bar",
    data: {
      labels: dados.map(({ mes }) => mes),
      datasets: [{
        label: "Pedidos",
        data: dados.map(({ total }) => total),
        backgroundColor: "#487a65",
        borderRadius: 5,
        maxBarThickness: 56,
      }],
    },
    options: {
      maintainAspectRatio: false,
      animation: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, ticks: { precision: 0 } },
      },
    },
  });
}
