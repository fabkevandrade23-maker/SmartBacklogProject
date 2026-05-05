<<<<<<< HEAD
async function runAI() {

  const tasks = ["Task 1", "Task 2"];

  const res = await fetch("http://localhost:8000/ai/prioritize", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
=======
async function openAI() {
  const tasks = [...document.querySelectorAll(".task")]
    .map(t => t.innerText);

  const res = await fetch("/ai/prioritize", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
>>>>>>> ea5a9878f07903e96f59f6dd44012f742124cbef
    body: JSON.stringify({ tasks })
  });

  const data = await res.json();
<<<<<<< HEAD

=======
>>>>>>> ea5a9878f07903e96f59f6dd44012f742124cbef
  alert(data.result);
}