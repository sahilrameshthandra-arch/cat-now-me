import Link from 'next/link';
import { 
  Bot, 
  Globe, 
  Zap, 
  Code, 
  Database, 
  Terminal,
  CheckCircle,
  ArrowRight,
  Github,
  ExternalLink
} from 'lucide-react';

const features = [
  {
    icon: Globe,
    title: 'Professional Websites',
    description: 'Next.js 15 + Tailwind + TypeScript. Deploy to Vercel in minutes. Built for client work.',
    href: '/projects',
  },
  {
    icon: Bot,
    title: 'Local AI Agents',
    description: 'LangGraph + Ollama. Run codellama, deepseek-coder, llama3.1 locally. Zero API costs.',
    href: '/agents',
  },
  {
    icon: Zap,
    title: 'Automation Workflows',
    description: 'n8n visual workflow builder. Webhooks, schedules, API integrations. Self-hosted.',
    href: '/workflows',
  },
  {
    icon: Code,
    title: 'Full-Stack Development',
    description: 'FastAPI + Next.js monorepo. Shared types. Hot reload. Type-safe end-to-end.',
    href: '/docs',
  },
  {
    icon: Database,
    title: 'Data & RAG',
    description: 'PostgreSQL + pgvector + ChromaDB. Document ingestion. Semantic search. Local embeddings.',
    href: '/knowledge',
  },
  {
    icon: Terminal,
    title: 'Developer Experience',
    description: 'TypeScript, ESLint, Prettier, Husky, GitHub Actions. One command to rule them all.',
    href: '/docs/dev-setup',
  },
];

