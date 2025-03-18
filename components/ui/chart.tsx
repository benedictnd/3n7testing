"use client"

import * as React from "react"
import { type TooltipProps } from "recharts"
import { cn } from "@/lib/utils"

export interface ChartConfig {
  [key: string]: {
    label: string
    color: string
  }
}

interface ChartContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  config: ChartConfig
}

export function ChartContainer({
  children,
  config,
  className,
  ...props
}: ChartContainerProps) {
  const styles = React.useMemo(() => {
    return Object.entries(config).reduce<Record<string, string>>((acc, [key, value]) => {
      acc[`--color-${key}`] = value.color
      return acc
    }, {})
  }, [config])

  return (
    <div className={cn("w-full h-full", className)} style={styles} {...props}>
      {children}
    </div>
  )
}

interface ChartTooltipContentProps extends Partial<TooltipProps<any, any>> {
  indicator?: "solid" | "dashed"
  hideLabel?: boolean
}

export function ChartTooltipContent({
  active,
  payload,
  indicator = "solid",
  hideLabel = false,
}: ChartTooltipContentProps) {
  if (!active || !payload?.length) return null

  return (
    <div className="rounded-lg border bg-background p-2 shadow-sm">
      <div className="grid gap-2">
        {payload.map((item: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-1">
              <div
                className={cn(
                  "h-1 w-1 rounded-full",
                  indicator === "solid" ? "h-2 w-2" : "border-2"
                )}
                style={{ background: item.color }}
              />
              {!hideLabel && <span className="font-medium">{item.name}</span>}
            </div>
            <span>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
} 