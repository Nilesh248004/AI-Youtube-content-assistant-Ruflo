const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

function getErrorMessage(payload) {
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }

  if (Array.isArray(payload?.detail)) {
    return payload.detail.map((item) => item.msg).join(" ");
  }

  return "The content package could not be generated.";
}

export async function generateContent(formData) {
  let response;

  try {
    response = await fetch(`${API_URL}/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });
  } catch {
    throw new Error(
      "Cannot reach the backend. Make sure FastAPI is running on port 8000.",
    );
  }

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(getErrorMessage(payload));
  }

  return payload;
}
