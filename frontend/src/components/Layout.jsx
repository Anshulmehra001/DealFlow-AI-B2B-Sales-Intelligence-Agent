import { Outlet, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Users, Briefcase, BarChart3, Bot } from 'lucide-react'

export default function Layout() {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Leads', href: '/leads', icon: Users },
    { name: 'Deals', href: '/deals', icon: Briefcase },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 z-10">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-200">
            <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 leading-tight">DealFlow AI</h1>
              <p className="text-xs text-gray-400">Sales Intelligence</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-5 space-y-1">
            {navigation.map(({ name, href, icon: Icon }) => {
              const active = location.pathname === href
              return (
                <Link
                  key={name}
                  to={href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    active
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {name}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-100">
            <p className="text-xs text-gray-400">Gemini 1.5 Pro + MongoDB Atlas</p>
            <p className="text-xs text-gray-300 mt-0.5">Google Cloud Hackathon 2026</p>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64 min-h-screen">
        <Outlet />
      </div>
    </div>
  )
}
