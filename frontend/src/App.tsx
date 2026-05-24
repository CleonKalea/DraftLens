import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FolderOpen, Bot, SendHorizontal, User } from "lucide-react";

export default function App() {

  const [messages, setMessages] = useState([
    { id: 1, role: "ai", text: "Halo Kal! Saya siap menganalisis dokumen hukummu. Silakan tanyakan pasal atau klausul yang ingin kamu bedah." }
  ]);
  const [inputText, setInputText] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      text: inputText
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");

    setTimeout(() => {
      const aiMessage = {
        id: Date.now() + 1,
        role: "ai",
        text: `Dokumen DraftLens mendeteksi pertanyaanmu tentang: "${inputText}". Ini adalah respon simulasi dari Llama 3 backend sebelum API dihubungkan.`
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 800);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-zinc-950 text-white font-sans antialiased">
      
      {/* Sidebar */}
      <aside className="w-80 h-full border-r border-zinc-800 bg-zinc-950 flex flex-col">
        <div className="p-6 border-b border-zinc-900 flex items-center gap-3">
          <div className="h-6 w-6 rounded-md bg-white text-black flex items-center justify-center font-bold text-xs">DL</div>
          <span className="font-medium tracking-tight text-sm">DraftLens Workspace</span>
        </div>
        <div className="flex-1 p-4">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider mb-3 px-2">Dokumen Hukum</div>
          <ScrollArea className="h-full">
            <div className="space-y-1">
              <button className="w-full flex items-center gap-3 p-2.5 rounded-xl text-left text-xs bg-zinc-900 text-white border border-zinc-800 shadow-sm">
                <FolderOpen className="h-4 w-4 text-zinc-400 shrink-0" />
                <span className="truncate">Amdal_Villa_Ubud.pdf</span>
              </button>
            </div>
          </ScrollArea>
        </div>
      </aside>

      {/* Chat Workspace */}
      <main className="flex-1 h-full flex flex-col bg-zinc-900/30">
        <header className="h-16 px-6 border-b border-zinc-800 bg-zinc-950 flex items-center gap-3">
          <Bot className="h-4 w-4 text-zinc-400" />
          <span className="text-xs font-medium">Analisis RAG: Amdal_Villa_Ubud.pdf</span>
        </header>

        <div className="flex-1 p-6 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="max-w-2xl mx-auto space-y-4">
              
              {messages.map((msg) => (
                <div 
                  key={msg.id} 
                  className={`flex gap-4 p-4 rounded-xl border text-xs leading-relaxed transition-all ${
                    msg.role === "user" 
                      ? "bg-zinc-800/40 border-zinc-700/50 ml-12" // Gaya Kotak Chat User (Agak ke kanan)
                      : "bg-zinc-900/60 border-zinc-800/50 mr-12"  // Gaya Kotak Chat AI (Agak ke kiri)
                  }`}
                >
                  <div className={`h-6 w-6 rounded flex items-center justify-center font-bold text-[10px] shrink-0 ${
                    msg.role === "user" ? "bg-zinc-700 text-zinc-300" : "bg-white text-black"
                  }`}>
                    {msg.role === "user" ? <User className="h-3 w-3" /> : "AI"}
                  </div>
                  <div>{msg.text}</div>
                </div>
              ))}

            </div>
            <div ref={chatEndRef} />
          </ScrollArea>
        </div>

        {/* INPUT BAR INTERAKTIF */}
        <footer className="p-6 bg-zinc-950 border-t border-zinc-800">
          <div className="max-w-2xl mx-auto flex gap-2">
            <Input 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Tanyakan sesuatu tentang dokumen ini..." 
              className="h-10 rounded-xl text-xs bg-zinc-900 border-zinc-800 focus-visible:ring-zinc-700"
            />
            <Button 
              onClick={handleSendMessage}
              className="h-10 w-10 p-0 rounded-xl bg-white hover:bg-zinc-200 text-black shadow-sm"
            >
              <SendHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </footer>

      </main>

    </div>
  );
}