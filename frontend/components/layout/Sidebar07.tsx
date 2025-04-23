"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  BarChart3,
  Calendar,
  Clock,
  Home,
  LogOut,
  Menu,
  Settings,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface NavItem {
  href: string
  label: string
  icon: React.ReactNode
}

const navigation: NavItem[] = [
  {
    href: "/dashboard",
    label: "Dashboard",
    icon: <Home className="h-5 w-5" />,
  },
  {
    href: "/training-report",
    label: "Training Reports",
    icon: <BarChart3 className="h-5 w-5" />,
  },
  {
    href: "/training-history",
    label: "Training History",
    icon: <Clock className="h-5 w-5" />,
  },
  {
    href: "/calendar",
    label: "Calendar",
    icon: <Calendar className="h-5 w-5" />,
  },
  {
    href: "/settings",
    label: "Settings",
    icon: <Settings className="h-5 w-5" />,
  },
]

export function Sidebar07() {
  const pathname = usePathname()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false)

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        className="fixed right-4 top-4 z-50 rounded-lg bg-white p-2 shadow-lg md:hidden"
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
      >
        <Menu className="h-6 w-6 text-gray-600" />
      </button>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-white px-4 py-8 shadow-lg transition-transform md:translate-x-0",
          isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="mb-8 flex items-center justify-center">
          <img src="/static/image/Logo Black.png" alt="3&7 Logo" className="h-12" />
        </div>

        {/* User Profile */}
        <div className="mb-8 text-center">
          <div className="relative mx-auto mb-4 h-20 w-20">
            <img
              src="/static/image/profile-placeholder.jpg"
              alt="User Profile"
              className="h-full w-full rounded-full object-cover"
            />
            <span className="absolute bottom-0 right-0 h-4 w-4 rounded-full border-2 border-white bg-green-400" />
          </div>
          <h4 className="mb-1 text-lg font-semibold text-gray-800">John Coach</h4>
          <p className="text-sm text-gray-500">Head Coach</p>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center px-4 py-3 text-gray-600 transition-colors hover:bg-gray-50 hover:text-gray-900",
                pathname === item.href && "bg-gray-50 text-gray-900",
                "rounded-lg"
              )}
            >
              {item.icon}
              <span className="ml-3">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-gray-100 px-4 py-6">
          <Button
            variant="ghost"
            className="flex w-full items-center justify-center space-x-2"
            onClick={() => {
              // Implement logout functionality
              console.log("Logging out...")
            }}
          >
            <LogOut className="h-5 w-5" />
            <span>Logout</span>
          </Button>
        </div>
      </aside>
    </>
  )
} 