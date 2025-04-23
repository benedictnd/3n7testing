"use client"

import * as React from "react"
import { Menu } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface SidebarContextValue {
  isOpen: boolean
  setIsOpen: (value: boolean) => void
}

const SidebarContext = React.createContext<SidebarContextValue>({
  isOpen: false,
  setIsOpen: () => {},
})

export function SidebarProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = React.useState(false)

  return (
    <SidebarContext.Provider value={{ isOpen, setIsOpen }}>
      {children}
    </SidebarContext.Provider>
  )
}

export function SidebarTrigger({ className }: { className?: string }) {
  const { isOpen, setIsOpen } = React.useContext(SidebarContext)

  return (
    <Button
      variant="ghost"
      size="icon"
      className={cn("shrink-0", className)}
      onClick={() => setIsOpen(!isOpen)}
    >
      <Menu className="h-5 w-5" />
      <span className="sr-only">Toggle sidebar</span>
    </Button>
  )
}

export function SidebarInset({ children }: { children: React.ReactNode }) {
  const { isOpen } = React.useContext(SidebarContext)

  return (
    <div
      className={cn(
        "flex flex-1 flex-col",
        isOpen && "md:pl-64"
      )}
    >
      {children}
    </div>
  )
} 