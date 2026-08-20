import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown';
import { Send, RotateCcw, ShieldCheck, Mic, Volume2, VolumeX } from 'lucide-react';
import Avatar from './components/Avatar.jsx';
import PersonaSwitcher from './components/PersonaSwitcher.jsx';
import PermissionPanel from './components/PermissionPanel.jsx';

const USERS = [
  { id: 'u_student_rahul', name: 'Rahul Sharma', role: 'student', allowed: ['view_attendance', 'request_escalation'] },
  { id: 'u_parent_sharma', name: 'Mr. Sharma', role: 'parent', allowed: ['view_attendance', 'request_escalation'] },
  { id: 'u_teacher_mehta', name: 'Ms. Mehta', role: 'teacher', allowed: ['view_attendance', 'mark_attendance', 'request_escalation'] },
  { id: 'u_principal_rao', name: 'Dr. Rao', role: 'principal', allowed: ['view_attendance', 'view_school_analytics', 'request_escalation'] },
];

const TOOLS = ['view_attendance', 'mark_attendance', 'view_school_analytics', 'request_escalation'];

export default function App() {
  const [currentUser, setCurrentUser] = useState(USERS[0]);
  const [token, setToken] = useState(null);
  const [language, setLanguage] = useState('English');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [voiceOn, setVoiceOn] = useState(true);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  // Handle Login when user changes
  const fetchLogin = async (user) => {
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: user.id }),
    });
    return res.json();
  };

  useEffect(() => {
    let ignore = false;

    fetchLogin(currentUser)
      .then((data) => {
        if (ignore) return;
        setToken(data.access_token || data.token);
        setMessages([
          {
            role: 'assistant',
            content: `Logged in as **${currentUser.name}** (${currentUser.role}). How can I help you today?`,
            time: Date.now(),
          },
        ]);
      })
      .catch((err) => {
        if (!ignore) console.error('Login failed', err);
      });

    return () => {
      ignore = true;
    };
  }, [currentUser]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Send Message to /chat
  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading || !token) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage, time: Date.now() }]);
    setLoading(true);

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: userMessage, language }),
      });
            const data = await res.json();
      const replyText = data.reply || data.detail || 'No response received.';
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: replyText, time: Date.now() },
      ]);
      speak(replyText);
    } catch (err) {
      console.error('Chat request failed', err);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '⚠️ Error communicating with the AI service.', time: Date.now(), failed: true, retryText: userMessage },
      ]);
    } finally {
      setLoading(false);
    }
  };

    // Speech-to-text: mic button fills the input
  const handleMicClick = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      alert('Speech recognition is not supported in this browser. Try Chrome.');
      return;
    }
    if (listening) {
      recognitionRef.current?.stop();
      return;
    }
    const recognition = new SR();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      setInput((prev) => (prev ? `${prev} ${text}` : text));
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  // Text-to-speech: read assistant replies aloud
  const speak = (text) => {
    if (!voiceOn || !window.speechSynthesis) return;
    const plain = text.replace(/[*_`#]/g, '');
    const utterance = new SpeechSynthesisUtterance(plain);
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  // Retry a failed message
  const handleRetry = (text) => {
    if (!text) return;
    setInput(text);
    setTimeout(() => handleSend(), 0);
  };

  // Reset Session
  const handleReset = async () => {
    if (!token) return;
    try {
      await fetch('/chat/reset', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessages([{ role: 'assistant', content: `Session reset for **${currentUser.name}**.`, time: Date.now() }]);
    } catch (err) {
      console.error('Reset failed', err);
    }
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans">
      {/* Left Sidebar: Role Switcher & RBAC Inspector */}
      <aside className="w-80 border-r border-slate-800 bg-slate-950 p-5 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 mb-6">
            <ShieldCheck className="text-emerald-400 w-6 h-6" />
            <h1 className="text-lg font-bold tracking-wide">XYZ AI Assistant</h1>
          </div>

          <div className="mb-6">
            <PersonaSwitcher users={USERS} currentUser={currentUser} onSelect={setCurrentUser} />
          </div>

          <PermissionPanel user={currentUser} tools={TOOLS} />
        </div>

        <div className="text-xs text-slate-500 text-center">
          Aug 20 Demo Build • FastAPI + Gemini RBAC
        </div>
      </aside>

      {/* Main Chat Interface */}
      <main className="flex-1 flex flex-col bg-slate-900">
        {/* Top Navbar */}
                <header className="h-16 border-b border-slate-800 flex items-center justify-between px-6 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <Avatar
              state={speaking ? 'speaking' : listening ? 'listening' : loading ? 'thinking' : 'idle'}
              size="lg"
            />
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-200">{currentUser.name}</span>
              <span className="bg-slate-800 text-slate-400 text-xs px-2 py-0.5 rounded uppercase font-medium">
                {currentUser.role}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
                        <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-200 outline-none"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi (हिंदी)</option>
              <option value="Tamil">Tamil (தமிழ்)</option>
              <option value="Telugu">Telugu (తెలుగు)</option>
              <option value="Marathi">Marathi (मराठी)</option>
              <option value="Bengali">Bengali (বাংলা)</option>
              <option value="Gujarati">Gujarati (ગુજરાતી)</option>
              <option value="Punjabi">Punjabi (ਪੰਜਾਬੀ)</option>
              <option value="Kannada">Kannada (ಕನ್ನಡ)</option>
              <option value="Malayalam">Malayalam (മലയാളം)</option>
              <option value="Urdu">Urdu (اردو)</option>
            </select>
            <button
              onClick={handleReset}
              className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs px-3 py-1.5 rounded-lg border border-slate-700 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Chat
            </button>
          </div>
        </header>

        {/* Message Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((m, idx) => (
            <div key={idx} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {m.role === 'assistant' && <Avatar state={speaking ? 'speaking' : 'idle'} size="sm" />}
              <div
                className={`max-w-2xl rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-emerald-600 text-white rounded-br-none'
                    : m.failed
                    ? 'bg-rose-950/40 text-rose-200 border border-rose-800/60 rounded-bl-none shadow-sm'
                    : 'bg-slate-800/90 text-slate-200 border border-slate-700/80 rounded-bl-none shadow-sm'
                }`}
              >
                <div className="prose prose-invert prose-sm max-w-none prose-p:my-1 prose-ul:my-1">
                  <ReactMarkdown>
                    {m.content}
                  </ReactMarkdown>
                </div>
                {m.time && (
                  <div className={`mt-1 flex items-center gap-2 text-[10px] ${m.role === 'user' ? 'text-emerald-100/70' : 'text-slate-500'}`}>
                    {new Date(m.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    {m.failed && (
                      <button
                        type="button"
                        onClick={() => handleRetry(m.retryText)}
                        className="text-rose-300 underline underline-offset-2 hover:text-rose-200"
                      >
                        Retry
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

                    {loading && (
            <div className="flex gap-3 items-center text-slate-400 text-xs">
              <Avatar state="thinking" size="sm" />
              <span>Processing with Gemini function-calling...</span>
            </div>
          )}
          {listening && (
            <div className="flex gap-3 items-center text-emerald-400 text-xs">
              <Avatar state="listening" size="sm" />
              <span>Listening...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="p-4 border-t border-slate-800 bg-slate-950/60 flex gap-3">
          <button
            type="button"
            onClick={handleMicClick}
            disabled={loading}
            title={listening ? 'Stop listening' : 'Speak your message'}
            className={`px-3 py-2.5 rounded-xl border text-sm transition-colors disabled:opacity-50 ${
              listening
                ? 'bg-rose-600 border-rose-500 text-white animate-pulse'
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'
            }`}
          >
            <Mic className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => setVoiceOn((v) => !v)}
            title={voiceOn ? 'Voice replies on' : 'Voice replies off'}
            className={`px-3 py-2.5 rounded-xl border text-sm transition-colors ${
              voiceOn
                ? 'bg-emerald-600/20 border-emerald-500/50 text-emerald-400'
                : 'bg-slate-800 border-slate-700 text-slate-500'
            }`}
          >
            {voiceOn ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Message as ${currentUser.name} (${currentUser.role})...`}
            disabled={loading}
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-4 py-2.5 rounded-xl font-medium text-sm flex items-center gap-1.5 transition-all shadow-md"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
      </main>
    </div>
  );
}