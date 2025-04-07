import { Providers } from './providers'
import '../styles/globals.css'

export const metadata = {
  title: 'הסכתומאט',
  description: 'מערכת ניהול הסכתים',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="he" dir="rtl" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
} 