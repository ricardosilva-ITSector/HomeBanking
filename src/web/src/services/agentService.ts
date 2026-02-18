/**
 * Agent service for communicating with the AI banking assistant.
 * Handles API calls to the agent HTTP server.
 */

/**
 * Base URL for agent API requests.
 * Uses VITE_AGENT_URL environment variable or defaults to http://localhost:8087.
 */
const AGENT_BASE_URL = import.meta.env.VITE_AGENT_URL || "http://localhost:8087";

/**
 * Error class for agent-specific errors.
 */
export class AgentError extends Error {
  status?: number;
  
  constructor(message: string, status?: number) {
    super(message);
    this.name = "AgentError";
    this.status = status;
  }
}

/**
 * Send a message to the agent and get a streaming response.
 * @param message - User message text
 * @param threadId - Optional thread ID for conversation continuity
 * @returns AsyncGenerator yielding response chunks
 */
export async function* sendMessageToAgent(
  message: string,
  threadId?: string
): AsyncGenerator<string, void, unknown> {
  try {
    const response = await fetch(`${AGENT_BASE_URL}/agent/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        input: message,
        thread_id: threadId,
      }),
    });

    if (!response.ok) {
      throw new AgentError(
        `Agent request failed: ${response.statusText}`,
        response.status
      );
    }

    if (!response.body) {
      throw new AgentError("No response body from agent");
    }

    // Stream the response
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process server-sent events (SSE)
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6); // Remove "data: " prefix
            
            try {
              const event = JSON.parse(data);
              
              if (event.type === "text" && event.text) {
                // Unescape the text
                const text = event.text
                  .replace(/\\n/g, "\n")
                  .replace(/\\'/g, "'");
                yield text;
              } else if (event.type === "error") {
                throw new AgentError(event.error || "Agent error");
              }
              // Ignore thread_id and done events
            } catch (e) {
              // Skip invalid JSON
              console.warn("Failed to parse SSE data:", data, e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  } catch (error) {
    if (error instanceof AgentError) {
      throw error;
    }
    throw new AgentError(
      error instanceof Error ? error.message : "Failed to send message to agent"
    );
  }
}

/**
 * Check if the agent service is available.
 * @returns Promise<boolean> - true if agent is reachable
 */
export async function checkAgentHealth(): Promise<boolean> {
  try {
    // Try to connect to the agent server health endpoint
    const response = await fetch(`${AGENT_BASE_URL}/health`, {
      method: "GET",
      signal: AbortSignal.timeout(3000),
    });
    
    if (!response.ok) {
      return false;
    }
    
    const data = await response.json();
    return data.status === "healthy" || data.status === "degraded";
  } catch {
    return false;
  }
}
