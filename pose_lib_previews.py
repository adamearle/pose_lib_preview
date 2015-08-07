import os
import bpy
from bpy.props import StringProperty
from bpy.props import EnumProperty
import bpy.utils.previews


# Dict to hold the ui previews collection
preview_collections = {}


# create th previews and an enum with label, tooltip and preview as custom icon
def generate_previews(self, context):
    enum_items = []

    if context is None:
        return enum_items

    obj = self
    directory = obj.pose_previews_dir

    pcoll = preview_collections["pose_previews"]

    if directory == pcoll.pose_previews_dir:
        return pcoll.pose_previews

    # if bpy.data.filepath:
    #     blend_dir = os.path.dirname(bpy.data.filepath)
    #     arm_name = bpy.path.clean_name(self.name)
    #     directory = os.path.join(blend_dir, "pose_previews", arm_name)
    # else:
    #     directory = pcoll.pose_previews_dir

    # if directory == pcoll.pose_previews_dir:
    #     return pcoll.pose_previews

    if directory and os.path.isdir(bpy.path.abspath(directory)):
        if pcoll:
            pcoll.clear()
        image_paths = []
        for fn in os.listdir(bpy.path.abspath(directory)):
            if os.path.splitext(fn)[-1].lower() == ".png":
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(bpy.path.abspath(directory), name)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.pose_previews = enum_items
    pcoll.pose_previews_dir = directory
    return pcoll.pose_previews


def update_pose(self, context):
    fn = os.path.basename(self.pose_previews)
    value = int(os.path.splitext(fn)[0]) - 1
    if self.pose_library.pose_markers:
        bpy.ops.poselib.apply_pose(pose_index=value)


# def set_enum(self, value):
#     print("value: {}".format(value))
#     pcoll = preview_collections["pose_previews"]
#     print(list(pcoll.keys())[value])


class PoseLibPreviewPanel(bpy.types.Panel):
    """Creates a Panel in the armature context of the properties editor"""
    bl_label = "Pose Library Previews"
    bl_idname = "DATA_PT_pose_previews"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'ARMATURE' and obj.pose_library

    def draw(self, context):
        layout = self.layout
        obj = context.object
        # previews
        layout.template_icon_view(obj, "pose_previews", show_labels=False)
        layout.prop(obj, "pose_previews_dir")


def register():
    bpy.types.Object.pose_previews = EnumProperty(
        items=generate_previews,
        update=update_pose)
    bpy.types.Object.pose_previews_dir = StringProperty(
        name="Folder Path",
        subtype='DIR_PATH',
        default="")

    pcoll = bpy.utils.previews.new()
    pcoll.pose_previews_dir = ""
    pcoll.pose_previews = ()
    preview_collections["pose_previews"] = pcoll


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    del bpy.types.Object.pose_previews
    del bpy.types.Object.pose_previews_dir