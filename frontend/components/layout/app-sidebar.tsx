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
  Settings,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { NotificationBell } from "@/components/ui/notification-bell"
import { useNotifications } from "@/hooks/useNotifications"

// Create a temporary SidebarContext since the actual one isn't exported
const SidebarContext = React.createContext<{ isOpen: boolean }>({
  isOpen: false,
})

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

export function AppSidebar() {
  const pathname = usePathname()
  const { isOpen } = React.useContext(SidebarContext)
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications()

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 -translate-x-full border-r bg-background transition-transform md:translate-x-0",
        isOpen && "translate-x-0"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-4">
        <img src="/static/image/Logo Black.png" alt="3&7 Logo" className="h-8" />
      </div>

      {/* User Profile and Notifications */}
      <div className="border-b px-4 py-6">
        <div className="relative mx-auto mb-4 h-20 w-20">
          <img
            src="/static/image/profile-placeholder.jpg"
            alt="User Profile"
            className="h-full w-full rounded-full object-cover"
          />
          <span className="absolute bottom-0 right-0 h-4 w-4 rounded-full border-2 border-background bg-green-400" />
        </div>
        <div className="flex items-center justify-between mb-1">
          <h4 className="text-lg font-semibold">John Coach</h4>
          <NotificationBell 
            notifications={notifications}
            unreadCount={unreadCount}
            onMarkAsRead={markAsRead}
            onMarkAllAsRead={markAllAsRead}
          />
        </div>
        <p className="text-sm text-muted-foreground text-center">Head Coach</p>
      </div>

      {/* Navigation */}
      <nav className="space-y-1 p-4">
        {navigation.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground",
              pathname === item.href && "bg-accent text-accent-foreground"
            )}
          >
            {item.icon}
            {item.label}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 border-t p-4">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3"
          onClick={() => {
            // Implement logout functionality
            console.log("Logging out...")
          }}
        >
          <LogOut className="h-5 w-5" />
          Logout
        </Button>
      </div>
    </aside>
  )
} 