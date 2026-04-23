async function loadAnalytics() {
  const res = await fetch("/analytics");
  const data = await res.json();

  new Chart(document.getElementById("chart"), {
    type: "bar",
    data: {
      labels: ["To Do", "Progress", "Done"],
      datasets: [{
        data: [data.todo, data.progress, data.done]
      }]
    }
  });
}

loadAnalytics();
