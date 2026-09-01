'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, Plus } from 'lucide-react';

export default function Header() {
  const pathname = usePathname();

  let title = 'Home';
  if (pathname.startsWith('/leads')) title = 'Leads';
  else if (pathname.startsWith('/campaigns')) title = 'Campaigns';
  else if (pathname.startsWith('/settings')) title = 'Settings';

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Title */}
      <h1 className="text-sm font-semibold text-slate-900 tracking-tight">{title}</h1>

      {/* Global Search & Actions */}
      <div className="flex items-center gap-4">
        <div className="relative w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search leads, companies or email..."
            className="w-full bg-slate-50 border border-slate-200 rounded-md pl-9 pr-3 py-1.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 transition"
          />
        </div>

        {/* Quick Lead Find CTA button */}
        <Link
          href="/leads?modal=find"
          className="flex items-center gap-1.5 bg-slate-900 hover:bg-black text-white px-3.5 py-1.5 rounded-md text-xs font-medium transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Find leads</span>
        </Link>
      </div>
    </header>
  );
}
