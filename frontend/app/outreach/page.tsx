'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RedirectPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/leads');
  }, [router]);

  return <div className="text-xs text-slate-500 p-6">Redirecting to leads workspace...</div>;
}
