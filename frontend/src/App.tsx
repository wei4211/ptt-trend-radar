import { BrowserRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Layout/Sidebar";
import Dashboard from "./pages/Dashboard";
import Keywords from "./pages/Keywords";
import Sentiment from "./pages/Sentiment";
import WordCloud from "./pages/WordCloud";
import Articles from "./pages/Articles";
import Topics from "./pages/Topics";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/topics" element={<Topics />} />
            <Route path="/keywords" element={<Keywords />} />
            <Route path="/sentiment" element={<Sentiment />} />
            <Route path="/wordcloud" element={<WordCloud />} />
            <Route path="/articles" element={<Articles />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
