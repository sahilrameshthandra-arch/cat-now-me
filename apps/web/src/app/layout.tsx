import type { Metadata, Viewport } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'cat-now-me | AI Development Platform',
    template: '%s | cat-now-me',
  },
  description: 'Build professional websites, AI agents, and automation workflows with local AI models.',
  keywords: ['Next.js', 'AI', 'Ollama', 'LangGraph', 'automation', 'web development'],
  authors: [{ name: 'Sahil' }],
  creator: 'Sahil',
  publisher: 'cat-now-me',
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://cat-now-me.vercel.app',
    siteName: 'cat-now-me',
    title: 'cat-now-me | AI Development Platform',
    description: 'Build professional websites, AI agents, and automation workflows with local AI models.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'cat-now-me',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'cat-now-me | AI Development Platform',
    description: 'Build professional websites, AI agents, and automation workflows with local AI models.',
    images: ['/og-image.png'],
  },
  verification: {
    google: 'google-site-verification-code',
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}