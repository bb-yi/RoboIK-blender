# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import bpy
import numpy as np
import sys
import subprocess
from mathutils import Vector
import time

bl_info = {
    "name": "RoboIK",
    "author": "SFY",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}
# ----------------------------插件配置面板-------------------------------


class RoboIKToolPrefs(bpy.types.AddonPreferences):

    bl_idname = __name__

    # 定义插件可自定义的属性
    is_install = False

    try:
        # import PIL
        from ikpy.chain import Chain
        from ikpy.link import OriginLink, URDFLink

        is_install = True
    #        print("is_install")

    except:
        is_install = False

    # 绘制插件配置UI面板
    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.scale_y = 2
        col.enabled = not self.is_install
        col.label(text="您还未安装插件依赖：IKPY")
        col.operator(InstallIKPYOperator.bl_idname, icon="IMPORT")

        col = layout.column()
        col.scale_y = 2
        col.enabled = self.is_install
        col.label(text="不再使用并且要卸载IKPY ？")
        col.operator(UnInstallIKPYOperator.bl_idname, icon="EXPORT")


# ----------------------------安装工具-------------------------------


# 定义安装 IKPY 的操作符类
class InstallIKPYOperator(bpy.types.Operator):
    """
    操作员在Blender的Python环境中安装IKPY
    """

    bl_idname = "addon.install_ikpy"
    bl_label = "安装 IKPY库（需要网络）"

    def execute(self, context):
        # 获取Blender自带Python解释器的路径
        blender_python_path = sys.executable
        try:
            # 构建用于安装Pyaudio的pip命令
            install_command = [blender_python_path, "-m", "pip", "install", "ikpy"]
            # 执行命令，捕获输出和错误信息
            process = subprocess.Popen(install_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                self.report({"INFO"}, "IKPY安装成功！")
                RoboIKToolPrefs.is_install = True
            else:
                error_message = stderr.decode("utf-8") if stderr else "Unknown error"
                self.report({"ERROR"}, f"缺少IKPY。请在插件面板上安装 IKPY。")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"安装过程中出错: {str(e)}")
            return {"CANCELLED"}


# 定义卸载 IKPY 的操作符类
class UnInstallIKPYOperator(bpy.types.Operator):
    """
    操作员从Blender的Python环境中卸载IKPY
    """

    bl_idname = "addon.uninstall_ikpy"
    bl_label = "卸载 IKPY"

    def execute(self, context):
        try:
            import ikpy

        except:
            self.report({"ERROR"}, f"未安装 IKPY。")
            return {"CANCELLED"}
        # 获取Blender自带Python解释器的路径
        blender_python_path = sys.executable
        try:
            # 构建用于卸载IKPY的pip命令
            uninstall_command = [blender_python_path, "-m", "pip", "uninstall", "ikpy", "-y"]
            # 执行命令，捕获输出和错误信息
            process = subprocess.Popen(uninstall_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                self.report({"INFO"}, "IKPY 卸载成功！")
                RoboIKToolPrefs.is_install = False
            else:
                error_message = stderr.decode("utf-8") if stderr else "Unknown error"
                self.report({"ERROR"}, f"卸载 IKPY 失败。错误: {error_message}")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"卸载过程中出错: {str(e)}")

            return {"CANCELLED"}


# Define the operator class for the button
class TestOperator(bpy.types.Operator):
    """Roboik Operator"""

    bl_idname = "view3d.test_operator"  # Unique identifier for buttons and menus
    bl_label = "test"  # Display name in the interface

    def execute(self, context):
        # Your code here to perform the IK calculation with restrictions
        chain_collection = context.scene.roboik_properties.chain_item_collection
        collection_active_index = context.scene.roboik_properties.chain_item_collection_active_index
        bone_collection_active_index = context.scene.roboik_properties.chain_bone_item_collection_active_index
        val = chain_collection[collection_active_index].armature
        print(val)
        # self.report({"INFO"}, str(val))
        return {"FINISHED"}


class OpenAddonPreferencesOperator(bpy.types.Operator):
    """打开插件的安装配置界面"""

    bl_idname = "addon.open_preferences"
    bl_label = "打开插件配置界面"

    def execute(self, context):
        # 通过 bpy.ops.preferences.addon_show 打开插件的安装配置界面
        bpy.ops.preferences.addon_show(module=__name__)
        return {"FINISHED"}


