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
  const [documents, setDocuments] = useState<{ id: number; filename: string }[]>([]);
  const [activeDocId, setActiveDocId] = useState<number | null>(null);
  const [docSummary, setDocSummary] = useState<string>("");

  const chatEndRef = useRef<HTMLDivElement>(null);

  const fetchDocuments = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/document/list");
      if (!response.ok) throw new Error("Gagal mengambil daftar dokumen");
      const data = await response.json();
      setDocuments(data.documents);
      
      // Jika ada dokumen yang tersedia di database, otomatis aktifkan dokumen pertama
      if (data.documents.length > 0) {
        setActiveDocId(data.documents[0].id);
      }
    } catch (error) {
      console.error("Error fetching docs:", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleSendMessage = async () => {
    if (!inputText.trim() || activeDocId === null) return;

    const userText = inputText;
    setInputText("");

    const userMessage = {
      id: Date.now(),
      role: "user",
      text: userText
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const response = await fetch("http://localhost:8000/api/v1/rag/chat/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: activeDocId, 
          question: userText        
        })
      });

      if (!response.ok) throw new Error("Server RAG merespon dengan eror");

      const data = await response.json(); 

      const aiMessage = {
        id: Date.now() + 1,
        role: "ai",
        text: data.answer 
      };
      setMessages((prev) => [...prev, aiMessage]);

    } catch (error) {
      console.error("Error RAG query:", error);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 2, role: "ai", text: "Maaf Kal, koneksi ke mesin backend AI terputus. Pastikan FastAPI sudah dinyalakan." }
      ]);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Mencari objek dokumen yang sedang aktif untuk menampilkan nama filenya di header
  const activeDocument = documents.find(doc => doc.id === activeDocId);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-zinc-950 text-white font-sans antialiased">

      <aside className="w-80 h-full border-r border-zinc-800 bg-zinc-950 flex flex-col">
        <div className="p-6 border-b border-zinc-900 flex items-center gap-3">
          <div className="h-6 w-6 rounded-md bg-white text-black flex items-center justify-center font-bold text-xs">DL</div>
          <span className="font-medium tracking-tight text-sm">DraftLens Workspace</span>
        </div>
        
        <div className="flex-1 p-4 flex flex-col min-h-0">
          <div className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider mb-3 px-2">Dokumen</div>
          
          <ScrollArea className="flex-1">
            <div className="space-y-1 pr-3">
              {documents.length === 0 ? (
                <p className="text-xs text-zinc-500 p-2 italic">Belum ada dokumen di database.</p>
              ) : (
                documents.map((doc) => {
                  const isActive = doc.id === activeDocId;
                  return (
                    <button
                      key={doc.id}
                      onClick={() => setActiveDocId(doc.id)}
                      className={`w-full flex items-center gap-3 p-2.5 rounded-xl text-left text-xs transition-all border ${
                        isActive
                          ? "bg-zinc-900 text-white border-zinc-800 shadow-sm"
                          : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-900/40 hover:text-zinc-200"
                      }`}
                    >
                      <FolderOpen className={`h-4 w-4 shrink-0 ${isActive ? "text-white" : "text-zinc-500"}`} />
                      <span className="truncate font-medium">{doc.filename}</span>
                    </button>
                  );
                })
              )}
            </div>
          </ScrollArea>
        </div>
      </aside>
      <main className="flex-1 h-full flex flex-col bg-zinc-900/30">

        <header className="h-16 px-6 border-b border-zinc-800 bg-zinc-950 flex items-center gap-3">
          <Bot className="h-4 w-4 text-zinc-400" />
          <span className="text-xs font-medium tracking-tight">
            {activeDocument ? `Analisis RAG: ${activeDocument.filename}` : "Pilih dokumen di sidebar"}
          </span>
        </header>

        <div className="flex-1 p-6 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="max-w-2xl mx-auto space-y-4 pb-4">
              
              {messages.map((msg) => (
                <div 
                  key={msg.id} 
                  className={`flex gap-4 p-4 rounded-xl border text-xs leading-relaxed transition-all ${
                    msg.role === "user" 
                      ? "bg-zinc-800/40 border-zinc-700/50 ml-12"
                      : "bg-zinc-900/60 border-zinc-800/50 mr-12"
                  }`}
                >
                  <div className={`h-6 w-6 rounded flex items-center justify-center font-bold text-[10px] shrink-0 ${
                    msg.role === "user" ? "bg-zinc-700 text-zinc-300" : "bg-white text-black"
                  }`}>
                    {msg.role === "user" ? <User className="h-3 w-3" /> : "AI"}
                  </div>
                  <div className="whitespace-pre-wrap">{msg.text}</div>
                </div>
              ))}

              <div ref={chatEndRef} />
            </div>
          </ScrollArea>
        </div>

        <footer className="p-6 bg-zinc-950 border-t border-zinc-800">
          <div className="max-w-2xl mx-auto flex gap-2">
            <Input 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              disabled={activeDocId === null} // Kunci input jika belum ada dokumen hukum terpilih
              placeholder={activeDocId ? "Tanyakan sesuatu tentang dokumen ini..." : "Silakan upload atau pilih dokumen terlebih dahulu"} 
              className="h-10 rounded-xl text-xs bg-zinc-900 border-zinc-800 focus-visible:ring-zinc-700 disabled:opacity-50"
            />
            <Button 
              onClick={handleSendMessage}
              disabled={activeDocId === null}
              className="h-10 w-10 p-0 rounded-xl bg-white hover:bg-zinc-200 text-black shadow-sm disabled:bg-zinc-800 disabled:text-zinc-600"
            >
              <SendHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </footer>

      </main>

    </div>
  );
}