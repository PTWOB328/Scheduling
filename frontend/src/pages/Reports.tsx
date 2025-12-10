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

interface Event {
  id: number
  title: string
  start_time: string
  end_time: string
  event_type: 'flight' | 'simulator'
  status: 'scheduled' | 'effective' | 'cancelled'
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
    // Count events per pilot
    const pilotStats: Record<number, { flights: number; sims: number }> = {}
    pilots.forEach((pilot) => {
      pilotStats[pilot.id] = { flights: 0, sims: 0 }
    })

    events.forEach((event) => {
      if (event.status === 'effective') {
        // In a real implementation, you'd get assignments from the event
        // For now, this is a placeholder
      }
    })

    return pilotStats
  }

  const handleExport = () => {
    const report = generateReport()
    const csv = [
      'Pilot,Flights,Simulators',
      ...pilots.map(
        (pilot) =>
          `${pilot.call_sign || `Pilot ${pilot.id}`},${report[pilot.id]?.flights || 0},${report[pilot.id]?.sims || 0}`
      ),
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
              <TableCell>Flights</TableCell>
              <TableCell>Simulators</TableCell>
              <TableCell>Total Events</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {pilots.map((pilot) => {
              const stats = generateReport()[pilot.id] || { flights: 0, sims: 0 }
              return (
                <TableRow key={pilot.id}>
                  <TableCell>{pilot.call_sign || `Pilot ${pilot.id}`}</TableCell>
                  <TableCell>{stats.flights}</TableCell>
                  <TableCell>{stats.sims}</TableCell>
                  <TableCell>{stats.flights + stats.sims}</TableCell>
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
