'use client';

import { ReactNode, useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authService } from '@/lib/auth';
import { 
  GraduationCap, 
  LayoutDashboard, 
  Map, 
  Target, 
  BookOpen,
  ClipboardList,
  LogOut,
  Sparkles,
  Award,
  Menu,
  X,
  MessageCircle
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const [mounted, setMounted] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    setMounted(true);
    setUser(authService.getCurrentUser());
  }, []);

  useEffect(() => {
    // Close mobile menu when route changes
    setMobileMenuOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    authService.logout();
    router.push('/login');
  };

  const navItems = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/dashboard/my-courses', icon: Award, label: 'My Courses' },
    { href: '/dashboard/learning-path', icon: Map, label: 'Learning Path' },
    { href: '/dashboard/skill-gaps', icon: Target, label: 'Skill Gaps' },
    { href: '/dashboard/assessments', icon: ClipboardList, label: 'Assessments' },
    { href: '/dashboard/courses', icon: BookOpen, label: 'Courses' },
    { href: '/dashboard/chat', icon: MessageCircle, label: 'Chat' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50">
        <div className="flex items-center justify-between h-full px-4">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="p-1.5 bg-primary-600 rounded-lg">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-900">SkillStudio</span>
          </Link>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40 pt-16"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar - Desktop & Mobile Slide-in */}
      <aside className={`
        fixed left-0 h-full w-64 bg-white border-r border-gray-200 flex flex-col z-40 transition-transform duration-300
        lg:top-0
        top-16
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="p-2 bg-primary-600 rounded-lg">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">SkillStudio</h1>
              <p className="text-xs text-gray-500 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                AI-Powered
              </p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary-50 text-primary-700 font-medium'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-gray-200">
          {mounted && (
            <div className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-lg mb-2">
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
                {user?.full_name?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.full_name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors text-sm"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="lg:ml-64 min-h-screen pt-16 lg:pt-0">
        {children}
      </main>
    </div>
  );
}