# Define the panel class
class Roboik_PT_MainPanel(bpy.types.Panel):
    """Creates a Panel in the 3D Viewport"""

    bl_label = "RoboIK"
    bl_idname = "ROBOIK_PT_MainPanel"
    bl_space_type = "VIEW_3D"  # Specify the space type as 'VIEW_3D'
    bl_region_type = "UI"  # Specify the region type as 'UI'
    bl_category = "RoboIK"  # Specify the category, can be any string

    def draw(self, context):
        layout = self.layout
        # Create a row in the panel
        if not RoboIKToolPrefs.is_install:
            row = layout.row()
            row.alert = not RoboIKToolPrefs.is_install
            row.operator("addon.open_preferences", text="未安装IKPY库,打开配置面板安装", icon="ERROR")
        # row.operator("view3d.test_operator", text="Test Operator", icon="ITALIC")
        # row2 = layout.row()
        # row2.prop(context.scene.roboik_properties, "test", text="Test Property")
        # 显示列表


class CHAIN_PT_SubPanel(bpy.types.Panel):
    bl_label = "链集合"  # 子面板的标题
    bl_idname = "CHAIN_PT_SubPanel"  # 子面板的唯一标识符
    bl_space_type = "VIEW_3D"  # 与主面板保持一致
    bl_region_type = "UI"  # 与主面板保持一致
    bl_category = "RoboIK"  # 与主面板保持一致
    bl_parent_id = "ROBOIK_PT_MainPanel"  # 父面板的 ID，关联到主面板

    @classmethod
    def poll(cls, context):
        bool1 = RoboIKToolPrefs.is_install
        return bool1

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row()
        row.template_list(
            "CHAIN_UL_List", "chain_list", scene.roboik_properties, "chain_item_collection", scene.roboik_properties, "chain_item_collection_active_index"
        )  # 列表类型，Blender 内置类型  # 列表 ID，可以留空  # 数据对象  # 数据集合属性名称  # 活动数据对象  # 活动索引属性名称
        Col = row.column(align=True)
        Col.operator("chain_collection.add_item", icon="ADD", text="")
        Col.operator("chain_collection.remove_item", icon="REMOVE", text="")
        Col.separator()
        Col.operator("chain_collection.move_item_up", icon="TRIA_UP", text="")
        Col.operator("chain_collection.move_item_down", icon="TRIA_DOWN", text="")


class CHAIN_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # item是列表中的每一项，这里我们假设item有两个属性：index和data_string
        row = layout.row(align=True)
        row.alignment = "LEFT".upper()
        row.label(text=f"{index}")
        row.prop(item, "enabled", text="", emboss=False, icon="HIDE_OFF" if item.enabled else "HIDE_ON")
        row2 = row.row(align=True)
        row2.prop(item, "name", text="", emboss=False)
        row2.prop(item, "armature", text="骨架", emboss=True)
        row2.prop(item, "target_object", text="目标", emboss=True)
        row2.prop(item, "orientation_mode", text="旋转约束", emboss=True)


class AddChainItem(bpy.types.Operator):
    bl_idname = "chain_collection.add_item"
    bl_label = "Add Item"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        collection = context.scene.roboik_properties.chain_item_collection
        active_index = context.scene.roboik_properties.chain_item_collection_active_index
        item = collection.add()
        item.name = f"Chain {len(collection)-1}"
        item.value = len(collection)
        context.scene.roboik_properties.chain_item_collection_active_index = min(len(collection) - 1, active_index + 1)
        return {"FINISHED"}


class RemoveChainItem(bpy.types.Operator):
    bl_idname = "chain_collection.remove_item"
    bl_label = "Remove Item"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        collection = context.scene.roboik_properties.chain_item_collection
        active_index = context.scene.roboik_properties.chain_item_collection_active_index
        if collection:
            collection.remove(active_index)
            context.scene.roboik_properties.chain_item_collection_active_index = max(0, active_index - 1)
        return {"FINISHED"}


