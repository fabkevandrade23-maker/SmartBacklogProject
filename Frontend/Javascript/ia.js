async function runAI() {

  const tasks = ["Task 1", "Task 2"];

  const res = await fetch("http://localhost:8000/ai/prioritize", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ tasks })
  });

  const data = await res.json();

  alert(data.result);
}
