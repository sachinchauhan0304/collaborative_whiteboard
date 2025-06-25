import { CreateBoardButton } from '@/components/create-board-button';
import { Button } from '@/components/ui/button';
import { Pen, Share2 } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="p-4 border-b">
        <h1 className="text-2xl font-bold text-primary font-headline">CollabDraw</h1>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center text-center p-4">
        <div className="max-w-2xl">
          <div className="inline-block bg-primary/10 p-4 rounded-full mb-6">
            <Pen className="w-12 h-12 text-primary" />
          </div>
          <h2 className="text-4xl md:text-5xl font-bold font-headline mb-4">
            Your Digital Whiteboard, Reimagined.
          </h2>
          <p className="text-muted-foreground mb-8 text-lg">
            Unleash your creativity with a real-time collaborative whiteboard. Draw, write, and innovate together, no matter where you are. Perfect for team brainstorming, planning, and teaching.
          </p>
          <CreateBoardButton />
        </div>
      </main>
      <footer className="p-4 text-center text-sm text-muted-foreground">
        © {new Date().getFullYear()} CollabDraw. All rights reserved.
      </footer>
    </div>
  );
}
