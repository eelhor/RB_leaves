import bpy

bl_info = {
    "name": "RB leaves",
    "author": "eelh",
    "version": (0, 1),
    "blender": (2, 90, 0),
    "category": "Object",
    "location": "3D Viewport -> UI",
    "description": "Prepare leaves objects for rigid body simulation",
}


def apply_transforms(object_pattern):
    select_objects_by_pattern(object_pattern + "*")
    bpy.ops.object.visual_transform_apply()
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')


def delete_objects(object_pattern):
    select_objects_by_pattern(object_pattern + "*")
    bpy.ops.object.delete(use_global=False)


def select_objects_by_pattern(pattern):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern=pattern)
    if bpy.context.selected_objects:
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    else:
        show_message_box("No " + pattern + " objects found", "Error", 'ERROR')
        return 'CANCELLED'


def create_collection(collection_name):
    collection = bpy.data.collections.new(collection_name)
    collection.name = collection_name
    # Link new collection to currently active
    bpy.context.collection.children.link(collection)


def create_new_collection_in_root_collection(new_collection_name, root_view_layer_collection):
    bpy.context.view_layer.active_layer_collection = root_view_layer_collection
    create_collection(new_collection_name)
    bpy.context.view_layer.active_layer_collection = root_view_layer_collection.children[-1]
    return bpy.context.collection


def show_message_box(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def RB_leaf(): return bpy.context.scene.pattern


def RB_holder(): return "rb_holder_" + bpy.context.scene.pattern


def RB_base(): return "rb_base_" + bpy.context.scene.pattern


def RB_constraint(): return "rb_constraint_" + bpy.context.scene.pattern


class VIEW3D_PT_rbleaves(bpy.types.Panel):
    """Creates a Panel in 3D viewport properties"""
    bl_label = "RB leaves"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RB leaves"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.prop(context.scene, 'pattern', text='')

        row = layout.row()
        row.label(text="Select leaves objects")

        row = layout.row()
        row.operator("operator.setup_rb", text="Setup rigid bodies")

        row = layout.row()
        row.label(text="Prepare object with particle systems")

        row = layout.row()
        row.operator("operator.setup_constraints", text="Convert particle systems")

        row = layout.row()
        row.label(text="Set passive RB to collision objects")

        row = layout.row()
        row.label(text="Run animation or bake RB")

        row = layout.row()
        row.operator("operator.apply_transforms", text="Apply transforms, cleanup")

        row = layout.row()
        row.label(text="Helpers:")

        row = layout.row()
        row.operator("operator.select_holders", text="Select holders")

        row = layout.row()
        row.operator("operator.select_leaves", text="Select leaves")

        row = layout.row()
        row.operator("operator.select_bases", text="Select bases")

        row = layout.row()
        row.operator("operator.select_constraints", text="Select constraints")


class SetupRB(bpy.types.Operator):
    bl_idname = "operator.setup_rb"
    bl_label = "Setup RB"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Setup RB for objects"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        # Check if objects are selected
        if not selected_objects:
            show_message_box("No visible objects selected", "Error", "ERROR")
            return {'CANCELLED'}
        # Create root collection in master collection
        create_new_collection_in_root_collection("RB_leaves", bpy.context.view_layer.layer_collection)
        root_collection = bpy.context.view_layer.active_layer_collection
        # Create base mesh - origin with no vertices
        bpy.ops.mesh.primitive_cube_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        base_mesh = bpy.context.object.data
        base_mesh.name = "rb_base_mesh"
        bpy.ops.object.delete(use_global=False)

        cursor = bpy.context.scene.cursor
        for obj in selected_objects:
            # Rename object
            index = str('{:02d}'.format(selected_objects.index(obj)))
            obj.name = RB_leaf() + "_" + index
            # Set active RB for object
            bpy.data.objects[obj.name].select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.rigidbody.object_add(type='ACTIVE')
            # Link object to new collection
            collection = create_new_collection_in_root_collection("rb_" + RB_leaf() + "_" + index, root_collection)
            collection.objects.link(obj)
            # Set cursor location and rotation to object's
            cursor.location = obj.location
            cursor.rotation_euler = obj.rotation_euler
            # Create holder object
            bpy.ops.object.empty_add(type='SPHERE', radius=0.01, align='CURSOR',
                                     location=cursor.location,
                                     rotation=cursor.rotation_euler)
            holder = bpy.context.selected_objects[0]
            holder.name = RB_holder() + "_" + index
            # Parent object to parent
            obj.parent = holder
            obj.matrix_parent_inverse = holder.matrix_world.inverted()
            # Create base object
            base = bpy.data.objects.new(name="base", object_data=base_mesh)
            base.name = RB_base() + "_" + index
            collection.objects.link(base)
            base.parent = holder
            # Set passive RB to base object
            bpy.data.objects[base.name].select_set(True)
            bpy.context.view_layer.objects.active = base
            bpy.ops.rigidbody.object_add(type='PASSIVE')
            # Create constraint object
            bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.02, align='WORLD', location=(0, 0, 0))
            constraint = bpy.context.selected_objects[0]
            constraint.name = RB_constraint() + "_" + index
            constraint.parent = holder
            # Setup RB constraint
            bpy.ops.rigidbody.constraint_add(type='GENERIC')
            generic_constraint = bpy.context.object.rigid_body_constraint
            generic_constraint.use_limit_ang_x = True
            generic_constraint.use_limit_ang_y = True
            generic_constraint.use_limit_ang_z = True
            generic_constraint.use_limit_lin_x = True
            generic_constraint.use_limit_lin_y = True
            generic_constraint.use_limit_lin_z = True
            generic_constraint.limit_ang_x_lower = -0.349066
            generic_constraint.limit_ang_x_upper = 0.349066
            generic_constraint.limit_ang_y_lower = -0.349066
            generic_constraint.limit_ang_y_upper = 0.349066
            generic_constraint.limit_ang_z_lower = -3.14159
            generic_constraint.limit_ang_z_upper = 3.14159
            generic_constraint.limit_lin_x_lower = 0
            generic_constraint.limit_lin_x_upper = 0
            generic_constraint.limit_lin_y_lower = 0
            generic_constraint.limit_lin_y_upper = 0
            generic_constraint.limit_lin_z_lower = 0
            generic_constraint.limit_lin_z_upper = 0
            generic_constraint.object1 = base
            generic_constraint.object2 = obj
        return {'FINISHED'}


