const API_URL = "https://ai-pro-trader-api.vercel.app";

const upload = document.getElementById("chart");
const preview = document.getElementById("preview");
const button = document.getElementById("analyze");
const status = document.getElementById("status");
const result = document.getElementById("result");
const signal = document.getElementById("signal");
const details = document.getElementById("details");

let selectedFile = null;

upload.addEventListener("change", () => {
  selectedFile = upload.files[0];
  if (!selectedFile) return;

  preview.src = URL.createObjectURL(selectedFile);
  status.textContent = "Screenshot siap dianalisis.";
});

button.addEventListener("click", async () => {
  if (!selectedFile) {
    status.textContent = "Upload screenshot terlebih dahulu.";
    return;
  }

  button.disabled = true;
  status.textContent = "AI sedang menganalisis...";

  try {
    const form = new FormData();
    form.append("file", selectedFile);

    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      body: form
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Analisis gagal.");
    }

    signal.textContent = data.signal || "WAIT";
    details.textContent = JSON.stringify(data, null, 2);
    result.hidden = false;
    status.textContent = "Analisis selesai.";

  } catch (error) {
    status.textContent = "Gagal: " + error.message;
  } finally {
    button.disabled = false;
  }
});
