"use client"

import * as React from "react"
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"

interface TrainingDistribution {
  name: string
  value: number
  color: string
}

const data: TrainingDistribution[] = [
  { name: "Morning", value: 35, color: "#4C8BF1" },
  { name: "Afternoon", value: 40, color: "#353BDF" },
  { name: "Night", value: 25, color: "#09104E" },
]

export function TrainingPieChart() {
  return (
    <div className="rounded-lg border bg-white p-6">
      <h3 className="mb-6 text-lg font-semibold">Session Distribution</h3>
      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={100}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
} 