class MoveChainItemUp(bpy.types.Operator):
    bl_idname = "chain_collection.move_item_up"
    bl_label = "Move Item Up"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        collection = context.scene.roboik_properties.chain_item_collection
        active_index = context.scene.roboik_properties.chain_item_collection_active_index

        # 如果当前项不是第一个项，则上移
        if active_index > 0:
            collection.move(active_index, active_index - 1)
            context.scene.roboik_properties.chain_item_collection_active_index = active_index - 1

        return {"FINISHED"}


class MoveChainItemDown(bpy.types.Operator):
    bl_idname = "chain_collection.move_item_down"
    bl_label = "Move Item Down"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        collection = context.scene.roboik_properties.chain_item_collection
        active_index = context.scene.roboik_properties.chain_item_collection_active_index

        # 如果当前项不是最后一项，则下移
        if active_index < len(collection) - 1:
            collection.move(active_index, active_index + 1)
            context.scene.roboik_properties.chain_item_collection_active_index = active_index + 1

        return {"FINISHED"}


def update_bone_list(self, context):
    # 获取当前的 ChainBoneItem 对象
    chain_bone_item = self

    # 获取该 ChainBoneItem 所在的 ChainItem
    chain_item = context.scene.roboik_properties.chain_item_collection.get(self.id_data.name)

    if chain_item and chain_item.armature:  # 确保 armature 存在
        arma = chain_item.armature
        # 获取 armature 中所有骨骼的名称，并返回作为 EnumProperty 的项
        return [(bone.name, bone.name, "") for bone in arma.data.bones]
    else:
        return []


class ChainBoneItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Item Name")
    value: bpy.props.IntProperty(name="Value")
    # bone_name: bpy.props.EnumProperty(name="", items=update_bone_list, description="Select a bone from the armature")
    rot_axis: bpy.props.EnumProperty(name="旋转轴", items=[("X", "X", ""), ("Y", "Y", ""), ("Z", "Z", "")], default="Z")
    bone_name: bpy.props.StringProperty(name="Bone Name", default="")


