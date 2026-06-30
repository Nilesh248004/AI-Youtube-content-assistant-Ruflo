const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const REQUEST_TIMEOUT_MS = 120_000;

function getErrorMessage(payload) {
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }

  if (Array.isArray(payload?.detail)) {
    return payload.detail.map((item) => item.msg).join(" ");
  }

  return "The content package could not be generated.";
}

async function requestJson(path, options = {}) {
  const controller = new AbortController();
  const timeout = window.setTimeout(
    () => controller.abort(),
    REQUEST_TIMEOUT_MS,
  );

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("The request timed out. Please try again.");
    }
    throw new Error(
      "Cannot reach the backend. Make sure FastAPI is running on port 8000.",
    );
  } finally {
    window.clearTimeout(timeout);
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(getErrorMessage(payload));
  }
  return payload;
}

export function getServiceInfo() {
  return requestJson("/");
}

export function generateContent(formData) {
  return requestJson("/generate", {
    method: "POST",
    body: JSON.stringify(formData),
  });
}

export function regenerateContent(section, currentPackage) {
  return requestJson(`/regenerate/${section}`, {
    method: "POST",
    body: JSON.stringify({ current_package: currentPackage }),
  });
}
