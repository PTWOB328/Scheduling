import React, { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
} from '@mui/material'
import { Add, Edit, Delete } from '@mui/icons-material'
import { pilotService } from '../services/api'

interface Pilot {
  id: number
  call_sign: string | null
  rank: string | null
  qualifications: string[]
  is_active: boolean
}

const Pilots: React.FC = () => {
  const [pilots, setPilots] = useState<Pilot[]>([])
  const [openDialog, setOpenDialog] = useState(false)
  const [selectedPilot, setSelectedPilot] = useState<Pilot | null>(null)

  useEffect(() => {
    loadPilots()
  }, [])

  const loadPilots = async () => {
    try {
      const response = await pilotService.getAll()
      setPilots(response.data)
    } catch (error) {
      console.error('Error loading pilots:', error)
    }
  }

  const handleEdit = (pilot: Pilot) => {
    setSelectedPilot(pilot)
    setOpenDialog(true)
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this pilot?')) return
    try {
      await pilotService.delete(id)
      loadPilots()
    } catch (error) {
      console.error('Error deleting pilot:', error)
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Pilots</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => {
            setSelectedPilot(null)
            setOpenDialog(true)
          }}
        >
          Add Pilot
        </Button>
      </Box>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Call Sign</TableCell>
              <TableCell>Rank</TableCell>
              <TableCell>Qualifications</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {pilots.map((pilot) => (
              <TableRow key={pilot.id}>
                <TableCell>{pilot.call_sign || 'N/A'}</TableCell>
                <TableCell>{pilot.rank || 'N/A'}</TableCell>
                <TableCell>{pilot.qualifications.join(', ') || 'None'}</TableCell>
                <TableCell>{pilot.is_active ? 'Active' : 'Inactive'}</TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => handleEdit(pilot)}>
                    <Edit />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleDelete(pilot.id)}>
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {openDialog && (
        <PilotDialog
          pilot={selectedPilot}
          open={openDialog}
          onClose={() => {
            setOpenDialog(false)
            setSelectedPilot(null)
          }}
          onSave={loadPilots}
        />
      )}
    </Box>
  )
}

interface PilotDialogProps {
  pilot: Pilot | null
  open: boolean
  onClose: () => void
  onSave: () => void
}

const PilotDialog: React.FC<PilotDialogProps> = ({ pilot, open, onClose, onSave }) => {
  const [callSign, setCallSign] = useState(pilot?.call_sign || '')
  const [rank, setRank] = useState(pilot?.rank || '')
  const [loading, setLoading] = useState(false)

  const handleSave = async () => {
    setLoading(true)
    try {
      const pilotData = {
        call_sign: callSign,
        rank: rank,
        qualifications: [],
      }
      if (pilot?.id) {
        await pilotService.update(pilot.id, pilotData)
      } else {
        await pilotService.create(pilotData)
      }
      onSave()
      onClose()
    } catch (error) {
      console.error('Error saving pilot:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{pilot ? 'Edit Pilot' : 'New Pilot'}</DialogTitle>
      <DialogContent>
        <TextField
          fullWidth
          label="Call Sign"
          value={callSign}
          onChange={(e) => setCallSign(e.target.value)}
          margin="normal"
        />
        <TextField
          fullWidth
          label="Rank"
          value={rank}
          onChange={(e) => setRank(e.target.value)}
          margin="normal"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button onClick={handleSave} variant="contained" disabled={loading}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default Pilots