const stats = [
  { value: '100%', label: 'Local-First' },
  { value: '$0', label: 'API Costs' },
  { value: '5+', label: 'AI Models' },
  { value: '∞', label: 'Scalability' },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-brand-50/30 to-white dark:from-gray-950 dark:via-brand-900/10 dark:to-gray-950">
      {/* Navigation */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-950/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
        <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8" aria-label="Main navigation">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-8 w-8 text-brand-600" aria-hidden="true" />
              <span className="text-xl font-bold text-gray-900 dark:text-white">cat-now-me</span>
            </div>
            <div className="hidden md:flex items-center gap-6">
              <Link href="#features" className="text-sm font-medium text-gray-700 hover:text-brand-600 dark:text-gray-300 dark:hover:text-brand-400 transition-colors">
                Features
              </Link>
              <Link href="#stack" className="text-sm font-medium text-gray-700 hover:text-brand-600 dark:text-gray-300 dark:hover:text-brand-400 transition-colors">
                Stack
              </Link>
              <Link href="#getting-started" className="text-sm font-medium text-gray-700 hover:text-brand-600 dark:text-gray-300 dark:hover:text-brand-400 transition-colors">
                Get Started
              </Link>
              <a 
                href="https://github.com/sahilrameshthandra-arch/cat-now-me" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-sm font-medium text-gray-700 hover:text-brand-600 dark:text-gray-300 dark:hover:text-brand-400 transition-colors"
              >
                <Github className="h-4 w-4" aria-hidden="true" />
                GitHub
              </a>
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center animate-in">
            <div className="inline-flex items-center gap-2 rounded-full bg-brand-100/50 px-4 py-1.5 text-sm font-medium text-brand-700 dark:bg-brand-900/30 dark:text-brand-300 mb-6">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-500"></span>
              </span>
              Local-First AI Development Platform
            </div>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-gray-900 dark:text-white mb-6">
              Build <span className="text-brand-600">AI-Powered</span> Products
              <br />
              <span className="text-gray-600 dark:text-gray-300">Without Cloud Dependencies</span>
            </h1>
            <p className="mx-auto max-w-3xl text-lg sm:text-xl text-gray-600 dark:text-gray-400 mb-10">
              A production-ready monorepo for building client websites, AI agents, and automation workflows.
              Run everything locally with Ollama. Deploy anywhere.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="#getting-started" className="btn-primary group w-full sm:w-auto">
                <span>Start Building</span>
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" aria-hidden="true" />
              </Link>
              <a 
                href="https://github.com/sahilrameshthandra-arch/cat-now-me" 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn-outline group w-full sm:w-auto"
              >
                <Github className="h-4 w-4" aria-hidden="true" />
                View on GitHub
                <ExternalLink className="h-4 w-4 ml-1" aria-hidden="true" />
              </a>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center animate-in">
                <div className="text-4xl sm:text-5xl font-bold text-brand-600 dark:text-brand-400 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-950">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16 animate-in">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Everything You Need to <span className="text-brand-600">Ship Fast</span>
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Six integrated capabilities. One codebase. Zero vendor lock-in.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <article
                key={feature.title}
                className="card-hover p-6 animate-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-100 text-brand-600 dark:bg-brand-900/30 dark:text-brand-400 mb-4">
                  <feature.icon className="h-6 w-6" aria-hidden="true" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {feature.description}
                </p>
                <Link
                  href={feature.href}
                  className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400 dark:hover:text-brand-300 transition-colors"
                >
                  Explore
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section id="stack" className="py-20 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16 animate-in">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Modern <span className="text-brand-600">Tech Stack</span>
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Carefully selected tools that work together seamlessly.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Frontend */}
            <div className="card p-6 animate-in">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Globe className="h-5 w-5 text-brand-600" aria-hidden="true" />
                Frontend
              </h3>
              <ul className="space-y-3">
                {[
                  'Next.js 15 (App Router + Turbopack)',
                  'React 18 + TypeScript',
                  'Tailwind CSS 3.4',
                  'Radix UI Primitives',
                  'React Hook Form + Zod',
                  'Lucide Icons',
                ].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                    <CheckCircle className="h-4 w-4 text-brand-500 flex-shrink-0" aria-hidden="true" />
                    <span className="text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Backend */}
            <div className="card p-6 animate-in">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Database className="h-5 w-5 text-brand-600" aria-hidden="true" />
                Backend & AI
              </h3>
              <ul className="space-y-3">
                {[
                  'FastAPI (Python 3.11+)',
                  'LangGraph + LangChain',
                  'Ollama (Local LLMs)',
                  'PostgreSQL + pgvector',
                  'ChromaDB (Vector Store)',
                  'Pydantic v2',
                ].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                    <CheckCircle className="h-4 w-4 text-brand-500 flex-shrink-0" aria-hidden="true" />
                    <span className="text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* DevOps */}
            <div className="card p-6 animate-in">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Terminal className="h-5 w-5 text-brand-600" aria-hidden="true" />
                DevOps & Automation
              </h3>
              <ul className="space-y-3">
                {[
                  'Docker + Docker Compose',
                  'n8n (Self-hosted)',
                  'GitHub Actions CI/CD',
                  'Vercel (Web Deploy)',
                  'Railway/Render (API Deploy)',
                  'pnpm Workspaces',
                ].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                    <CheckCircle className="h-4 w-4 text-brand-500 flex-shrink-0" aria-hidden="true" />
                    <span className="text-sm">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Getting Started Section */}
      <section id="getting-started" className="py-20 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-950">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16 animate-in">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              <span className="text-brand-600">Get Started</span> in 3 Steps
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              From zero to running AI agents in under 10 minutes.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Clone & Install',
                description: 'Clone the repo, install dependencies, and start the dev servers.',
                commands: [
                  'git clone https://github.com/sahilrameshthandra-arch/cat-now-me.git',
                  'cd cat-now-me',
                  'npm install',
                  'cd apps/api && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt',
                ],
              },
              {
                step: '02',
                title: 'Start Ollama & Models',
                description: 'Pull the coding models you need for AI agents.',
                commands: [
                  'ollama serve',
                  'ollama pull codellama:13b-instruct',
                  'ollama pull deepseek-coder:6.7b',
                  'ollama pull llama3.1:8b',
                ],
              },
              {
                step: '03',
                title: 'Run Everything',
                description: 'Start the web app, API, and n8n with one command.',
                commands: [
                  'npm run dev',
                  '# Web: http://localhost:3000',
                  '# API: http://localhost:8000',
                  '# n8n: http://localhost:5678',
                ],
              },
            ].map((step, index) => (
              <div key={step.step} className="card p-6 animate-in relative" style={{ animationDelay: `${index * 150}ms` }}>
                <div className="absolute -top-3 left-6 bg-white dark:bg-gray-950 px-2 text-brand-600 dark:text-brand-400 font-bold text-lg">
                  Step {step.step}
                </div>
                <div className="pt-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {step.description}
                  </p>
                  <div className="bg-gray-950 dark:bg-gray-900 rounded-lg p-4 font-mono text-sm text-green-400 overflow-x-auto">
                    {step.commands.map((cmd, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <span className="text-gray-500">$</span>
                        <code>{cmd}</code>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-brand-600">
        <div className="mx-auto max-w-7xl text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Ready to Build with Local AI?
          </h2>
          <p className="text-lg text-brand-100 mb-8 max-w-2xl mx-auto">
            Join developers building the future of AI-powered applications — without sending data to the cloud.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="#getting-started" className="btn bg-white text-brand-600 hover:bg-brand-50 px-8 py-3 text-lg">
              Start Building Now
            </Link>
            <a 
              href="https://github.com/sahilrameshthandra-arch/cat-now-me" 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn border-2 border-white text-white hover:bg-white/10 px-8 py-3 text-lg"
            >
              <Github className="h-5 w-5 mr-2" aria-hidden="true" />
              Star on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
        <div className="mx-auto max-w-7xl">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Bot className="h-8 w-8 text-brand-600" aria-hidden="true" />
                <span className="text-xl font-bold text-gray-900 dark:text-white">cat-now-me</span>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                All-in-one AI development platform. Build websites, agents, and workflows locally.
              </p>
            </div>
            <nav>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><Link href="/docs" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Documentation</Link></li>
                <li><Link href="/agents" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">AI Agents Guide</Link></li>
                <li><Link href="/workflows" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">n8n Workflows</Link></li>
                <li><Link href="/projects" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Project Templates</Link></li>
              </ul>
            </nav>
            <nav>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Community</h4>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><a href="https://github.com/sahilrameshthandra-arch/cat-now-me/discussions" target="_blank" rel="noopener noreferrer" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Discussions</a></li>
                <li><a href="https://github.com/sahilrameshthandra-arch/cat-now-me/issues" target="_blank" rel="noopener noreferrer" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Issues</a></li>
                <li><a href="https://discord.gg/cat-now-me" target="_blank" rel="noopener noreferrer" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Discord</a></li>
                <li><a href="https://twitter.com/catnowme" target="_blank" rel="noopener noreferrer" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Twitter</a></li>
              </ul>
            </nav>
            <nav>
              <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li><Link href="/privacy" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Terms of Service</Link></li>
                <li><Link href="/license" className="hover:text-brand-600 dark:hover:text-brand-400 transition-colors">License (MIT)</Link></li>
              </ul>
            </nav>
          </div>
          <div className="pt-8 border-t border-gray-200 dark:border-gray-800 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              © 2026 cat-now-me. Built with Next.js, FastAPI, and ❤️
            </p>
            <div className="flex items-center gap-6">
              <a href="https://github.com/sahilrameshthandra-arch/cat-now-me" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-brand-600 dark:hover:text-brand-400 transition-colors">
                <Github className="h-5 w-5" aria-hidden="true" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}