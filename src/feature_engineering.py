import pyart
import numpy as np
import pandas as pd
from pyart.retrieve import mbes
from scipy import ndimage

def calculate_vil(radar, refl_field='reflectivity'):
    """
    Calculates Vertically Integrated Liquid (VIL).
    """
    refl_lin = 10.0**(radar.fields[refl_field]['data'] / 10.0)
    a = 3.44e-6
    b = 4.0 / 7.0
    m = a * (refl_lin**b)
    gate_heights = radar.gate_z['data']
    dz = np.diff(gate_heights, axis=0)
    dz = np.vstack([dz, np.zeros(dz.shape[1])])
    vil = np.sum(m * dz, axis=0)
    return vil

def get_storm_cells(vil_grid, threshold=5.0):
    """
    Identifies individual storm cells from a VIL grid using a threshold.
    """
    labeled_cells, num_features = ndimage.label(vil_grid > threshold)
    return labeled_cells, num_features

def extract_features_for_cells(radar, labeled_cells, num_features):
    """
    Extracts key features for each identified storm cell.
    """
    features = []
    refl_data = radar.fields['reflectivity']['data']
    mesh_field = mbes.get_mesh(radar, refl_field='reflectivity')
    mesh_data = mesh_field['data']

    for i in range(1, num_features + 1):
        cell_mask = (labeled_cells == i)
        if not np.any(cell_mask):
            continue
            
        cell_mask_3d = np.broadcast_to(cell_mask, refl_data.shape)
        max_reflectivity = np.max(refl_data[cell_mask_3d])
        max_mesh = np.max(mesh_data[cell_mask])
        
        gate_heights = radar.gate_z['data']
        refl_above_threshold = refl_data > 18.0
        cell_refl_above_threshold = refl_above_threshold & cell_mask_3d
        
        if np.any(cell_refl_above_threshold):
            echo_top = np.max(gate_heights[cell_refl_above_threshold]) / 1000.0 # in km
        else:
            echo_top = 0

        center_of_mass = ndimage.center_of_mass(cell_mask)
        lon, lat = radar.gate_longitude['data'][0, int(center_of_mass[1])], radar.gate_latitude['data'][int(center_of_mass[0]), 0]
        
        features.append({
            'cell_id': i,
            'max_reflectivity_dbz': max_reflectivity,
            'max_mesh_mm': max_mesh * 25.4, # Convert inches to mm
            'echo_top_km': echo_top,
            'centroid_lat': lat,
            'centroid_lon': lon,
            'scan_time': pd.to_datetime(radar.time['units'].replace('seconds since ', ''))
        })
        
    return pd.DataFrame(features)