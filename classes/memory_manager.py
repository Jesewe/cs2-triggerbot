import pymem
import pymem.process
from classes.logger import Logger
from classes.utility import Utility

# Initialize the logger for consistent logging
logger = Logger.get_logger()

class MemoryManager:
    def __init__(self, offsets: dict, client_data: dict) -> None:
        self.offsets, self.client_data = offsets, client_data
        self.pm, self.client_base = None, None
        self.ent_list = None  # Cache for entity list pointer
        # Offset attributes will be set by load_offsets
        self.dwEntityList = None
        self.dwLocalPlayerPawn = None
        self.m_iHealth = None
        self.m_iTeamNum = None
        self.m_iIDEntIndex = None

    def initialize(self) -> bool:
        """
        Initialize memory access by attaching to the process and setting up necessary data.
        Returns True if successful, False otherwise.
        """
        # Check if pymem is initialized and the client module is retrieved
        if not self.initialize_pymem() or not self.get_client_module():
            return False
        # Cache the entity list pointer
        self.load_offsets()
        if self.dwEntityList is None:  # Ensure offsets were loaded successfully
            return False
        self.ent_list = self.pm.read_longlong(self.client_base + self.dwEntityList)
        return True

    def initialize_pymem(self) -> bool:
        """Attach pymem to the game process."""
        try:
            # Attempt to attach to the cs2.exe process
            self.pm = pymem.Pymem("cs2.exe")
            logger.info("Successfully attached to cs2.exe process.")
            return True
        except pymem.exception.ProcessNotFound:
            # Log an error if the process is not found
            logger.error("cs2.exe process not found. Ensure the game is running.")
            return False
        except Exception as e:
            # Log any other exceptions that may occur
            logger.error(f"Unexpected error while attaching to cs2.exe: {e}")
            return False

    def get_client_module(self) -> bool:
        """Retrieve the client.dll module base address."""
        try:
            # Attempt to retrieve the client.dll module
            client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
            self.client_base = client_module.lpBaseOfDll
            logger.info("client.dll module found and base address retrieved.")
            return True
        except pymem.exception.ModuleNotFoundError:
            # Log an error if the module is not found
            logger.error("client.dll not found. Ensure it is loaded.")
            return False
        except Exception as e:
            # Log any other exceptions that may occur
            logger.error(f"Unexpected error while retrieving client.dll module: {e}")
            return False

    def load_offsets(self) -> None:
        """Load memory offsets from Utility.extract_offsets."""
        extracted = Utility.extract_offsets(self.offsets, self.client_data)
        if extracted:
            self.dwEntityList = extracted["dwEntityList"]
            self.dwLocalPlayerPawn = extracted["dwLocalPlayerPawn"]
            self.m_iHealth = extracted["m_iHealth"]
            self.m_iTeamNum = extracted["m_iTeamNum"]
            self.m_iIDEntIndex = extracted["m_iIDEntIndex"]
            logger.info("Offsets initialized successfully.")
        else:
            logger.error("Failed to initialize offsets from extracted data.")

    def get_entity(self, index: int):
        """Retrieve an entity from the entity list."""
        try:
            # Use cached entity list pointer
            list_offset = 0x8 * (index >> 9)
            ent_entry = self.pm.read_longlong(self.ent_list + list_offset + 0x10)
            entity_offset = 120 * (index & 0x1FF)
            return self.pm.read_longlong(ent_entry + entity_offset)
        except Exception as e:
            logger.error(f"Error reading entity: {e}")
            return None

    def get_fire_logic_data(self) -> dict | None:
        """Retrieve data necessary for firing logic."""
        try:
            # Read the local player and entity ID
            player = self.pm.read_longlong(self.client_base + self.dwLocalPlayerPawn)
            entity_id = self.pm.read_int(player + self.m_iIDEntIndex)

            if entity_id > 0:
                # Retrieve the entity, team, and health
                entity = self.get_entity(entity_id)
                if entity:
                    entity_team = self.pm.read_int(entity + self.m_iTeamNum)
                    player_team = self.pm.read_int(player + self.m_iTeamNum)
                    entity_health = self.pm.read_int(entity + self.m_iHealth)
                    return {
                        "entity_team": entity_team,
                        "player_team": player_team,
                        "entity_health": entity_health
                    }
            return None
        except Exception as e:
            # Log any exceptions that may occur during the process
            if "Could not read memory at" in str(e):
                logger.error("Game was updated, new offsets are required. Please wait for the offsets update.")
            else:
                logger.error(f"Error in fire logic: {e}")
            return None