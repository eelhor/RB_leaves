# RB_leaves
Blender addon. Helps to prepare leaves objects for rigid body simulation.
<p align="center">
  <img src="https://i.imgur.com/oqr43sg.jpg">
</p>
<p align="center">
<b>Warning: </b>
</p>
<p align="center">
This method does not prevent intersections, but can reduce them.
</p>
<p align="center">
  <img src="https://i.imgur.com/S5v9cm8.jpg">
</p>

<p><b>Name pattern</b> field allows to specify the name for leaves objects.</p>
<p>Addon follows next naming convention: [name_pattern]_[index].[instance]</p>
<p>Example: leaf_01.002</p>

<p><b>Setup rigid bodies</b>: Renames selected objects, creates RB helpers objects, sets up RB.</p>
<p>RB helpers:</p>
<p>- constraint - empty object with RB constraint, set to Generic, which holds leaf object to base RB helper object, allowing specified rotations.</p>
<p>- base - object with no vertices, only origin, with RB set to passive type.</p>
<p>- holder - empty object, set as parent for leaf and RB helpers objects, helps manipulating the whole construction.</p>

<p><b>Convert particle systems</b>: Converts particle systems. Sets appropriate objects for RB constraints.</p>

<p><b>*Shrinkwrap leaves</b>: Adds shrinkwrap constraint to leaves objects with target set to provided object.</p>

<p><b>Apply RB transforms, cleanup</b>: Applies RB transforms, removes RB helpers objects.</p>

<b>Helpers</b>: Select leaves and RB helpers objects by provided pattern.
<p>
<a href="https://www.youtube.com/playlist?list=PLWfG_VUdQuzPsM6DI6yYxCTNr8kM3ae-O">Demo video</a>
</p>
