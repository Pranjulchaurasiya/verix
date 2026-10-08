import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { GeistSans } from 'geist/font/sans'
import { GeistMono } from 'geist/font/mono'
import { Toaster } from '@/components/ui/sonner'
import './globals.css'

export const metadata: Metadata = {
  title: 'Verix — Product image evidence',
  description:
    'Paste a product image or listing link and see everywhere that photo appears on the web, with a clear, plain-language trust signal. Built for shoppers and independent sellers.',
  icons: {
    icon: [{ url: '/verix-mark.svg?v=2', type: 'image/svg+xml' }],
    shortcut: '/verix-mark.svg?v=2',
  },
}

export const viewport: Viewport = {
  colorScheme: 'dark',
  themeColor: '#08111e',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable}`}>
      <body className="antialiased">
        {children}
        <Toaster />
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
