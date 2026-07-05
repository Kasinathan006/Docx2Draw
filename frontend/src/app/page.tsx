"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, FileText, Image as ImageIcon, Sparkles, Wand2, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const FEATURES = [
  {
    icon: Zap,
    title: "10x Faster Creation",
    body: "Turn a 30-page blueprint into a chapter-by-chapter visual map in under 60 seconds.",
  },
  {
    icon: Sparkles,
    title: "Studio-Grade Aesthetics",
    body: "Automated color harmony, grid alignment, and containerization — designed by an AI architect.",
  },
  {
    icon: ImageIcon,
    title: "Multimodal Assets",
    body: "Extract key video frames or embed reference screenshots directly onto the canvas.",
  },
  {
    icon: FileText,
    title: "Universal Export",
    body: "Editable .excalidraw, high-res PNG, SVG, or a shareable interactive link.",
  },
];

const PRICING = [
  { name: "Starter", price: "$0", period: "/mo", perks: ["3 diagrams / month", "Word & text upload", "Standard grid layout"], cta: "Start free", highlight: false },
  { name: "Creator Pro", price: "$19", period: "/mo", perks: ["Unlimited diagrams", "Video & screenshots (500MB)", "All layout styles", "PNG & SVG export"], cta: "Go Pro", highlight: true },
  { name: "Team & Agency", price: "$49", period: "/mo", perks: ["Everything in Pro", "5 team seats", "Shared template library", "API access"], cta: "Contact us", highlight: false },
];

export default function Landing() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-14">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-auto max-w-3xl text-center"
      >
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700">
          <Wand2 className="h-4 w-4" /> AI Document-to-Diagram Engine
        </div>
        <h1 className="bg-gradient-to-r from-brand-700 via-brand-500 to-blue-500 bg-clip-text text-5xl font-extrabold tracking-tight text-transparent sm:text-6xl">
          Doc2Draw AI
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-lg text-slate-600 dark:text-slate-300">
          Turn Word documents, PDF notes, and video courses into stunning, interactive
          Excalidraw visual maps in seconds.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link href="/dashboard/new">
            <Button size="lg">
              Create a visual map <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline">
              View dashboard
            </Button>
          </Link>
        </div>
      </motion.section>

      {/* Features */}
      <section className="mt-20 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="h-full p-6">
              <f.icon className="mb-3 h-7 w-7 text-brand-600" />
              <h3 className="font-semibold text-slate-800 dark:text-slate-100">{f.title}</h3>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{f.body}</p>
            </Card>
          </motion.div>
        ))}
      </section>

      {/* Pricing */}
      <section className="mt-24">
        <h2 className="text-center text-3xl font-bold text-slate-800 dark:text-slate-100">Simple pricing</h2>
        <div className="mt-10 grid grid-cols-1 gap-6 md:grid-cols-3">
          {PRICING.map((tier) => (
            <Card
              key={tier.name}
              className={
                tier.highlight
                  ? "relative border-brand-400 p-7 ring-2 ring-brand-400"
                  : "p-7"
              }
            >
              {tier.highlight && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand-600 px-3 py-1 text-xs font-semibold text-white">
                  Most Popular
                </span>
              )}
              <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">{tier.name}</h3>
              <p className="mt-3">
                <span className="text-4xl font-extrabold text-slate-900 dark:text-white">{tier.price}</span>
                <span className="text-slate-400">{tier.period}</span>
              </p>
              <ul className="mt-5 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                {tier.perks.map((p) => (
                  <li key={p} className="flex items-center gap-2">
                    <span className="text-brand-500">✓</span> {p}
                  </li>
                ))}
              </ul>
              <Link href="/dashboard/new" className="mt-6 block">
                <Button className="w-full" variant={tier.highlight ? "default" : "outline"}>
                  {tier.cta}
                </Button>
              </Link>
            </Card>
          ))}
        </div>
      </section>

      <footer className="mt-24 text-center text-xs text-slate-400">
        Doc2Draw AI · Documents → Excalidraw · Built for scale &amp; aesthetic excellence
      </footer>
    </main>
  );
}
