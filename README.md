# auto-source-placement-based-on-mesh

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
