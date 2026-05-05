async function loadAnalytics() {
  const res = await fetch("http://localhost:8000/analytics");
  const data = await res.json();

  console.log(data);
}