class ChainItem(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    name: bpy.props.StringProperty(name="Item Name")
    value: bpy.props.IntProperty(name="Value")
    armature: bpy.props.PointerProperty(name="Armature", type=bpy.types.Armature, description="IK物体的骨架")
    chain_bone_item_collection: bpy.props.CollectionProperty(type=ChainBoneItem)
    target_object: bpy.props.PointerProperty(name="Target Object", type=bpy.types.Object, description="IK目标物体")
    orientation_mode: bpy.props.EnumProperty(
        name="Orientation Mode",
        items=[("None", "None", ""), ("orientation_axis", "单轴", ""), ("all", "all", "")],
        default="None",
        description="末端旋转对齐模式",
    )

    # 指向骨架对象的属性


# 定义旋转轴与单位向量的映射
axis_mapping = {
    0: [1, 0, 0],
    1: [0, 1, 0],
    2: [0, 0, 1],
}  # X轴  # Y轴  # Z轴
rot_axis_map = {"X": 0, "Y": 1, "Z": 2}


class BoneData:
    def __init__(self, bone, name, location, rotation_euler, rot_axis, Local_matrix, Global_matrix):
        self.bone = bone
        self.name = name
        self.location = location
        self.rotation_euler = rotation_euler
        self.rot_axis = rot_axis
        self.Local_matrix = Local_matrix
        self.Global_matrix = Global_matrix


def get_A2B_matrix(bone_A, bone_B):
    bone_A_matrix = bone_A.matrix
    bone_B_matrix = bone_B.matrix
    A2B_matrix = bone_A_matrix.inverted() @ bone_B_matrix
    # print(bone_A_matrix, "\n", bone_B_matrix)
    return A2B_matrix


def get_bone_data_list(bone_list, rot_axis_list):
    bone_data_list = []
    for i in range(len(bone_list)):
        bone = bone_list[i]
        if i == 0:
            matrix = bone.matrix
            blender_bone_obj = BoneData(bone, bone.name, matrix.translation, matrix.to_euler(), rot_axis_list[i], matrix, matrix)
        else:
            matrix = get_A2B_matrix(bone_list[i - 1], bone)
            blender_bone_obj = BoneData(bone, bone.name, matrix.translation, matrix.to_euler(), rot_axis_list[i], bone.matrix, matrix)
        bone_data_list.append(blender_bone_obj)
    return bone_data_list


def creat_ik_chain(bone_data_list):
    chain = Chain(name="chain", links=[OriginLink()])

    for i in range(len(bone_data_list)):
        bone_data = bone_data_list[i]
        urdf_link = URDFLink(
            name=bone_data.name,
            origin_translation=bone_data.location,
            origin_orientation=bone_data.rotation_euler,
            rotation=axis_mapping[bone_data.rot_axis],
        )
        chain.links.append(urdf_link)
    urdf_end_link = URDFLink(
        name="end_link",
        origin_translation=[0, bone_data_list[-1].bone.length, 0],
        origin_orientation=[0, 0, 0],
        rotation=[0, 1, 0],
    )
    chain.links.append(urdf_end_link)
    return chain


def set_bone_angle_to_zero(bone_list):
    for i in range(len(bone_list)):
        bone_list[i].rotation_euler = [0, 0, 0]


def set_bone_angle(bone_list, angle_list, rot_axis_list):
    for i in range(len(bone_list)):
        bone_data = bone_list[i]
        bone_data.rotation_euler[rot_axis_list[i]] = angle_list[i]


def set_bone_rotation_mode(bone_list):
    for i in range(len(bone_list)):
        bone_list[i].rotation_mode = "XYZ"


def print_chain_info(chain):
    # 打印每个关节的信息
    for link in chain.links:
        # 检查 link 类型，跳过 OriginLink，因为它没有相关的字段
        if isinstance(link, URDFLink):
            print(f"Name: {link.name}")
            print(f"Origin Translation: {link.origin_translation}")
            print(f"Origin Orientation: {link.origin_orientation}")
            print(f"Rotation: {link.rotation}")
            print("=" * 30)


chain_list = []
chain_bone_list = []
chain_bone_axis_list = []


class UPDATE_ChainIK_OT_RoboIK(bpy.types.Operator):
    bl_idname = "update_chain_ik.roboik"
    bl_label = "Update Chain IK"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        global chain_list
        global chain_bone_list
        global chain_bone_axis_list
        bpy.ops.depsgraph_post_handler.remove()
        bpy.ops.frame_change_pre_handler.remove()
        armature_has_none = False
        target_has_none = False
        for i in range(len(context.scene.roboik_properties.chain_item_collection)):
            if context.scene.roboik_properties.chain_item_collection[i].enabled:
                if context.scene.roboik_properties.chain_item_collection[i].armature is None:
                    armature_has_none = True
                    break
                if context.scene.roboik_properties.chain_item_collection[i].target_object is None:
                    target_has_none = True
                    break
        if target_has_none:
            self.report({"ERROR"}, "有目标为空,请选择目标")
            return {"FINISHED"}
        if armature_has_none:
            self.report({"ERROR"}, "有骨架为空,请选择骨架")
            return {"FINISHED"}
        bone_has_none = False
        bone_has_repeat = False
        bone_has_none2 = False
        for i in range(len(context.scene.roboik_properties.chain_item_collection)):
            if context.scene.roboik_properties.chain_item_collection[i].enabled:
                bone_name_list = []
                for j in range(len(context.scene.roboik_properties.chain_item_collection[i].chain_bone_item_collection)):
                    print(context.scene.roboik_properties.chain_item_collection[i].chain_bone_item_collection[j].bone_name)
                    if context.scene.roboik_properties.chain_item_collection[i].chain_bone_item_collection[j].bone_name == "":
                        bone_has_none2 = True
                    bone_name_list.append(context.scene.roboik_properties.chain_item_collection[i].chain_bone_item_collection[j].bone_name)
                print(bone_name_list, i)
                if len(bone_name_list) == 0:
                    bone_has_none = True
                    break
                bone_has_repeat = len(bone_name_list) != len(set(bone_name_list))
                if bone_has_repeat:
                    break
        if bone_has_none:
            self.report({"ERROR"}, "有链条为空,请选择骨骼")
            return {"FINISHED"}
        if bone_has_none2:
            self.report({"ERROR"}, "有空骨骼,请选择骨骼")
            return {"FINISHED"}
        if bone_has_repeat:
            self.report({"ERROR"}, "有重复的骨骼")
            return {"FINISHED"}
        chain_list.clear()
        chain_bone_list.clear()
        chain_bone_axis_list.clear()
        for i in range(len(context.scene.roboik_properties.chain_item_collection)):
            if context.scene.roboik_properties.chain_item_collection[i].enabled:
                print(context.scene.roboik_properties.chain_item_collection[i].enabled)
                bone_list = []
                rot_axis_list = []
                bone_angle_list = []
                active_links_mask = [0]
                bone_collection = context.scene.roboik_properties.chain_item_collection[i]
                armature_obj = bpy.data.objects[bone_collection.armature.name]
                for j in range(len(bone_collection.chain_bone_item_collection)):
                    bone_name = bone_collection.chain_bone_item_collection[j].bone_name
                    bone_list.append(armature_obj.pose.bones[bone_name])
                    rot_axis_list.append(rot_axis_map.get(bone_collection.chain_bone_item_collection[j].rot_axis))
                    bone_angle_list.append(0)
                    active_links_mask.append(1)
                active_links_mask.append(0)
                set_bone_rotation_mode(bone_list)
                set_bone_angle_to_zero(bone_list)
                set_bone_angle(bone_list, bone_angle_list, rot_axis_list)
                bone_data_list = get_bone_data_list(bone_list, rot_axis_list)
                chain = creat_ik_chain(bone_data_list)
                chain.active_links_mask = active_links_mask
                chain_list.append(chain)
                chain_bone_list.append(bone_list)
                chain_bone_axis_list.append(rot_axis_list)
            # print_chain_info(chain)

        self.report({"INFO"}, "已更新IK数据")
        return {"FINISHED"}


def loop():
    # print(chain_list)
    chain_collection = bpy.context.scene.roboik_properties.chain_item_collection
    offset = 0
    start_time = time.time()

    for i in range(len(chain_collection)):
        if chain_collection[i].enabled:
            chain = chain_list[i - offset]
            target_obj = chain_collection[i].target_object
            armature_obj = bpy.data.objects[chain_collection[i].armature.name]
            target_position = armature_obj.matrix_world.inverted() @ target_obj.location
            if chain_collection[i].orientation_mode == "None":
                target_angle = chain.inverse_kinematics(target_position=target_position)
            elif chain_collection[i].orientation_mode == "orientation_axis":
                target_axis = target_obj.matrix_world.to_3x3() @ Vector((0, 1, 0))
                target_angle = chain.inverse_kinematics(target_position=target_position, target_orientation=target_axis, orientation_mode="Y")
            elif chain_collection[i].orientation_mode == "all":
                target_orientation = target_obj.matrix_world.to_3x3()
                target_angle = chain.inverse_kinematics(target_position=target_position, target_orientation=target_orientation, orientation_mode="all")
            target_angle = target_angle[1:-1]
            if i == bpy.context.scene.roboik_properties.chain_item_collection_active_index:
                bpy.context.scene.roboik_properties.IK_angle_output = str([round(np.degrees(angle), 2) for angle in target_angle])
            # print("目标角度：", [np.degrees(angle) for angle in target_angle])
            set_bone_angle(chain_bone_list[i - offset], target_angle, chain_bone_axis_list[i - offset])
        else:
            offset += 1
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000
    bpy.context.scene.roboik_properties.elapsed_time = elapsed_time


# 定义一个处理函数
def update(scene):
    # print("222")
    loop()
    pass


# bpy.app.handlers.frame_change_pre.clear()
# bpy.app.handlers.depsgraph_update_pre.clear()
# bpy.app.handlers.depsgraph_update_post.clear()


class Update_depsgraph_post_handler(bpy.types.Operator):
    bl_idname = "depsgraph_post_handler.update"
    bl_label = "update depsgraph_update_post_handler"

    def execute(self, context):
        # bpy.app.handlers.depsgraph_update_post.clear()

        handler_list = []
        print(chain_list)
        for handler in bpy.app.handlers.depsgraph_update_post:
            if handler.__name__ == update.__name__:
                handler_list.append(handler)
        for handler in handler_list:
            bpy.app.handlers.depsgraph_update_post.remove(handler)
        bpy.app.handlers.depsgraph_update_post.append(update)
        self.report({"INFO"}, "已添加实时更新")
        return {"FINISHED"}


class Remove_depsgraph_post_handler(bpy.types.Operator):
    bl_idname = "depsgraph_post_handler.remove"
    bl_label = "remove depsgraph_update_post_handler"

    def execute(self, context):
        print(chain_list)
        handler_list = []
        for handler in bpy.app.handlers.depsgraph_update_post:
            if handler.__name__ == update.__name__:
                handler_list.append(handler)
        for handler in handler_list:
            bpy.app.handlers.depsgraph_update_post.remove(handler)
        for i in range(len(chain_list)):
            bone_list = chain_bone_list[i]
            print(bone_list)
            set_bone_angle_to_zero(bone_list)
        self.report({"INFO"}, "已移除实时更新")
        return {"FINISHED"}


class Update_frame_change_pre_handler(bpy.types.Operator):
    bl_idname = "frame_change_pre_handler.update"
    bl_label = "update frame_change_pre_handler"

    def execute(self, context):
        # bpy.app.handlers.frame_change_pre.clear()

        handler_list = []
        for handler in bpy.app.handlers.frame_change_pre:
            if handler.__name__ == update.__name__:
                handler_list.append(handler)
        for handler in handler_list:
            bpy.app.handlers.frame_change_pre.remove(handler)
        bpy.app.handlers.frame_change_pre.append(update)
        self.report({"INFO"}, "已添加帧更新")
        return {"FINISHED"}


class Remove_frame_change_pre_handler(bpy.types.Operator):
    bl_idname = "frame_change_pre_handler.remove"
    bl_label = "remove frame_change_pre_handler"

    def execute(self, context):
        handler_list = []
        for handler in bpy.app.handlers.frame_change_pre:
            if handler.__name__ == update.__name__:
                handler_list.append(handler)
        for handler in handler_list:
            bpy.app.handlers.frame_change_pre.remove(handler)
        self.report({"INFO"}, "已移除帧更新")
        return {"FINISHED"}


class CHAIN_BONE_PT_SubPanel(bpy.types.Panel):
    bl_label = "链骨骼"  # 子面板的标题
    bl_idname = "CHAIN_BONE_PT_SubPanel"  # 子面板的唯一标识符
    bl_space_type = "VIEW_3D"  # 与主面板保持一致
    bl_region_type = "UI"  # 与主面板保持一致
    bl_category = "RoboIK"  # 与主面板保持一致
    bl_parent_id = "ROBOIK_PT_MainPanel"  # 父面板的 ID，关联到主面板

    @classmethod
    def poll(cls, context):
        collection = context.scene.roboik_properties.chain_item_collection
        bool1 = collection is not None and len(collection) > 0
        bool2 = True
        if not bool1:
            return bool1
        if collection[context.scene.roboik_properties.chain_item_collection_active_index].armature == None:
            bool2 = False
        # 控制显示条件，例如仅当有选中对象时显示
        return bool1 and bool2

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        chain_collection = scene.roboik_properties.chain_item_collection
        collection_active_index = scene.roboik_properties.chain_item_collection_active_index
        row = layout.row()
        row.template_list(
            "CHAIN_BONE_UL_List",
            "roboik_list",
            chain_collection[collection_active_index],
            "chain_bone_item_collection",
            scene.roboik_properties,
            "chain_bone_item_collection_active_index",
        )  # 列表类型，Blender 内置类型  # 列表 ID，可以留空  # 数据对象  # 数据集合属性名称  # 活动数据对象  # 活动索引属性名称
        Col = row.column(align=True)
        Col.operator("chain_bone_collection.add_item", icon="ADD", text="")
        Col.operator("chain_bone_collection.remove_item", icon="REMOVE", text="")
        Col.separator()
        Col.operator("bone_collection.move_item_up", icon="TRIA_UP", text="")
        Col.operator("bone_collection.move_item_down", icon="TRIA_DOWN", text="")
        Col.separator()
        Col.operator("bone_collection.clear_all_item", icon="TRASH", text="")
        row1 = layout.row(align=True)
        row1_1 = row1.row(align=True)
        row1_1.scale_x = 2
        row1_1_1 = row1_1.row(align=True)
        row1_1_1.scale_x = 0.5
        row1_1_1.label(text="角度输出")
        row1_1.prop(scene.roboik_properties, "IK_angle_output", text="", emboss=False)
        row1_2 = row1.row(align=True)
        row1_2.alignment = "RIGHT".upper()
        row1_2.prop(scene.roboik_properties, "elapsed_time", text="计算时间", emboss=False)
        row1_2.label(text="ms")
        row2 = layout.row()
        row2.operator("update_chain_ik.roboik", text="更新IK链数据", icon="CON_SPLINEIK", emboss=True)
        row3 = layout.row()
        row3_1 = row3.row(align=True)
        row3_1.scale_x = 1.5
        row3_1.operator("depsgraph_post_handler.update", text="实时更新", icon="FILE_REFRESH")
        row3_1.operator("depsgraph_post_handler.remove", text="", icon="TRASH")
        row3_2 = row3.row(align=True)
        row3_2.scale_x = 1.5
        row3_2.operator("frame_change_pre_handler.update", text="帧更新时更新", icon="FILE_REFRESH")
        row3_2.operator("frame_change_pre_handler.remove", text="", icon="TRASH")


class CHAIN_BONE_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # item是列表中的每一项，这里我们假设item有两个属性：index和data_string
        row = layout.row(align=True)
        row.alignment = "LEFT".upper()
        row.label(text=f"{index}")
        row2 = row.row(align=True)
        row2.prop(item, "name", text="", emboss=False)
        row2.prop(item, "rot_axis", text="旋转轴", emboss=True)
        # row2.prop_search(item, "bone_name", context.scene.roboik_properties.chain_item_collection[context.scene.roboik_properties.chain_item_collection_active_index].armature, "bones", text="", icon="BONE_DATA")

        chain_item_collection = context.scene.roboik_properties.chain_item_collection
        collection_active_index = context.scene.roboik_properties.chain_item_collection_active_index
        chain_item = chain_item_collection[collection_active_index]

        # 确保 armature 有效
        if chain_item and chain_item.armature:
            # 使用 prop_search 显示 armature 中的骨骼列表
            row2.prop_search(item, "bone_name", chain_item.armature, "bones", text="", icon="BONE_DATA")
        else:
            row2.label(text="No Armature Assigned", icon="ERROR")

        # row2.prop(item, "bone_name", text="", emboss=True, icon="BONE_DATA")


class AddChainBoneItem(bpy.types.Operator):
    bl_idname = "chain_bone_collection.add_item"
    bl_label = "Add Item"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        scene = context.scene
        chain_collection = scene.roboik_properties.chain_item_collection
        collection_active_index = scene.roboik_properties.chain_item_collection_active_index
        collection = chain_collection[collection_active_index].chain_bone_item_collection
        active_index = context.scene.roboik_properties.chain_bone_item_collection_active_index
        item = collection.add()
        item.name = f"bone {len(collection)-1}"
        item.value = len(collection)
        # item.bone_name = "bone"
        context.scene.roboik_properties.chain_bone_item_collection_active_index = min(len(collection) - 1, active_index + 1)
        active_index = context.scene.roboik_properties.chain_bone_item_collection_active_index
        if active_index > 0:
            armature = chain_collection[collection_active_index].armature
            if collection[active_index - 1].bone_name != "":
                pre_bone = armature.bones[collection[active_index - 1].bone_name]
                if pre_bone.children:
                    item.bone_name = pre_bone.children[0].name
                else:
                    item.bone_name = pre_bone.name
        return {"FINISHED"}


class RemoveChainBoneItem(bpy.types.Operator):
    bl_idname = "chain_bone_collection.remove_item"
    bl_label = "Remove Item"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        scene = context.scene
        chain_collection = scene.roboik_properties.chain_item_collection
        collection_active_index = scene.roboik_properties.chain_item_collection_active_index
        collection = chain_collection[collection_active_index].chain_bone_item_collection
        active_index = context.scene.roboik_properties.chain_bone_item_collection_active_index
        if collection:
            collection.remove(active_index)
            context.scene.roboik_properties.chain_bone_item_collection_active_index = max(0, active_index - 1)
        return {"FINISHED"}


class MoveBoneItemUp(bpy.types.Operator):
    bl_idname = "bone_collection.move_item_up"
    bl_label = "Move Item Up"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        collection = context.scene.roboik_properties.chain_item_collection
        active_index = context.scene.roboik_properties.chain_item_collection_active_index
        bone_collection = collection[active_index].chain_bone_item_collection
        bone_collection_active_index = context.scene.roboik_properties.chain_bone_item_collection_active_index
        # 如果当前项不是第一个项，则上移
        if bone_collection_active_index > 0:
            bone_collection.move(bone_collection_active_index, bone_collection_active_index - 1)
            context.scene.roboik_properties.chain_bone_item_collection_active_index = bone_collection_active_index - 1

        return {"FINISHED"}


class MoveBoneItemDown(bpy.types.Operator):
    bl_idname = "bone_collection.move_item_down"
    bl_label = "Move Item Down"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        collection = context.scene.roboik_properties.chain_item_collection
        active_index = context.scene.roboik_properties.chain_item_collection_active_index
        bone_collection = collection[active_index].chain_bone_item_collection
        bone_collection_active_index = context.scene.roboik_properties.chain_bone_item_collection_active_index
        # 如果当前项不是最后一项，则下移
        if bone_collection_active_index < len(bone_collection_active_index) - 1:
            bone_collection.move(bone_collection_active_index, bone_collection_active_index + 1)
            context.scene.roboik_properties.chain_bone_item_collection_active_index = bone_collection_active_index + 1

        return {"FINISHED"}


class ClearAllBoneItem(bpy.types.Operator):
    bl_idname = "bone_collection.clear_all_item"
    bl_label = "Clear All Item"
    bl_options = {"REGISTER", "UNDO"}  # 启用注册和撤销功能

    def execute(self, context):
        collection = context.scene.roboik_properties.chain_item_collection
        active_index = context.scene.roboik_properties.chain_item_collection_active_index
        bone_collection = collection[active_index].chain_bone_item_collection
        bone_collection.clear()
        self.report({"INFO"}, "已清空所有骨骼项")
        return {"FINISHED"}


class RoboikProperties(bpy.types.PropertyGroup):
    test: bpy.props.FloatProperty(name="Test Property", default=1.0)
    chain_item_collection: bpy.props.CollectionProperty(type=ChainItem)
    chain_item_collection_active_index: bpy.props.IntProperty(name="Active Index", default=0)
    chain_bone_item_collection_active_index: bpy.props.IntProperty(name="Active Index", default=0)
    IK_angle_output: bpy.props.StringProperty(name="IK angle output", default="None")
    elapsed_time: bpy.props.FloatProperty(name="Elapsed Time", default=0.0)


OperatorList = [
    TestOperator,
    AddChainItem,
    RemoveChainItem,
    MoveChainItemUp,
    MoveChainItemDown,
    AddChainBoneItem,
    RemoveChainBoneItem,
    MoveBoneItemUp,
    MoveBoneItemDown,
    ClearAllBoneItem,
    UPDATE_ChainIK_OT_RoboIK,
    Update_depsgraph_post_handler,
    Remove_depsgraph_post_handler,
    Update_frame_change_pre_handler,
    Remove_frame_change_pre_handler,
    InstallIKPYOperator,
    UnInstallIKPYOperator,
    OpenAddonPreferencesOperator,
]


PanelList = [
    Roboik_PT_MainPanel,
    CHAIN_PT_SubPanel,
    CHAIN_BONE_PT_SubPanel,
    CHAIN_UL_List,
    CHAIN_BONE_UL_List,
    RoboIKToolPrefs,
]
propertyList = [
    ChainBoneItem,
    ChainItem,
    RoboikProperties,
]


# Register the operator and panel
def register():
    for operator in OperatorList:
        bpy.utils.register_class(operator)
    for panel in PanelList:
        bpy.utils.register_class(panel)
    for property in propertyList:
        bpy.utils.register_class(property)
    bpy.types.Scene.roboik_properties = bpy.props.PointerProperty(type=RoboikProperties)


# Unregister the operator and panel
def unregister():
    for operator in OperatorList:
        bpy.utils.unregister_class(operator)
    for panel in PanelList:
        bpy.utils.unregister_class(panel)
    for property in propertyList:
        bpy.utils.unregister_class(property)
    del bpy.types.Scene.roboik_properties


# Register the plugin
if __name__ == "__main__":
    register()
