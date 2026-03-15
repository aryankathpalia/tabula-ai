import { error } from "@sveltejs/kit";

export async function load({ params, fetch }) {

  const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/${params.id}`);

  if (!res.ok) {
    throw error(res.status, "Failed to load document");
  }

  const documentData = await res.json();

  return { documentData };
}