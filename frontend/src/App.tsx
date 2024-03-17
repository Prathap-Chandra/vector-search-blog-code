import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ImageGeneration from "./views/image-generation";
import ImageSearch from "./views/image-search";
import PDFChat from "./views/pdf-chat";
import PageNotFound from "./views/page-not-found";

const App = () => {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/generate-image-from-text-description" element={<ImageGeneration />} />
          <Route path="/search-visually-similar-images" element={<ImageSearch />} />
          <Route path="/chat-with-your-pdf" element={<PDFChat />} />
          <Route path="*" element={<PageNotFound />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;