import threading
import time
import pyMeow as overlay
import keyboard
import struct
from typing import Iterator, Optional, Dict

from pynput.keyboard import Listener as KeyboardListener
from classes.config_manager import ConfigManager, Colors, COLOR_CHOICES
from classes.memory_manager import MemoryManager
from classes.logger import Logger
from classes.utility import Utility

# Initialize the logger for consistent logging
logger = Logger.get_logger()
# Define the main loop sleep time for reduced CPU usage
MAIN_LOOP_SLEEP = 0.05
# Number of entities to iterate over
ENTITY_COUNT = 64
# Size of each entity entry in memory
ENTITY_ENTRY_SIZE = 120

SKELETON_BONES = {
    6: [5],
    5: [4],
    4: [3, 8, 11],
    3: [0],
    8: [9],
    9: [10],
    11: [12],
    12: [13],
    0: [22, 25],
    22: [23],
    23: [24],
    25: [26],
    26: [27],
}
ALL_BONE_IDS = set(SKELETON_BONES.keys())
for _bones in SKELETON_BONES.values():
    ALL_BONE_IDS.update(_bones)
MAX_BONE_ID = max(ALL_BONE_IDS) if ALL_BONE_IDS else 0

class Entity:
    """Represents a game entity with cached data for efficient access."""
    def __init__(self, controller_ptr: int, pawn_ptr: int, memory_manager: MemoryManager) -> None:
        self.controller_ptr = controller_ptr
        self.pawn_ptr = pawn_ptr
        self.memory_manager = memory_manager
        self.pos2d: Optional[Dict[str, float]] = None
        self.head_pos2d: Optional[Dict[str, float]] = None
        self._cached_data = None
        self._last_update = 0
        self._cached_bones = None
        self._last_bone_update = 0

    def _update_cache(self) -> None:
        """Update cached data with a time interval."""
        current_time = time.time()
        if current_time - self._last_update >= 0.1:
            try:
                self._cached_data = {
                    "name": self.memory_manager.read_string(self.controller_ptr + self.memory_manager.m_iszPlayerName),
                    "health": self.memory_manager.read_int(self.pawn_ptr + self.memory_manager.m_iHealth),
                    "team": self.memory_manager.read_int(self.pawn_ptr + self.memory_manager.m_iTeamNum),
                    "pos": self.memory_manager.read_vec3(self.pawn_ptr + self.memory_manager.m_vOldOrigin),
                    "dormant": bool(self.memory_manager.read_int(self.pawn_ptr + self.memory_manager.m_bDormant))
                }
                self._last_update = current_time
            except Exception as e:
                logger.error(f"Failed to update cache for entity: {e}")
                self._cached_data = None

    @property
    def name(self) -> str:
        """Get the entity's name, optionally transliterated."""
        self._update_cache()
        if self._cached_data and self._cached_data.get("name"):
            return Utility.transliterate(self._cached_data["name"]) if self.memory_manager.config["Overlay"]["use_transliteration"] else self._cached_data["name"]
        return ""

    @property
    def health(self) -> int:
        """Get the entity's health."""
        self._update_cache()
        return self._cached_data["health"] if self._cached_data else 0

    @property
    def team(self) -> int:
        """Get the entity's team number."""
        self._update_cache()
        return self._cached_data["team"] if self._cached_data else -1

    @property
    def pos(self) -> Dict[str, float]:
        """Get the entity's 3D position."""
        self._update_cache()
        return self._cached_data["pos"] if self._cached_data else {"x": 0.0, "y": 0.0, "z": 0.0}

    @property
    def dormant(self) -> bool:
        """Check if the entity is dormant."""
        self._update_cache()
        return self._cached_data["dormant"] if self._cached_data else True

    def bone_pos(self, bone: int) -> Dict[str, float]:
        """Get the 3D position of a specific bone."""
        if self._cached_bones and bone in self._cached_bones:
            return self._cached_bones[bone]
        try:
            game_scene = self.memory_manager.read_longlong(self.pawn_ptr + self.memory_manager.m_pGameSceneNode)
            bone_array_ptr = self.memory_manager.read_longlong(game_scene + self.memory_manager.m_pBoneArray)
            return self.memory_manager.read_vec3(bone_array_ptr + bone * 32)
        except Exception as e:
            logger.error(f"Failed to get bone position for bone {bone}: {e}")
            return {"x": 0.0, "y": 0.0, "z": 0.0}

    def all_bone_pos(self) -> Optional[Dict[int, Dict[str, float]]]:
        """Get all bone positions with caching."""
        current_time = time.time()
        if self._cached_bones and current_time - self._last_bone_update < 0.2:  # Cache for 0.2 seconds
            return self._cached_bones
        try:
            game_scene = self.memory_manager.read_longlong(self.pawn_ptr + self.memory_manager.m_pGameSceneNode)
            bone_array_ptr = self.memory_manager.read_longlong(game_scene + self.memory_manager.m_pBoneArray)
            if not bone_array_ptr:
                return None
            
            num_bones_to_read = MAX_BONE_ID + 1
            data = self.memory_manager.pm.read_bytes(bone_array_ptr, num_bones_to_read * 32)
            
            bone_positions = {}
            for i in ALL_BONE_IDS:  # Only read relevant bones
                offset = i * 32
                x, y, z = struct.unpack_from('fff', data, offset)
                bone_positions[i] = {"x": x, "y": y, "z": z}
            self._cached_bones = bone_positions
            self._last_bone_update = current_time
            return bone_positions
        except Exception as e:
            logger.error(f"Failed to get all bone positions: {e}")
            return None

    @staticmethod
    def validate_screen_position(pos: Dict[str, float]) -> bool:
        """Validate if a screen position is within bounds."""
        screen_width = overlay.get_screen_width()
        screen_height = overlay.get_screen_height()
        return 0 <= pos["x"] <= screen_width and 0 <= pos["y"] <= screen_height

