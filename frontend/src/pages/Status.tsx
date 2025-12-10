import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  TextField,
} from '@mui/material'
import { Assessment } from '@mui/icons-material'
import { trainingService, pilotService } from '../services/api'
import { format } from 'date-fns'

interface PilotStatus {
  id: number
  pilot_id: number
  qualification_status: 'cmr' | 'bmc' | 'not_qualified'
  evaluation_month: string
  requirements_met: Record<string, boolean>
  deficiencies: string[]
}

interface Pilot {
  id: number
  call_sign: string | null
}

const Status: React.FC = () => {
  const [pilots, setPilots] = useState<Pilot[]>([])
  const [statuses, setStatuses] = useState<Record<number, PilotStatus>>({})
  const [evaluationMonth, setEvaluationMonth] = useState(
    format(new Date(), 'yyyy-MM')
  )
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadPilots()
  }, [])

  useEffect(() => {
    if (pilots.length > 0) {
      loadStatuses()
    }
  }, [pilots, evaluationMonth])

  const loadPilots = async () => {
    try {
      const response = await pilotService.getAll()
      setPilots(response.data)
    } catch (error) {
      console.error('Error loading pilots:', error)
    }
  }

  const loadStatuses = async () => {
    setLoading(true)
    try {
      // Convert YYYY-MM to YYYY-MM-01 for backend date parsing
      const evaluationDate = `${evaluationMonth}-01`
      const statusPromises = pilots.map((pilot) =>
        trainingService
          .getPilotStatus(pilot.id, evaluationDate)
          .then((res) => ({ pilotId: pilot.id, status: res.data }))
          .catch(() => null)
      )
      const results = await Promise.all(statusPromises)
      const statusMap: Record<number, PilotStatus> = {}
      results.forEach((result) => {
        if (result) {
          statusMap[result.pilotId] = result.status
        }
      })
      setStatuses(statusMap)
    } catch (error) {
      console.error('Error loading statuses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEvaluateAll = async () => {
    setLoading(true)
    try {
      // Convert YYYY-MM to YYYY-MM-01 for backend date parsing
      const evaluationDate = `${evaluationMonth}-01`
      await trainingService.evaluateAll(evaluationDate)
      loadStatuses()
    } catch (error) {
      console.error('Error evaluating all:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'cmr':
        return 'success'
      case 'bmc':
        return 'warning'
      default:
        return 'error'
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Pilot Status</Typography>
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            label="Evaluation Month"
            type="month"
            value={evaluationMonth}
            onChange={(e) => setEvaluationMonth(e.target.value)}
            InputLabelProps={{ shrink: true }}
          />
          <Button
            variant="contained"
            startIcon={<Assessment />}
            onClick={handleEvaluateAll}
            disabled={loading}
          >
            Evaluate All
          </Button>
        </Box>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Pilot</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Requirements Met</TableCell>
              <TableCell>Deficiencies</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {pilots.map((pilot) => {
              const status = statuses[pilot.id]
              return (
                <TableRow key={pilot.id}>
                  <TableCell>{pilot.call_sign || `Pilot ${pilot.id}`}</TableCell>
                  <TableCell>
                    {status ? (
                      <Chip
                        label={status.qualification_status.toUpperCase()}
                        color={getStatusColor(status.qualification_status)}
                      />
                    ) : (
                      'Not Evaluated'
                    )}
                  </TableCell>
                  <TableCell>
                    {status
                      ? `${Object.values(status.requirements_met).filter(Boolean).length}/${Object.keys(status.requirements_met).length}`
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {status && status.deficiencies.length > 0
                      ? status.deficiencies.join(', ')
                      : 'None'}
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}

export default Status
