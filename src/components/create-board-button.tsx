"use client";

import { useRouter } from "next/navigation";
import { Button } from "./ui/button";
import { Sparkles } from "lucide-react";

export function CreateBoardButton() {
  const router = useRouter();

  const handleCreateBoard = () => {
    const boardId = crypto.randomUUID().split("-")[0];
    router.push(`/board/${boardId}`);
  };

  return (
    <Button size="lg" onClick={handleCreateBoard}>
      <Sparkles className="mr-2" />
      Create a new board
    </Button>
  );
}