class SetupRBConstraints(bpy.types.Operator):
    bl_idname = "operator.setup_constraints"
    bl_label = "Setup RB constraints"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Set objects for RB constraints"

    def execute(self, context):
        current_object = bpy.context.object
        # Check if object is selected
        if not current_object:
            show_message_box("No visible selected object found", "Error", "ERROR")
            return {'CANCELLED'}
        # Check if object has modifiers
        if not current_object.modifiers:
            show_message_box("Object has no particle system", "Error", "ERROR")
            return {'CANCELLED'}
        # Check if object has particle system modifier visible
        visible_particle_system = False
        for modifier in current_object.modifiers:
            if modifier.name[:8] == 'Particle':
                if current_object.modifiers[modifier.name].show_viewport:
                    visible_particle_system = True
                    break
        if not visible_particle_system:
            show_message_box("Object has no visible particle system", "Error", "ERROR")
            return {'CANCELLED'}
        # Collection  in which converted particles will appear
        collection_to_unlink = bpy.context.object.users_collection[-1]
        if collection_to_unlink.name[:14] == "RigidBodyWorld":
            collection_to_unlink = bpy.context.object.users_collection[0]
        # Convert particles
        bpy.ops.object.duplicates_make_real(use_hierarchy=True)
        # Check if there are any particles converted
        leaves = bpy.context.selected_objects
        if not leaves:
            show_message_box("No particles found", "Error", "ERROR")
            return {'CANCELLED'}
        # Create new collection for particles in master collection
        collection_to_link = create_new_collection_in_root_collection("leaves_instances", bpy.context.view_layer.layer_collection)
        # Move particles to new collection
        for leaf_object in leaves:
            collection_to_unlink.objects.unlink(leaf_object)
            collection_to_link.objects.link(leaf_object)
        # Hide particle system modifiers from viewport and render
        for modifier in current_object.modifiers:
            if modifier.name[:8] == 'Particle':
                # TODO: Why hiding breaks RB?
                bpy.data.particles[modifier.particle_system.name].instance_collection = None
                # current_object.modifiers[modifier.name].show_viewport = False
                # current_object.modifiers[modifier.name].show_render = False
        # Check if RB constraint objects are among particles
        if select_objects_by_pattern(RB_constraint() + "*") == 'CANCELLED':
            return {'CANCELLED'}
        # Setup constraints
        obj_name_len = len(RB_constraint())
        for obj in bpy.context.selected_objects:
            suffix = obj.name[obj_name_len:]
            obj.rigid_body_constraint.object1 = bpy.data.objects[RB_base() + suffix]
            obj.rigid_body_constraint.object2 = bpy.data.objects[RB_leaf() + suffix]
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}


class ApplyRBTransforms(bpy.types.Operator):
    bl_idname = "operator.apply_transforms"
    bl_label = "Apply RB transforms"
    bl_description = "Apply RB transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        apply_transforms(RB_leaf())
        bpy.context.scene.rigidbody_world.enabled = False
        delete_objects(RB_holder())
        delete_objects(RB_base())
        delete_objects(RB_constraint())
        return {'FINISHED'}


class SelectLeaves(bpy.types.Operator):
    bl_idname = "operator.select_leaves"
    bl_label = "Select leaves"
    bl_description = "Select leaves"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_objects_by_pattern(RB_leaf() + "*")
        return {'FINISHED'}


class SelectHolders(bpy.types.Operator):
    bl_idname = "operator.select_holders"
    bl_label = "Select holders"
    bl_description = "Select holders"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_objects_by_pattern(RB_holder() + "*")
        return {'FINISHED'}


class SelectBases(bpy.types.Operator):
    bl_idname = "operator.select_bases"
    bl_label = "Select bases"
    bl_description = "Select bases"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_objects_by_pattern(RB_base() + "*")
        return {'FINISHED'}


class SelectConstraints(bpy.types.Operator):
    bl_idname = "operator.select_constraints"
    bl_label = "Select constraints"
    bl_description = "Select constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        select_objects_by_pattern(RB_constraint() + "*")
        return {'FINISHED'}


blender_classes = [
    VIEW3D_PT_rbleaves,
    SetupRB,
    SetupRBConstraints,
    ApplyRBTransforms,
    SelectLeaves,
    SelectHolders,
    SelectBases,
    SelectConstraints,
]


def register():
    bpy.types.Scene.pattern = bpy.props.StringProperty(
        name='Name pattern',
        description='\nExample: leaf_01.002\n   name pattern - leaf\n   index - 01\n   instance - 002',
        default='leaf',
        subtype='NONE',
    )
    for blender_class in blender_classes:
        bpy.utils.register_class(blender_class)
        print("Registered {}".format(bl_info['name']))


def unregister():
    del bpy.types.Scene.pattern
    for blender_class in blender_classes:
        bpy.utils.unregister_class(blender_class)
        print("Unregistered {}".format(bl_info['name']))
