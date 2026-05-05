document.querySelectorAll(".dropzone").forEach(zone => {

  zone.addEventListener("dragover", e => e.preventDefault());

  zone.addEventListener("drop", () => {
    const task = document.querySelector(".dragging");
    zone.appendChild(task);
  });

});