"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  BarChart,
  Calendar,
  ChevronDown,
  ChevronRight,
  LayoutDashboard,
  LogOut,
  Settings,
  User,
  Users,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface NavItem {
  title: string
  href: string
  icon: React.ReactNode
  submenu?: NavItem[]
}

const navItems: NavItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: <LayoutDashboard className="h-5 w-5" />,
  },
  {
    title: "Training Reports",
    href: "/training-report",
    icon: <BarChart className="h-5 w-5" />,
    submenu: [
      {
        title: "Monthly Overview",
        href: "/training-report/monthly",
        icon: <ChevronRight className="h-4 w-4" />,
      },
      {
        title: "Session Analysis",
        href: "/training-report/sessions",
        icon: <ChevronRight className="h-4 w-4" />,
      },
    ],
  },
  {
    title: "Calendar",
    href: "/calendar",
    icon: <Calendar className="h-5 w-5" />,
  },
  {
    title: "Users",
    href: "/users",
    icon: <Users className="h-5 w-5" />,
  },
  {
    title: "Settings",
    href: "/settings",
    icon: <Settings className="h-5 w-5" />,
  },
]

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()
  const [expanded, setExpanded] = React.useState<string | null>(null)

  const toggleSubmenu = (title: string) => {
    setExpanded(expanded === title ? null : title)
  }

  const renderNavItem = (item: NavItem, depth = 0) => {
    const isActive = pathname === item.href
    const hasSubmenu = item.submenu && item.submenu.length > 0
    const isExpanded = expanded === item.title

    return (
      <div key={item.href}>
        <Link
          href={item.href}
          className={cn(
            "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
            isActive ? "bg-gray-100 text-gray-900" : "",
            depth > 0 ? "ml-6" : "",
            "group"
          )}
          onClick={(e: React.MouseEvent) => {
            if (hasSubmenu) {
              e.preventDefault()
              toggleSubmenu(item.title)
            }
          }}
        >
          {item.icon}
          <span className="flex-1 font-medium">{item.title}</span>
          {hasSubmenu && (
            <ChevronDown
              className={cn(
                "h-4 w-4 text-gray-500 transition-transform",
                isExpanded ? "rotate-180" : "",
                "group-hover:text-gray-900"
              )}
            />
          )}
        </Link>
        {hasSubmenu && isExpanded && (
          <div className="mt-1 space-y-1">
            {item.submenu?.map((subItem) => renderNavItem(subItem, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={cn("flex h-screen w-64 flex-col border-r bg-white", className)}>
      {/* User Profile Section */}
      <div className="flex flex-col items-center border-b p-6">
        <div className="relative h-16 w-16">
          <div className="absolute h-full w-full rounded-full bg-gray-200">
            <User className="h-full w-full p-4 text-gray-500" />
          </div>
        </div>
        <h2 className="mt-4 font-semibold">John Coach</h2>
        <p className="text-sm text-gray-500">Head Coach</p>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="mt-2">
              View Profile
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuItem className="text-red-600">
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Navigation Section */}
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => renderNavItem(item))}
      </nav>

      {/* Footer Section */}
      <div className="border-t p-4">
        <p className="text-center text-sm text-gray-500">
          3&7 Training Platform v1.0
        </p>
      </div>
    </div>
  )
} 