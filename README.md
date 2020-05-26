# RB_leaves
Blender addon. Prepare leaves objects for rigid body simulation.

<p align="center">
  <img width="550" height="288" src="https://imgur.com/oqr43sg">
</p>
<p align="center">
<b>Warning: </b>
</p>
<p align="center">
This method does not prevent intersections, but can reduce them.
</p>

<p align="center">
  <img width="232" height="440" src="https://imgur.com/WIvhcjD">
</p>
<p align="center">

<p><b>Name pattern</b> field allows to specify the name for leaves objects.
<p>Addon follows next naming convention: [name_pattern]_[index].[instance]
<p>Example: leaf_01.002

<b>Setup rigid bodies</b>: Renames selected objects, creates RB helpers objects, sets up RB.
<p> RB helpers objects consist of:
<p> constraint - empty object with RB constraint, set to Generic, which holds leaf object to base RB helpers object, allowing specified rotations.
<p> base - object with no vertices, only origin, with RB set to passive type.
<p> holder - empty object, set as parent for leaf and RB helpers objects, helps manipulating(translation, rotation, scale) the whole construction.

<b>Convert particle systems</b>: Converts particle systems. Sets appropriate objects for RB constraints.

<b>Apply RB transforms</b>: Applies RB transforms, removes RB helpers objects.

<b>Helpers</b>: Selects leaves and RB helpers objects by provided pattern.
