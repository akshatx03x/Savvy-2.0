'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Users, Send, Settings, User } from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

const navItems: NavItem[] = [
  { name: 'Home', href: '/', icon: LayoutDashboard },
  { name: 'Leads', href: '/leads', icon: Users },
  { name: 'Campaigns', href: '/campaigns', icon: Send },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-200">
          <Link href="/" className="block">
            <div className="font-bold text-slate-900 text-base tracking-tight">
              LEAD GEN AI
            </div>
            <div className="text-xs text-slate-500 font-medium mt-0.5">
              Find. Write. Send.
            </div>
          </Link>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const isActive =
              item.href === '/'
                ? pathname === '/'
                : pathname === item.href || pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3.5 py-2.5 rounded-md text-xs font-medium transition ${
                  isActive
                    ? 'bg-slate-900 text-white font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer Account Item */}
      <div className="p-4 border-t border-slate-200 bg-white">
        <div className="flex items-center gap-3 text-xs text-slate-700 font-medium px-2 py-1.5 rounded-md hover:bg-slate-100 transition cursor-pointer">
          <div className="w-7 h-7 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold">
            A
          </div>
          <div className="truncate">
            <div className="truncate font-semibold text-slate-900 text-xs">Akshat</div>
            <div className="text-[11px] text-slate-500 truncate">Account</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
