import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import { ToastProvider } from '@/components/common/ToastContext';
import ToastContainer from '@/components/common/ToastContainer';

export const metadata: Metadata = {
  title: 'Lead Gen AI | Find. Write. Send.',
  description: 'Simple B2B Prospecting & Outreach Suite.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-white text-slate-900 min-h-screen flex antialiased">

        <ToastProvider>
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <Header />
            <main className="flex-1 p-6 overflow-y-auto bg-white">
              {children}
            </main>
          </div>
          <ToastContainer />
        </ToastProvider>
      </body>
    </html>
  );
}
