async function login() {
  const res = await fetch("http://localhost:8000/auth/login", {
    method: "POST"
  });

  const data = await res.json();
  localStorage.setItem("token", data.token);
}