import React from "react";
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';

export default function QKDForm({ params, onChange }) {
  const handleChange = (e) => {
    const { name, value, type } = e.target;
    onChange({ ...params, [name]: type === 'number' ? Number(value) : value });
  };

  return (
    <Box component="form" mb={4} display="flex" gap={3} alignItems="center" flexWrap="wrap" onSubmit={e => e.preventDefault()}>
      <FormControl sx={{ minWidth: 180 }} size="small">
        <InputLabel id="protocol-label">Protocol</InputLabel>
        <Select
          labelId="protocol-label"
          name="protocol"
          value={params.protocol}
          label="Protocol"
          onChange={handleChange}
        >
          <MenuItem value="dps">DPS-QKD</MenuItem>
          <MenuItem value="cow">COW-QKD</MenuItem>
          <MenuItem value="bb84">BB84-QKD</MenuItem>
        </Select>
      </FormControl>
      {params.protocol === "cow" && (
        <>
          <TextField
            name="cow_monitor_pulse_ratio"
            label="COW Monitor Pulse Ratio"
            type="number"
            size="small"
            inputProps={{ step: 0.01 }}
            value={params.cow_monitor_pulse_ratio}
            onChange={handleChange}
            sx={{ minWidth: 200 }}
          />
          <TextField
            name="cow_detection_threshold_photons"
            label="COW Detection Threshold (Photons)"
            type="number"
            size="small"
            value={params.cow_detection_threshold_photons ?? 1}
            onChange={handleChange}
            sx={{ minWidth: 200 }}
          />
          <TextField
            name="cow_extinction_ratio_db"
            label="COW Extinction Ratio (dB)"
            type="number"
            size="small"
            value={params.cow_extinction_ratio_db}
            onChange={handleChange}
            sx={{ minWidth: 200 }}
          />
        </>
      )}
    </Box>
  );
} 