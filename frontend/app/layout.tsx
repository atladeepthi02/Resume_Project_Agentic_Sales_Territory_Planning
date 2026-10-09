import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sales Territory Planning Assistant',
  description:
    'Review prioritized accounts, understand the evidence, approve the plan and export approved actions.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
