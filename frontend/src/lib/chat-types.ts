/** TypeScript types for chat state — Phase 3 Part 3 */

export interface ToolCallInfo {
  tool: string;
  arguments: Record<string, unknown>;
}

export interface ChatState {
  isOpen: boolean;
  threadId: string | null;
}
