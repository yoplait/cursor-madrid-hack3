const API_BASE = window.API_BASE || "http://127.0.0.1:8000";

const form = document.getElementById("form");
const fileInput = document.getElementById("file");
const confInput = document.getElementById("conf");
const output = document.getElementById("output");
const image = document.getElementById("image");

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (!file) return;
  image.hidden = false;
  image.src = URL.createObjectURL(file);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files?.[0];
  if (!file) return;

  output.textContent = "Detectando…";
  const body = new FormData();
  body.append("file", file);

  const url = new URL(`${API_BASE}/detect`);
  url.searchParams.set("conf", confInput.value || "0.25");

  try {
    const response = await fetch(url, { method: "POST", body });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || response.statusText);
    }
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = `Error: ${error.message}`;
  }
});
