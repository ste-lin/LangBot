import { ReactNode } from 'react';

export default function CardsLayout({ children }: { children: ReactNode }) {
  return (
    <div style={{ height: '100%' }}>
      {children}
    </div>
  );
}
