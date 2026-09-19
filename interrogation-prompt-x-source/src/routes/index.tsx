import { createFileRoute } from "@tanstack/react-router";
import { InterrogationApp } from "../components/InterrogationApp";

export const Route = createFileRoute("/")({
  ssr: false,
  head: () => ({
    meta: [
      { title: "Prompt X — Interrogation Protocol" },
      { name: "description", content: "A cinematic 3D interrogation room experience." },
      { property: "og:title", content: "Prompt X — Interrogation Protocol" },
      { property: "og:description", content: "Question the suspect and uncover the truth in an immersive 3D interrogation room." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: InterrogationApp,
});
