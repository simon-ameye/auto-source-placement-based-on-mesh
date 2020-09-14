# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 14:39:02 2020

@author: simon ameye : simon.ameye@avl.com

This script is used if you want to use mesh shapes as sources in PreonLab, as it is possible in conventional mesh based CFD software.
The script will automatically place sources based on a mesh.
The script will do the following: 
1)	Find all the mesh objects in the scene scene_name at scene_path
2)	Select only the one which contain “inlet_name” in their name
3)	Read mesh file associated and remove incompatible “color” lines in it
WARNING: If absolute path, set mesh_path_is_relative = False
4)	Detect size of source (if it is a rectangle, it will detect length and height)
5)	Create a source with the same size and place it at the center of gravity
6)	Align the source direction with mesh normal vector.
WARNING: to reverse source direction, set initial_source_vector = (0, -1, 0)
7)	WARNING: direction is aligned, but orientation is not! Please use PreonLab GUI option: “local coordinates system” and align sources using euler angles.
8)	Connections of sources will be deleted, mesh is disabled and hidden
9)	Set the flow rate according to array flow_rates, sorted as in PreonLab GUI
Then, you can open PreonLab scene again.
"""
import preonpy
import meshio
import numpy as np
import os
import math

#user parameters
inlet_name = "Inlet"
scene_path = "C:/Users/u22p37/Downloads/autoplace/"
scene_name = "auto_place_sources"
mesh_path_is_relative = True #In general case, if mesh file is inside PreonLab folder, path to object is relative. If outside, it is absolute.
flow_rates = np.array([0.    , 0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007,
                       0.0008, 0.0009, 0.001 , 0.0011, 0.0012, 0.0013, 0.0014, 0.0015,
                       0.0016, 0.0017, 0.0018, 0.0019, 0.002 , 0.0021, 0.0022, 0.0023,
                       0.0024, 0.0025, 0.0026, 0.0027, 0.0028, 0.0029, 0.003 , 0.0031,
                       0.0032, 0.0033, 0.0034, 0.0035, 0.0036, 0.0037, 0.0038, 0.0039,
                       0.004 , 0.0041, 0.0042, 0.0043, 0.0044, 0.0045, 0.0046, 0.0047,
                       0.0048, 0.0049, 0.005 , 0.0051, 0.0052, 0.0053, 0.0054, 0.0055,
                       0.0056, 0.0057, 0.0058, 0.011])
initial_source_vector = (0, 1, 0)

def removecontent(inputFileName, outputFileName):

    input = open(inputFileName, "r")
    if not os.path.exists(os.path.dirname(outputFileName)):
        os.makedirs(os.path.dirname(outputFileName))
    output = open(outputFileName, "w")
    output.write(input.readline())
    for line in input:
        if not line.lstrip().startswith("color"):
            output.write(line)
    input.close()
    output.close()

def euler_from_vecs(a=None, b=None):
    """
    Filename: align_vecotrs.py
    Created Date: Friday, May 20th 2020, 6:12:09 pm
    Author: Shreyas Joshi - Fifty2 Technology GmbH
    Email: shreyas.joshi@fifty2.eu
    
    Calculates euler angles to make vector a point in the direction of vector b
    Parameters
    ----------
    a : (x,y,z) vector (optional)
        default value (0,-1,0) pointing direction of AreaSource in PL-v4.2
        when its euler angles are (0,0,0)
    b : (x,y,z) vector
    Returns
    -------
    (PHI,THETA, PSI) for inputting in PreonLab
    """
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    I = np.identity(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    R = I + K + K @ K * ((1 - c) / (s ** 2))
    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0
    return np.array([x, y, z]) * 180 / np.pi

s=preonpy.Scene(scene_path + scene_name + ".prscene")
i = 0;
for obj_name in s.object_names: 
    obj = s.find_object(obj_name)
    if obj.type == "Mesh" and inlet_name in obj_name :
        print(obj_name + " is area source")
        obj["behavior"] = "inactive"
        obj["render mode"] = "invisible"
        source = s.create_object("Area source")
        source["inflow unit"] = "volumeFlowRate"
        ressource = obj.get_connected_objects("MeshResource", 0)
        ressource = ressource[0]
        meshpath = ressource["mesh file"]
        if mesh_path_is_relative :
            meshpath = scene_path + scene_name + "/" + meshpath
        print("Object mesh path = " + meshpath)
        custom_path = scene_path + "customgeo/" + str(i) + ".stl"
        removecontent(meshpath, custom_path)
        print("New mesh path = " + custom_path)
        mesh = meshio.read(custom_path)
        center = np.average(mesh.points / 1000, axis = 0)
        source["position"] = center
        points = mesh.points[0:3, :]/1000
        length1 = np.sqrt(np.sum(np.square(points[0] - points[1])))
        length2 = np.sqrt(np.sum(np.square(points[1] - points[2])))
        length3 = np.sqrt(np.sum(np.square(points[0] - points[2])))
        length = np.sort([length1, length2, length3])
        source["scale"] = [length[1], 0, length[0]]
        vec = points[2] - points[1]
        normal_vector = np.cross(points[1] - points[0], points[2] - points[0])
        normal_vector = normal_vector / np.linalg.norm(normal_vector)
        source["euler angles"] = euler_from_vecs(a = initial_source_vector, b = normal_vector)
        for connected_obj in source.get_connected_objects("TriangleMesh", False):
            preonpy.disconnect_objects(connected_obj, source, "TriangleMesh")
        i = i + 1
s.save()
        

