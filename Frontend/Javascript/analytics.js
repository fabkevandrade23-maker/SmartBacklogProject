async function loadAnalytics() {
<<<<<<< HEAD
  const res = await fetch("http://localhost:8000/analytics");
  const data = await res.json();

  console.log(data);
}
=======
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
>>>>>>> ea5a9878f07903e96f59f6dd44012f742124cbef
