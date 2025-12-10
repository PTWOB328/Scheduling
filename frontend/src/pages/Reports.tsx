import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material'
import { Download } from '@mui/icons-material'
import { eventService, pilotService } from '../services/api'
import { format } from 'date-fns'

interface EventAssignment {
  id: number
  pilot_id: number
  position: string
}

interface Event {
  id: number
  title: string
  start_time: string
  end_time: string
  event_type: 'b-2' | 'ob2' | 'ob3' | 'local' | 'maddog' | 'wst'
  status: 'scheduled' | 'effective' | 'cancelled'
  assignments?: EventAssignment[]
}

interface Pilot {
  id: number
  call_sign: string | null
}

const Reports: React.FC = () => {
  const [pilots, setPilots] = useState<Pilot[]>([])
  const [events, setEvents] = useState<Event[]>([])
  const [startDate, setStartDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [endDate, setEndDate] = useState(
    format(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd')
  )

  useEffect(() => {
    loadPilots()
    loadEvents()
  }, [startDate, endDate])

  const loadPilots = async () => {
    try {
      const response = await pilotService.getAll()
      setPilots(response.data)
    } catch (error) {
      console.error('Error loading pilots:', error)
    }
  }

  const loadEvents = async () => {
    try {
      const response = await eventService.getAll({
        start_date: startDate,
        end_date: endDate,
      })
      setEvents(response.data)
    } catch (error) {
      console.error('Error loading events:', error)
    }
  }

  const generateReport = () => {
    // Count events per pilot by type
    // T-38s: Local = 1, OB2 = 2, OB3 = 3
    const pilotStats: Record<number, { 
      b2: number
      t38: number  // Total T-38 flights (Local + OB2*2 + OB3*3)
      wst: number
    }> = {}
    
    pilots.forEach((pilot) => {
      pilotStats[pilot.id] = { 
        b2: 0,
        t38: 0,
        wst: 0
      }
    })

    events.forEach((event) => {
      if (event.status === 'effective' && event.assignments) {
        event.assignments.forEach((assignment) => {
          const pilotId = assignment.pilot_id
          if (pilotStats[pilotId]) {
            // Count by event type
            if (event.event_type === 'b-2') {
              pilotStats[pilotId].b2++
            } else if (event.event_type === 'local') {
              pilotStats[pilotId].t38 += 1  // Local = 1 T-38
            } else if (event.event_type === 'ob2') {
              pilotStats[pilotId].t38 += 2  // OB2 = 2 T-38s
            } else if (event.event_type === 'ob3') {
              pilotStats[pilotId].t38 += 3  // OB3 = 3 T-38s
            } else if (event.event_type === 'wst') {
              pilotStats[pilotId].wst++
            }
            // Maddog events are not counted
          }
        })
      }
    })

    return pilotStats
  }

  const handleExport = () => {
    const report = generateReport()
    const csv = [
      'Pilot,B-2,T-38,WST',
      ...pilots.map((pilot) => {
        const stats = report[pilot.id] || { b2: 0, t38: 0, wst: 0 }
        return `${pilot.call_sign || `Pilot ${pilot.id}`},${stats.b2},${stats.t38},${stats.wst}`
      }),
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `squadron_report_${startDate}_${endDate}.csv`
    a.click()
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Reports</Typography>
        <Button
          variant="contained"
          startIcon={<Download />}
          onClick={handleExport}
        >
          Export Report
        </Button>
      </Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" gap={2}>
          <TextField
            label="Start Date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            label="End Date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
        </Box>
      </Paper>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Pilot</TableCell>
              <TableCell>B-2</TableCell>
              <TableCell>T-38</TableCell>
              <TableCell>WST</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {pilots.map((pilot) => {
              const stats = generateReport()[pilot.id] || { b2: 0, t38: 0, wst: 0 }
              return (
                <TableRow key={pilot.id}>
                  <TableCell>{pilot.call_sign || `Pilot ${pilot.id}`}</TableCell>
                  <TableCell>{stats.b2}</TableCell>
                  <TableCell>{stats.t38}</TableCell>
                  <TableCell>{stats.wst}</TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

export default Reports
