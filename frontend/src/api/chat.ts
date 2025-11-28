const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface ChatReply {
  reply: string;
}

export async function sendChatMessage(message: string): Promise<ChatReply> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Chat API failed");
    throw new Error(
      `Chat API request failed (${response.status}): ${errorText}`
    );
  }

  return response.json();
}

