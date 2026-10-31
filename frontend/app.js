const API_URL = "https://ai-pro-trader-api.vercel.app";

const upload = document.getElementById("chart");
const preview = document.getElementById("preview");
const analyzeBtn = document.getElementById("analyze");
const result = document.getElementById("result");

let selectedFile = null;

upload.addEventListener("change", () => {
  selectedFile = upload.files[0];

  if (!selectedFile) return;

  preview.src = URL.createObjectURL(selectedFile);
  preview.style.display = "block";
  result.textContent = "Gambar siap dianalisis.";
});

analyzeBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    result.textContent = "Upload screenshot chart terlebih dahulu.";
    return;
  }

  analyzeBtn.disabled = true;
  result.textContent = "Sedang menganalisis chart...";

  try {
    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Analisis gagal.");
    }

    result.textContent = JSON.stringify(data, null, 2);

  } catch (error) {
    result.textContent = "Gagal: " + error.message;
  } finally {
    analyzeBtn.disabled = false;
  }
});
