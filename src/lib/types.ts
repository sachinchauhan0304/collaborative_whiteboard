export type Tool = "pen" | "rectangle" | "circle" | "line" | "eraser" | "text";

export interface Point {
  x: number;
  y: number;
}

export interface DrawingAction {
  tool: Tool;
  from: Point;
  to: Point;
  color: string;
  size: number;
  text?: string;
  clientId?: string;
}
