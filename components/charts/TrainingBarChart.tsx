"use client"

import * as React from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

interface TrainingData {
  week: string
  core: number
  endurance: number
}

const chartData: TrainingData[] = [
  { week: "Week 1", core: 4, endurance: 3 },
  { week: "Week 2", core: 3, endurance: 4 },
  { week: "Week 3", core: 5, endurance: 2 },
  { week: "Week 4", core: 4, endurance: 4 },
]

const chartConfig = {
  core: {
    label: "Core Training",
    color: "#4C8BF1",
  },
  endurance: {
    label: "Endurance Training",
    color: "#353BDF",
  },
} as const

export function TrainingBarChart() {
  return (
    <div className="rounded-lg border bg-white p-6">
      <h3 className="mb-6 text-lg font-semibold">Training Sessions</h3>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="week" />
            <YAxis tickFormatter={(value: number) => Math.round(value)} />
            <Tooltip />
            <Legend />
            <Bar
              dataKey="core"
              name={chartConfig.core.label}
              fill={chartConfig.core.color}
            />
            <Bar
              dataKey="endurance"
              name={chartConfig.endurance.label}
              fill={chartConfig.endurance.color}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
} 