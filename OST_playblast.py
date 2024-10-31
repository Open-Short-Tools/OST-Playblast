import bpy
import os
from bpy.props import IntProperty, StringProperty, EnumProperty

class VIEW3D_OT_playblast_operator(bpy.types.Operator):
    """Playblast Animation from Viewport"""
    bl_idname = "view3d.playblast_operator"
    bl_label = "EXPORT PLAYBLAST"
    
    output_directory: StringProperty(
        name="Output Directory",
        description="Directory where the output file will be saved",
        default="//",  # Default to the current blend file's directory
        subtype='DIR_PATH'  # Specify that this is a directory path
    )
    
    file_name: StringProperty(
        name="File Name",
        description="Name of the output file",
        default="playblast"
    )
    
    file_format: EnumProperty(
        name="File Format",
        description="File format for the output file",
        items=[
            ('FFMPEG', 'Video', 'Export as video'),
            ('PNG', 'Image Sequence', 'Export as image sequence')
        ],
        default='FFMPEG'
    )

    video_codec: EnumProperty(
        name="Video Codec",
        description="Codec for video export",
        items=[
            ('H264', 'H.264', 'H.264 Codec'),
            ('MPEG4', 'MPEG4', 'MPEG4 Codec')
        ],
        default='H264'
    )
    
    container_format: EnumProperty(
        name="Container",
        description="Container format for video export",
        items=[
            ('MPEG4', 'MPEG4', 'MPEG4 Container'),
            ('AVI', 'AVI', 'AVI Container'),
            ('QUICKTIME', 'QuickTime', 'QuickTime Container')
        ],
        default='QUICKTIME'
    )
    
    resolution_scale: IntProperty(
        name="Resolution Scale",
        description="Scale of the output resolution (1-100)",
        default=75,
        min=1,
        max=100
    )
    
    resolution_x: IntProperty(
        name="Resolution X",
        description="Width of the output resolution",
        default=1920,
        min=1
    )
    
    resolution_y: IntProperty(
        name="Resolution Y",
        description="Height of the output resolution",
        default=1080,
        min=1
    )
    
    start_frame: IntProperty(
        name="Start Frame",
        description="Start frame for playblast",
        default=bpy.context.scene.frame_start,
        min=1
    )

    end_frame: IntProperty(
        name="End Frame",
        description="End frame for playblast",
        default=bpy.context.scene.frame_end,
        min=1
    )

    def draw(self, context):
        layout = self.layout
        layout.scale_x = 5.0
    
        # Output Directory
        layout.label(text="Output Settings:")
        layout.prop(self, "output_directory", text="Directory")
        layout.prop(self, "file_name", text="File Name")
        
        # File Format
        layout.label(text="File Format Settings:")
        layout.prop(self, "file_format", text="Format")
        
        # Video Codec (only if the file format is FFMPEG)
        if self.file_format == 'FFMPEG':
            layout.prop(self, "video_codec", text="Video Codec")
            layout.prop(self, "container_format", text="Container")
        
        # Resolution Settings
        layout.label(text="Resolution Settings:")
        col = layout.column(align=True)
        split = layout.split(factor=0.5)  # Adjust factor for wider layout
        col1 = split.column()
        col1.prop(self, "resolution_x", text="Resolution X")
        col2 = split.column()
        col2.prop(self, "resolution_y", text="Resolution Y")
        col.prop(self, "resolution_scale", text="Resolution Scale (%)")
        
        # Frame Range
        layout.label(text="Frame Range:")
        col = layout.column(align=True)
        col.prop(self, "start_frame", text="Start Frame")
        col.prop(self, "end_frame", text="End Frame")
        
        # Add a separator for better visual spacing
        layout.separator()

    def execute (self, context):
        # Save current render settings
        render = context.scene.render
        original_filepath = render.filepath
        original_resolution_x = render.resolution_x
        original_resolution_y = render.resolution_y
        original_resolution_percentage = render.resolution_percentage
        original_file_format = render.image_settings.file_format
        #original_codec = render.image_settings.codec
        
        # Set resolution scale
        render.resolution_x = self.resolution_x
        render.resolution_y = self.resolution_y
        render.resolution_percentage = self.resolution_scale

        # Determine file extension based on selected file format
        if self.file_format == 'FFMPEG':
            file_extension = ".mp4"
            render.image_settings.file_format = 'FFMPEG'
            render.ffmpeg.format = self.container_format  # Set the container format
            render.ffmpeg.codec = self.video_codec
        elif self.file_format == 'PNG':
            file_extension = "_#####.png"  # Blender uses frame numbering for image sequences
            render.image_settings.file_format = 'PNG' # Set file format to PNG for image sequence

        # Set output path and file format
        base_filename = self.file_name + file_extension
        # Ensure the output directory is used
        render.filepath = os.path.join(os.path.dirname(original_filepath), base_filename)
        output_path = os.path.join(self.output_directory, base_filename)
        render.filepath = output_path

        # Set frame range
        context.scene.frame_start = self.start_frame
        context.scene.frame_end = self.end_frame

        bpy.ops.render.opengl(animation=True, sequencer=False)

        # Restore render settings
        render.filepath = original_filepath
        render.resolution_x = original_resolution_x
        render.resolution_y = original_resolution_y
        render.resolution_percentage = original_resolution_percentage
        render.image_settings.file_format = original_file_format

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

class OUTPUT_PT_Playblast_Panel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "output"
    bl_label = "Playblast"

    def draw(self, context):
        layout = self.layout
        layout.scale_y = 2.5
        layout.operator("view3d.playblast_operator", text="Export Playblast")

def register():
    bpy.utils.register_class(VIEW3D_OT_playblast_operator)
    bpy.utils.register_class(OUTPUT_PT_Playblast_Panel)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_playblast_operator)
    bpy.utils.unregister_class(OUTPUT_PT_Playblast_Panel)

if __name__ == "__main__":
    register()

    # To call the operator
    bpy.ops.view3d.playblast_operator('INVOKE_DEFAULT')