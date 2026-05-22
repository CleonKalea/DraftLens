import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FolderOpen, Bot, SendHorizontal } from "lucide-react";

export default function App() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-zinc-950 text-white font-sans antialiased">
      
      {/* Sidebar */}
      <aside className="w-80 h-full border-r border-zinc-800 bg-zinc-950 flex flex-col">
        {/* Header Sidebar */}
        <div className="p-6 border-b border-zinc-900 flex items-center gap-3">
          <div className="h-6 w-6 rounded-md bg-white text-black flex items-center justify-center font-bold text-xs">
            777
          </div>
          <span className="font-medium tracking-tight text-sm">DraftLens Workspace</span>
        </div>

        {/* Documents List */}
        <div className="flex-1 p-4">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider mb-3 px-2">
            Documents
          </div>
          
          <ScrollArea className="h-[calc(h-full-40px)]">
            <div className="space-y-1">
              {/* Item Example Preview */}
              <button className="w-full flex items-center gap-3 p-2.5 rounded-xl text-left text-xs bg-zinc-900 text-white border border-zinc-800 shadow-sm">
                <FolderOpen className="h-4 w-4 text-zinc-400 shrink-0" />
                <span className="truncate">DraftLens Docs 1.pdf</span>
              </button>
            </div>
          </ScrollArea>
        </div>

      </aside>

      {/* Chat Workspace */}
      <main className="flex-1 h-full flex flex-col bg-zinc-900/30">
        
        {/* Topbar Workspace */}
        <header className="h-16 px-6 border-b border-zinc-800 bg-zinc-950 flex items-center gap-3">
          <Bot className="h-4 w-4 text-zinc-400" />
          <span className="text-xs font-medium">RAG: DraftLens Docs 1.pdf</span>
        </header>

        {/* Chat View*/}
        <div className="flex-1 p-6 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="max-w-2xl mx-auto space-y-4">
              
              {/* Response Box Example*/}
              <div className="flex gap-4 p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/50 text-xs leading-relaxed">
                <div className="h-6 w-6 rounded bg-white text-black flex items-center justify-center font-bold text-[10px] shrink-0">
                  101
                </div>
                <div>
                  Hi! How can I help you with the document?
                </div>
              </div>

            </div>
          </ScrollArea>
        </div>

        {/* Chat Input Bar */}
        <footer className="p-6 bg-zinc-950 border-t border-zinc-800">
          <div className="max-w-2xl mx-auto flex gap-2">
            <Input 
              placeholder="What do you want to ask about the document?" 
              className="h-10 rounded-xl text-xs bg-zinc-900 border-zinc-800 focus-visible:ring-zinc-700"
            />
            <Button className="h-10 w-10 p-0 rounded-xl bg-white hover:bg-zinc-200 text-black shadow-sm">
              <SendHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </footer>

      </main>

    </div>
  );
}