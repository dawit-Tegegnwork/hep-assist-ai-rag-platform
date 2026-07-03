import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { AnswerPage } from "./pages/AnswerPage";
import { AskPage } from "./pages/AskPage";
import { AuditPage } from "./pages/AuditPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { HomePage } from "./pages/HomePage";
import { ReviewPage } from "./pages/ReviewPage";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/ask" element={<AskPage />} />
          <Route path="/answers/:id" element={<AnswerPage />} />
          <Route path="/review" element={<ReviewPage />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
          <Route path="/audit" element={<AuditPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
);