class CS2Overlay:
    """Manages the ESP overlay for Counter-Strike 2."""
    def __init__(self, memory_manager: MemoryManager) -> None:
        """
        Initialize the Overlay with a shared MemoryManager instance.
        """
        self.config = ConfigManager.load_config()
        self.memory_manager = memory_manager
        self.is_running = False
        self.stop_event = threading.Event()
        self.local_team = None
        self.screen_width = overlay.get_screen_width()
        self.screen_height = overlay.get_screen_height()
        self.load_configuration()

    def load_configuration(self) -> None:
        """Load and apply configuration settings."""
        settings = self.config['Overlay']
        self.enable_box = settings['enable_box']
        self.enable_skeleton = settings.get('enable_skeleton', True)
        self.draw_snaplines = settings['draw_snaplines']
        self.snaplines_color_hex = settings['snaplines_color_hex']
        self.box_line_thickness = settings['box_line_thickness']
        self.box_color_hex = settings['box_color_hex']
        self.text_color_hex = settings['text_color_hex']
        self.draw_health_numbers = settings['draw_health_numbers']
        self.use_transliteration = settings['use_transliteration']
        self.draw_nicknames = settings['draw_nicknames']
        self.draw_teammates = settings['draw_teammates']
        self.teammate_color_hex = settings['teammate_color_hex']
        self.enable_minimap = settings['enable_minimap']
        self.minimap_size = settings['minimap_size']
        self.target_fps = int(settings['target_fps'])
        # Default minimap position
        self.minimap_position = "top_left"  # Options: top_left, top_right, bottom_left, bottom_right
        self.minimap_positions = {
            "top_left": (10, 10),
            "top_right": (self.screen_width - self.minimap_size - 10, 10),
            "bottom_left": (10, self.screen_height - self.minimap_size - 10),
            "bottom_right": (self.screen_width - self.minimap_size - 10, self.screen_height - self.minimap_size - 10)
        }

    def update_config(self, config: dict) -> None:
        """Update the configuration settings."""
        self.config = config
        self.load_configuration()
        logger.debug("Overlay configuration updated.")

    def iterate_entities(self) -> Iterator[Entity]:
        """Iterate over game entities and yield Entity objects."""
        try:
            ent_list_ptr = self.memory_manager.read_longlong(self.memory_manager.client_dll_base + self.memory_manager.dwEntityList)
            local_controller_ptr = self.memory_manager.read_longlong(self.memory_manager.client_dll_base + self.memory_manager.dwLocalPlayerController)
        except Exception as e:
            logger.error(f"Error reading entity list or local controller pointer: {e}")
            return iter([])

        for i in range(1, ENTITY_COUNT + 1):
            try:
                list_index = (i & 0x7FFF) >> 9
                entity_index = i & 0x1FF
                entry_ptr = self.memory_manager.read_longlong(ent_list_ptr + (8 * list_index) + 16)
                if not entry_ptr:
                    continue

                controller_ptr = self.memory_manager.read_longlong(entry_ptr + ENTITY_ENTRY_SIZE * entity_index)
                if not controller_ptr or controller_ptr == local_controller_ptr:
                    continue

                controller_pawn_ptr = self.memory_manager.read_longlong(controller_ptr + self.memory_manager.m_hPlayerPawn)
                if not controller_pawn_ptr:
                    continue

                list_entry_ptr = self.memory_manager.read_longlong(ent_list_ptr + 8 * ((controller_pawn_ptr & 0x7FFF) >> 9) + 16)
                if not list_entry_ptr:
                    continue

                pawn_ptr = self.memory_manager.read_longlong(list_entry_ptr + ENTITY_ENTRY_SIZE * (controller_pawn_ptr & 0x1FF))
                if not pawn_ptr:
                    continue

                # Early validation of dormant state
                if bool(self.memory_manager.read_int(pawn_ptr + self.memory_manager.m_bDormant)):
                    continue

                yield Entity(controller_ptr, pawn_ptr, self.memory_manager)
            except Exception as e:
                logger.error(f"Error iterating entity {i}: {e}")
                continue

    def draw_skeleton(self, entity: Entity, view_matrix: list, color: tuple, all_bones_pos_3d: Dict[int, Dict[str, float]]) -> None:
        """Draw the skeleton of an entity."""
        try:
            if not all_bones_pos_3d:
                return

            bone_positions_2d = {}
            for bone_id in ALL_BONE_IDS:
                if bone_id in all_bones_pos_3d:
                    pos_3d = all_bones_pos_3d[bone_id]
                    try:
                        pos_2d = overlay.world_to_screen(view_matrix, pos_3d, 1)
                    except Exception:
                        pos_2d = None
                    
                    if pos_2d and entity.validate_screen_position(pos_2d):
                        bone_positions_2d[bone_id] = pos_2d

            for start_bone, end_bones in SKELETON_BONES.items():
                if start_bone in bone_positions_2d:
                    for end_bone in end_bones:
                        if end_bone in bone_positions_2d:
                            overlay.draw_line(
                                bone_positions_2d[start_bone]["x"],
                                bone_positions_2d[start_bone]["y"],
                                bone_positions_2d[end_bone]["x"],
                                bone_positions_2d[end_bone]["y"],
                                color,
                                1.5
                            )
        except Exception as e:
            logger.error(f"Error drawing skeleton: {e}")

    def draw_entity(self, entity: Entity, view_matrix: list, is_teammate: bool = False) -> None:
        """Render the ESP overlay for a given entity."""
        try:
            if entity.health <= 0 or entity.dormant:
                return

            # Only fetch bone positions if skeleton is enabled
            all_bones_pos_3d = entity.all_bone_pos() if self.enable_skeleton else None
            
            head_pos_3d = None
            if all_bones_pos_3d and 6 in all_bones_pos_3d:
                head_pos_3d = all_bones_pos_3d[6]
            else:
                head_pos_3d = entity.bone_pos(6)

            try:
                pos2d = overlay.world_to_screen(view_matrix, entity.pos, 1)
                head_pos2d = overlay.world_to_screen(view_matrix, head_pos_3d, 1)
            except Exception:
                pos2d, head_pos2d = None, None

            if not isinstance(pos2d, dict) or not isinstance(head_pos2d, dict) or not entity.validate_screen_position(pos2d) or not entity.validate_screen_position(head_pos2d):
                return

            entity.pos2d = pos2d
            entity.head_pos2d = head_pos2d

            head_y = entity.head_pos2d["y"]
            pos_y = entity.pos2d["y"]
            box_height = pos_y - head_y
            box_width = box_height / 2
            half_width = box_width / 2

            outline_color = overlay.get_color(self.teammate_color_hex if is_teammate else self.box_color_hex)
            text_color = overlay.get_color(self.text_color_hex)

            if self.enable_skeleton and all_bones_pos_3d:
                self.draw_skeleton(entity, view_matrix, outline_color, all_bones_pos_3d)

            if self.draw_snaplines:
                screen_width = overlay.get_screen_width()
                screen_height = overlay.get_screen_height()
                overlay.draw_line(
                    screen_width / 2,
                    screen_height / 2,
                    entity.head_pos2d["x"],
                    entity.head_pos2d["y"],
                    overlay.get_color(self.snaplines_color_hex),
                    2
                )

            if self.enable_box:
                overlay.draw_rectangle(
                    entity.head_pos2d["x"] - half_width,
                    entity.head_pos2d["y"] - half_width / 2,
                    box_width,
                    box_height + half_width / 2,
                    Colors.grey
                )
                overlay.draw_rectangle_lines(
                    entity.head_pos2d["x"] - half_width,
                    entity.head_pos2d["y"] - half_width / 2,
                    box_width,
                    box_height + half_width / 2,
                    outline_color,
                    self.box_line_thickness
                )

            if self.draw_nicknames:
                nickname = entity.name
                nickname_font_size = 11
                nickname_width = overlay.measure_text(nickname, nickname_font_size)
                overlay.draw_text(
                    nickname,
                    entity.head_pos2d["x"] - nickname_width // 2,
                    entity.head_pos2d["y"] - half_width / 2 - 15,
                    nickname_font_size,
                    text_color
                )

            bar_width = 4
            bar_margin = 2
            bar_x = entity.head_pos2d["x"] - half_width - bar_width - bar_margin
            bar_y = entity.head_pos2d["y"] - half_width / 2
            bar_height = box_height + half_width / 2
            overlay.draw_rectangle(
                bar_x,
                bar_y,
                bar_width,
                bar_height,
                overlay.get_color("black")
            )
            health_percent = max(0, min(entity.health, 100))
            fill_height = (health_percent / 100.0) * bar_height
            if health_percent <= 20:
                fill_color = overlay.get_color("red")
            elif health_percent <= 50:
                fill_color = overlay.get_color("yellow")
            else:
                fill_color = overlay.get_color("green")
            fill_y = bar_y + (bar_height - fill_height)
            overlay.draw_rectangle(
                bar_x,
                fill_y,
                bar_width,
                fill_height,
                fill_color
            )
            if self.draw_health_numbers:
                health_text = f"{entity.health}"
                overlay.draw_text(
                    health_text,
                    int(bar_x - 25),
                    int(bar_y + bar_height / 2 - 5),
                    10,
                    text_color
                )
        except Exception as e:
            logger.error(f"Error drawing entity: {e}")

    def draw_minimap(self, entities: list[Entity], view_matrix: list) -> None:
        """Render the minimap overlay."""
        if not self.enable_minimap:
            return

        map_min = {"x": -4000, "y": -4000}
        map_max = {"x": 4000, "y": 4000}
        map_size = {"x": map_max["x"] - map_min["x"], "y": map_max["y"] - map_min["y"]}

        minimap_size = self.minimap_size
        minimap_x, minimap_y = self.minimap_positions[self.minimap_position]

        overlay.draw_rectangle(minimap_x, minimap_y, minimap_size, minimap_size, Colors.grey)
        overlay.draw_rectangle_lines(minimap_x, minimap_y, minimap_size, minimap_size, Colors.black, 2)

        for entity in entities:
            if entity.health <= 0 or entity.dormant:
                continue
            pos = entity.pos
            map_x = ((pos["x"] - map_min["x"]) / map_size["x"]) * minimap_size + minimap_x
            map_y = ((map_max["y"] - pos["y"]) / map_size["y"]) * minimap_size + minimap_y
            color = Colors.cyan if entity.team == self.local_team else Colors.red
            overlay.draw_circle(map_x, map_y, 3, color)

    def start(self) -> None:
        """Start the Overlay."""
        self.is_running = True
        self.stop_event.clear()

        try:
            overlay.overlay_init("Counter-Strike 2", fps=self.target_fps)
        except Exception as e:
            logger.error(f"Overlay initialization error: {e}")
            self.is_running = False
            return

        frame_time = 1.0 / self.target_fps
        is_game_active = Utility.is_game_active
        sleep = time.sleep

        while not self.stop_event.is_set():
            try:
                # Check if game window is active
                if not is_game_active():
                    sleep(MAIN_LOOP_SLEEP)
                    continue

                start_time = time.time()
                view_matrix = self.memory_manager.read_floats(self.memory_manager.client_dll_base + self.memory_manager.dwViewMatrix, 16)

                local_controller_ptr = self.memory_manager.read_longlong(self.memory_manager.client_dll_base + self.memory_manager.dwLocalPlayerController)
                if local_controller_ptr:
                    local_pawn_handle = self.memory_manager.read_longlong(local_controller_ptr + self.memory_manager.m_hPlayerPawn)
                    local_pawn_ptr = self.memory_manager.read_longlong(self.memory_manager.client_dll_base + self.memory_manager.dwLocalPlayerPawn)
                    self.local_team = self.memory_manager.read_int(local_pawn_ptr + self.memory_manager.m_iTeamNum)

                entities = list(self.iterate_entities())

                if overlay.overlay_loop():
                    overlay.begin_drawing()
                    overlay.draw_fps(0, 0)
                    self.draw_minimap(entities, view_matrix)
                    for entity in entities:
                        if self.local_team is not None and entity.team == self.local_team and not self.draw_teammates:
                            continue
                        self.draw_entity(entity, view_matrix, entity.team == self.local_team)
                    overlay.end_drawing()

                elapsed_time = time.time() - start_time
                if elapsed_time < frame_time:
                    sleep(frame_time - elapsed_time)
            except KeyboardInterrupt:
                logger.debug("Overlay stopped by user.")
                self.stop()
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                sleep(MAIN_LOOP_SLEEP)

        overlay.overlay_close()
        logger.debug("Overlay loop ended.")

    def stop(self) -> None:
        """Stop the Overlay and clean up resources."""
        self.is_running = False
        self.stop_event.set()
        time.sleep(0.1)
        logger.debug("Overlay stopped.")