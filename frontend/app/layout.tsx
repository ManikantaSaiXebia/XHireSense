import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'XHireSense - Explainable AI for Smarter Hiring Decisions',
  description: 'AI-powered hiring decision assistant with transparency and explainability',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
