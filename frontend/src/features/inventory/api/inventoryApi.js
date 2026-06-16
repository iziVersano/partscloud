const API_BASE = "/api/v1";

export async function fetchSkus({ risk, ordering } = {}) {
  const params = new URLSearchParams();
  if (risk) params.set("risk", risk);
  if (ordering) params.set("ordering", ordering);

  const query = params.toString() ? `?${params.toString()}` : "";
  const response = await fetch(`${API_BASE}/skus${query}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch SKUs: ${response.status}`);
  }
  return response.json();
}

export async function updateSkuAction(sku, action) {
  const response = await fetch(`${API_BASE}/skus/${sku}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  if (!response.ok) {
    throw new Error(`Failed to update ${sku}: ${response.status}`);
  }
  return response.json();
}

export async function bulkUpdateSkuAction(skus, action) {
  const response = await fetch(`${API_BASE}/skus/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ skus, action }),
  });
  if (!response.ok) {
    throw new Error(`Failed to bulk update: ${response.status}`);
  }
  return response.json();
}
