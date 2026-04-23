async function openAI() {
  const tasks = [...document.querySelectorAll(".task")]
    .map(t => t.innerText);

  const res = await fetch("/ai/prioritize", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ tasks })
  });

  const data = await res.json();
  alert(data.result);
}