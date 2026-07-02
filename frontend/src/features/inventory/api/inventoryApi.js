const API_BASE = "/api/v1";

export async function fetchSkus({ risk, search, ordering, page = 1, pageSize = 10 } = {}) {
  const params = new URLSearchParams();
  if (risk) params.set("risk", risk);
  if (search) params.set("search", search);
  if (ordering) params.set("ordering", ordering);
  params.set("page", page);
  params.set("page_size", pageSize);

  const response = await fetch(`${API_BASE}/skus?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch SKUs: ${response.status}`);
  }
  return response.json();
}

export async function fetchStats() {
  const response = await fetch(`${API_BASE}/skus/stats`);
  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.status}`);
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
