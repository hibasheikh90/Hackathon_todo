import { AuthProvider } from '@/contexts/AuthContext';
import type { Metadata } from 'next';
import '../globals.css';

export const metadata: Metadata = {
  title: 'Todo App',
  description: 'A modern todo application with authentication',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <AuthProvider>
          <div className="min-h-screen bg-gray-50">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}