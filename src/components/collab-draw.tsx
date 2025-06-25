"use client";

import { useEffect, useRef, useState } from "react";
import {
  Pen,
  Square,
  Circle,
  Minus,
  Type,
  Eraser,
  Undo,
  Redo,
  Trash2,
  Download,
  Image as ImageIcon,
  Sparkles,
  Loader2,
  Share2,
  Save,
  CloudDownload,
} from "lucide-react";
import { collection, query, orderBy, onSnapshot, where, Timestamp } from "firebase/firestore";

import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Tool, DrawingAction, Point } from "@/lib/types";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { Card } from "./ui/card";
import { Label } from "./ui/label";
import { saveCanvas, loadCanvas, addDrawingAction } from "@/app/actions";
import { db } from "@/lib/firebase";

export default function CollabDraw({ boardId }: { boardId: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const snapshotRef = useRef<ImageData | null>(null);
  const startPointRef = useRef<Point | null>(null);
  const textInputRef = useRef<HTMLInputElement>(null);

  const [tool, setTool] = useState<Tool>("pen");
  const [color, setColor] = useState("#000000");
  const [size, setSize] = useState(5);
  const [isDrawing, setIsDrawing] = useState(false);
  const [history, setHistory] = useState<ImageData[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [background, setBackground] = useState<string | null>(null);
  
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [aiPrompt, setAiPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  const [isTextMode, setIsTextMode] = useState(false);
  const [textPosition, setTextPosition] = useState<Point | null>(null);
  const [textValue, setTextValue] = useState("");

  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  const [clientId] = useState(() => crypto.randomUUID());
  const [lastSaveTime, setLastSaveTime] = useState<Date | null>(null);

  const { toast } = useToast();

  const getContext = () => canvasRef.current?.getContext("2d") as CanvasRenderingContext2D;

  const saveToHistory = () => {
    const context = getContext();
    if (!context || !context.canvas.width) return;
    const imageData = context.getImageData(0, 0, context.canvas.width, context.canvas.height);
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(imageData);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const restoreFromHistory = (index: number) => {
    if (index < 0 || index >= history.length) return;
    const context = getContext();
    const imageData = history[index];
    context.putImageData(imageData, 0, 0);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = getContext();

    const resizeCanvas = () => {
        const currentDrawing = context.getImageData(0,0, canvas.width, canvas.height);
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        context.putImageData(currentDrawing, 0, 0);
    }
    
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    handleLoad(true); // Auto-load on initial mount
    
    return () => window.removeEventListener('resize', resizeCanvas);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!boardId || !lastSaveTime) return;

    const q = query(
      collection(db, 'boards', boardId, 'actions'),
      where('timestamp', '>', Timestamp.fromDate(lastSaveTime)),
      orderBy('timestamp')
    );

    const unsubscribe = onSnapshot(q, (snapshot) => {
      snapshot.docChanges().forEach((change) => {
        if (change.type === 'added') {
          const action = change.doc.data() as DrawingAction;
          if (action.clientId !== clientId) {
            drawAction(action, false);
          }
        }
      });
    });

    return () => unsubscribe();
  }, [boardId, clientId, lastSaveTime]);


  const drawAction = (action: DrawingAction, isLocal: boolean) => {
    const context = getContext();
    if (!context) return;

    context.strokeStyle = action.tool === "eraser" ? "#F5F5F5" : action.color;
    context.lineWidth = action.size;
    context.lineCap = "round";
    context.lineJoin = "round";
    context.globalCompositeOperation = action.tool === 'eraser' ? 'destination-out' : 'source-over';
    
    switch (action.tool) {
      case "pen":
      case "line":
        context.beginPath();
        context.moveTo(action.from.x, action.from.y);
        context.lineTo(action.to.x, action.to.y);
        context.stroke();
        break;
      case "rectangle":
        context.beginPath();
        context.strokeRect(action.from.x, action.from.y, action.to.x - action.from.x, action.to.y - action.from.y);
        break;
      case "circle":
        const radius = Math.sqrt(Math.pow(action.to.x - action.from.x, 2) + Math.pow(action.to.y - action.from.y, 2));
        context.beginPath();
        context.arc(action.from.x, action.from.y, radius, 0, 2 * Math.PI);
        context.stroke();
        break;
      case "text":
        if (action.text) {
          context.font = `${action.size * 4}px Inter`;
          context.fillStyle = action.color;
          context.globalCompositeOperation = 'source-over';
          context.fillText(action.text, action.from.x, action.from.y);
        }
        break;
    }
    
    if (isLocal && action.tool !== 'pen' && action.tool !== 'eraser') {
      addDrawingAction(boardId, { ...action, clientId });
    }
  };
  
  const getPoint = (e: React.MouseEvent<HTMLCanvasElement>): Point => ({ x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY });

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const point = getPoint(e);
    if (tool === 'text') {
        if(isTextMode) {
            handleTextSubmit();
        } else {
            setIsTextMode(true);
            setTextPosition(point);
        }
        return;
    }

    setIsDrawing(true);
    startPointRef.current = point;
    const context = getContext();
    snapshotRef.current = context.getImageData(0, 0, context.canvas.width, context.canvas.height);
  };
  
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !startPointRef.current) return;
    const currentPoint = getPoint(e);
    
    const action: DrawingAction = {
      tool,
      from: startPointRef.current,
      to: currentPoint,
      color,
      size,
    };
    
    if(tool === 'pen' || tool === 'eraser') {
      drawAction(action, true);
      addDrawingAction(boardId, { ...action, clientId });
      startPointRef.current = currentPoint;
    } else {
      if (snapshotRef.current) {
        getContext().putImageData(snapshotRef.current, 0, 0);
      }
      drawAction(action, false);
    }
  };
  
  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !startPointRef.current) return;
    
    const endPoint = getPoint(e);
    const action: DrawingAction = {
        tool,
        from: startPointRef.current,
        to: endPoint,
        color,
        size,
        clientId
    }

    if (tool !== 'pen' && tool !== 'eraser') {
        drawAction(action, true);
    }
    
    setIsDrawing(false);
    saveToHistory();
    startPointRef.current = null;
    snapshotRef.current = null;
  };

  const handleUndo = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      restoreFromHistory(newIndex);
    }
  };
  
  const handleRedo = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      restoreFromHistory(newIndex);
    }
  };

  const handleClear = () => {
    const context = getContext();
    context.clearRect(0, 0, context.canvas.width, context.canvas.height);
    saveToHistory();
  };
  
  const handleExport = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const dataUrl = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = `collab-draw-${boardId}.png`;
    a.click();
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            setBackground(event.target?.result as string);
        };
        reader.readAsDataURL(file);
    }
  };
  
  const handleGenerateAI = async () => {
    if (!aiPrompt) return;
    setIsGenerating(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    const hint = aiPrompt.split(" ").slice(0, 2).join(" ");
    const generatedBg = `https://placehold.co/1920x1080.png?text=${encodeURIComponent(aiPrompt)}`;
    setBackground(generatedBg);
    canvasRef.current?.setAttribute('data-ai-hint', hint);
    setIsGenerating(false);
    setIsAiModalOpen(false);
    setAiPrompt("");
  };

  const handleTextSubmit = () => {
    if (!textValue || !textPosition) {
        setIsTextMode(false);
        setTextValue("");
        return;
    }
    const action: DrawingAction = {
        tool: 'text',
        from: textPosition,
        to: textPosition,
        color,
        size,
        text: textValue,
        clientId,
    }

    drawAction(action, true);
    addDrawingAction(boardId, action);
    
    setIsTextMode(false);
    setTextValue("");
    setTextPosition(null);
    saveToHistory();
  };

  useEffect(() => {
    if (isTextMode && textInputRef.current) {
      textInputRef.current.focus();
    }
  }, [isTextMode]);
  
  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    toast({
      title: "Link Copied!",
      description: "You can now share the board with others.",
    });
  };

  const handleSave = async () => {
    if (!canvasRef.current || isSaving) return;
    setIsSaving(true);
    try {
        const dataUrl = canvasRef.current.toDataURL("image/png");
        const result = await saveCanvas(boardId, dataUrl);
        if (result.success && result.updatedAt) {
            setLastSaveTime(result.updatedAt);
            toast({
                title: "Board Saved!",
                description: "Your masterpiece is safe in the cloud.",
            });
        } else {
            throw new Error(result.error);
        }
    } catch (error: any) {
        toast({
            variant: "destructive",
            title: "Uh oh! Something went wrong.",
            description: error.message || "Could not save your board. Please try again.",
        });
    } finally {
        setIsSaving(false);
    }
  };

  const handleLoad = async (isInitialLoad = false) => {
    if (!canvasRef.current || isLoading) return;
    setIsLoading(true);
    try {
      const result = await loadCanvas(boardId);
      if (result.success && result.data) {
        const img = new Image();
        img.onload = () => {
          const context = getContext();
          context.clearRect(0, 0, context.canvas.width, context.canvas.height);
          context.drawImage(img, 0, 0, context.canvas.width, context.canvas.height);
          saveToHistory();
          setLastSaveTime(result.data.updatedAt);
          if (!isInitialLoad) {
            toast({
              title: "Board Loaded",
              description: "The saved state has been loaded.",
            });
          }
        };
        img.src = result.data.canvasState;
      } else if (result.success && !result.data) {
        setLastSaveTime(new Date(0)); // Start from epoch if no save exists
        if (!isInitialLoad) {
          toast({
            title: "New Board",
            description: "This board is empty. Start drawing!",
          });
        }
      } else {
        throw new Error(result.error);
      }
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Uh oh! Something went wrong.",
        description: error.message || "Could not load the board.",
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const tools: { name: Tool; icon: React.ElementType }[] = [
    { name: "pen", icon: Pen },
    { name: "rectangle", icon: Square },
    { name: "circle", icon: Circle },
    { name: "line", icon: Minus },
    { name: "text", icon: Type },
    { name: "eraser", icon: Eraser },
  ];

  return (
    <div className="relative w-full h-screen overflow-hidden" style={{ background: background ? `url(${background}) no-repeat center center / cover` : '#F5F5F5' }}>
      {isLoading && <div className="absolute inset-0 bg-white/80 z-50 flex items-center justify-center"><Loader2 className="w-12 h-12 animate-spin text-primary" /></div>}
      <h1 className="absolute top-4 left-4 text-2xl font-bold text-primary font-headline">CollabDraw</h1>
      <Card className="absolute top-4 left-1/2 -translate-x-1/2 z-10 p-2 flex items-center gap-2 shadow-lg">
        {tools.map(({ name, icon: Icon }) => (
          <Button
            key={name}
            variant={tool === name ? "default" : "ghost"}
            size="icon"
            onClick={() => setTool(name)}
            aria-label={name}
          >
            <Icon className="w-5 h-5" />
          </Button>
        ))}

        <Separator orientation="vertical" className="h-8 mx-2" />

        <Popover>
            <PopoverTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Color Picker">
                    <div className="w-6 h-6 rounded-full border" style={{ backgroundColor: color }} />
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-2">
                <input type="color" value={color} onChange={(e) => setColor(e.target.value)} className="w-16 h-10 border-none cursor-pointer" />
            </PopoverContent>
        </Popover>

        <Popover>
            <PopoverTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Brush Size">{size}</Button>
            </PopoverTrigger>
            <PopoverContent className="w-40 p-4">
                <Slider defaultValue={[size]} max={50} step={1} onValueChange={([val]) => setSize(val)} />
            </PopoverContent>
        </Popover>

        <Separator orientation="vertical" className="h-8 mx-2" />
        
        <Button variant="ghost" size="icon" onClick={handleUndo} disabled={historyIndex <= 0} aria-label="Undo"><Undo /></Button>
        <Button variant="ghost" size="icon" onClick={handleRedo} disabled={historyIndex >= history.length - 1} aria-label="Redo"><Redo /></Button>
        <Button variant="ghost" size="icon" onClick={handleClear} aria-label="Clear Canvas"><Trash2 /></Button>
      </Card>
      
      <Card className="absolute top-4 right-4 z-10 p-2 flex items-center gap-2 shadow-lg">
        <Button variant="ghost" size="icon" onClick={handleSave} disabled={isSaving} aria-label="Save Board">
            {isSaving ? <Loader2 className="animate-spin" /> : <Save />}
        </Button>
        <Button variant="ghost" size="icon" onClick={() => handleLoad(false)} disabled={isLoading} aria-label="Load Board">
            {isLoading ? <Loader2 className="animate-spin" /> : <CloudDownload />}
        </Button>

        <Separator orientation="vertical" className="h-8 mx-2" />
        
        <input type="file" id="image-upload" className="hidden" accept="image/*" onChange={handleImageUpload} />
        <Button variant="ghost" size="icon" onClick={() => document.getElementById('image-upload')?.click()} aria-label="Upload Background"><ImageIcon /></Button>
        <Button variant="ghost" size="icon" onClick={() => setIsAiModalOpen(true)} aria-label="Generate AI Background"><Sparkles /></Button>
        <Button variant="ghost" size="icon" onClick={handleExport} aria-label="Download"><Download /></Button>
        <Button onClick={handleShare} size="sm"><Share2 className="mr-2 h-4 w-4"/>Share</Button>
      </Card>

      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="w-full h-full cursor-crosshair"
      />

      {isTextMode && textPosition && (
        <div style={{ position: 'absolute', left: textPosition.x, top: textPosition.y }}>
            <Input
                ref={textInputRef}
                type="text"
                value={textValue}
                onChange={(e) => setTextValue(e.target.value)}
                onBlur={handleTextSubmit}
                onKeyDown={(e) => e.key === 'Enter' && handleTextSubmit()}
                className="bg-transparent border p-1"
                style={{ fontSize: `${size * 4}px`, color: color, width: 'auto' }}
            />
        </div>
      )}

      <Dialog open={isAiModalOpen} onOpenChange={setIsAiModalOpen}>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>Generate Background with AI</DialogTitle>
                <DialogDescription>Describe the background you want to create for your session.</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
                <Label htmlFor="ai-prompt">Prompt</Label>
                <Input id="ai-prompt" value={aiPrompt} onChange={(e) => setAiPrompt(e.target.value)} placeholder="e.g., a serene forest landscape" />
            </div>
            <DialogFooter>
                <Button onClick={handleGenerateAI} disabled={isGenerating}>
                    {isGenerating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                    Generate
                </Button>
            </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
