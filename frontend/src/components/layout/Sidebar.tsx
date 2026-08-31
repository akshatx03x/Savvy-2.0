'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Search,
  Users,
  Building2,
  Brain,
  Sparkles,
  Send,
  Mail,
  ShieldCheck,
  BarChart3,
  Settings,
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Find Leads', href: '/find-leads', icon: Search },
  { name: 'Leads', href: '/leads', icon: Users },
  { name: 'Companies', href: '/companies', icon: Building2 },
  { name: 'AI Research', href: '/ai-research', icon: Brain },
  { name: 'AI Outreach', href: '/outreach', icon: Send },
  { name: 'Campaigns', href: '/campaigns', icon: Sparkles },
  { name: 'Mailboxes', href: '/mailboxes', icon: Mail },
  { name: 'Deliverability', href: '/deliverability', icon: ShieldCheck },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-[#090D14] border-r border-slate-800/80 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-slate-800/60 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-600/30 group-hover:bg-indigo-500 transition">
              <Sparkles className="w-4 h-4 fill-white" />
            </div>
            <div>
              <div className="font-bold text-slate-100 text-sm tracking-tight flex items-center gap-1.5">
                LEAD GEN AI
                <span className="text-[9px] font-mono font-semibold bg-indigo-500/10 text-indigo-400 px-1.5 py-0.5 rounded border border-indigo-500/20">
                  PRO
                </span>
              </div>
              <div className="text-[10px] text-slate-400 font-mono">B2B Prospecting Suite</div>
            </div>
          </Link>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition group ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-400 font-semibold border border-indigo-500/30 shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 transition ${
                      isActive ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'
                    }`}
                  />
                  <span>{item.name}</span>
                </div>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer / System Status */}
      <div className="p-4 border-t border-slate-800/60 bg-[#090D14]/80">
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-400 font-mono">System Engine</span>
            <span className="text-emerald-400 font-mono flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Online
            </span>
          </div>
          <div className="text-[10px] text-slate-400 leading-tight">
            Modules 1, 2, 3 & 4 fully operational.
          </div>
        </div>
      </div>
    </aside>
  );
}
