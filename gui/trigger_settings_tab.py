import customtkinter as ctk

def populate_trigger_settings(main_window, frame):
    """Populate the settings frame with configuration options."""
    # Create a scrollable container for settings
    settings = ctk.CTkScrollableFrame(
        frame,
        fg_color="transparent"
    )
    settings.pack(fill="both", expand=True, padx=40, pady=40)
    
    # Frame for page title and subtitle
    title_frame = ctk.CTkFrame(settings, fg_color="transparent")
    title_frame.pack(fill="x", pady=(0, 40))
    
    # Settings title with an icon
    title_label = ctk.CTkLabel(
        title_frame,
        text="🔫  Trigger Settings",
        font=("Chivo", 36, "bold"),
        text_color=("#1f2937", "#ffffff"),
        anchor="w"
    )
    title_label.pack(side="left")
    
    # Subtitle providing context
    subtitle_label = ctk.CTkLabel(
        title_frame,
        text="Configure your trigger bot preferences",
        font=("Gambetta", 16),
        text_color=("#64748b", "#94a3b8"),
        anchor="w"
    )
    subtitle_label.pack(side="left", padx=(20, 0), pady=(10, 0))
    
    # Create sections for trigger and timing settings
    create_trigger_config_section(main_window, settings)
    create_timing_settings_section(main_window, settings)

def create_trigger_config_section(main_window, parent):
    """Create trigger configuration section with related settings."""
    # Section frame with modern styling
    section = ctk.CTkFrame(
        parent,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    section.pack(fill="x", pady=(0, 30))
    
    # Header frame for section title and description
    header = ctk.CTkFrame(section, fg_color="transparent")
    header.pack(fill="x", padx=40, pady=(40, 30))
    
    # Section title with icon
    ctk.CTkLabel(
        header,
        text="🎯  Configuration",
        font=("Chivo", 24, "bold"),
        text_color=("#1f2937", "#ffffff"),
        anchor="w"
    ).pack(side="left")
    
    # Description of section purpose
    ctk.CTkLabel(
        header,
        text="Control how the trigger responds",
        font=("Gambetta", 14),
        text_color=("#64748b", "#94a3b8"),
        anchor="e"
    ).pack(side="right")
    
    # List of settings for trigger configuration
    settings_list = [
        ("Trigger Key", "entry", "TriggerKey", "Key to activate trigger (e.g., 'x' or 'mouse4' for mouse button 4)"),
        ("Toggle Mode", "checkbox", "ToggleMode", "Enable toggle mode instead of hold mode"),
        ("Attack Teammates", "checkbox", "AttackOnTeammates", "Allow triggering on teammates")
    ]
    
    # Create each setting item
    for i, (label_text, widget_type, key, description) in enumerate(settings_list):
        item_frame = create_setting_item(
            section, 
            label_text, 
            description, 
            widget_type, 
            key, 
            main_window,
            is_last=(i == len(settings_list) - 1)
        )

def create_timing_settings_section(main_window, parent):
    """Create timing settings section for delay configurations."""
    # Section frame with modern styling
    section = ctk.CTkFrame(
        parent,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    section.pack(fill="x", pady=(0, 30))
    
    # Header frame for section title and description
    header = ctk.CTkFrame(section, fg_color="transparent")
    header.pack(fill="x", padx=40, pady=(40, 30))
    
    # Section title with icon
    ctk.CTkLabel(
        header,
        text="⏱️  Timing Settings",
        font=("Chivo", 24, "bold"),
        text_color=("#1f2937", "#ffffff"),
        anchor="w"
    ).pack(side="left")
    
    # Description of section purpose
    ctk.CTkLabel(
        header,
        text="Fine-tune shooting delays",
        font=("Gambetta", 14),
        text_color=("#64748b", "#94a3b8"),
        anchor="e"
    ).pack(side="right")
    
    # List of settings for timing configuration
    settings_list = [
        ("Min Shot Delay", "entry", "ShotDelayMin", "Minimum delay between shots (seconds)"),
        ("Max Shot Delay", "entry", "ShotDelayMax", "Maximum delay between shots (seconds)"),
        ("Post Shot Delay", "entry", "PostShotDelay", "Delay after shooting (seconds)")
    ]
    
    # Create each setting item
    for i, (label_text, widget_type, key, description) in enumerate(settings_list):
        item_frame = create_setting_item(
            section, 
            label_text, 
            description, 
            widget_type, 
            key, 
            main_window,
            is_last=(i == len(settings_list) - 1)
        )

def create_setting_item(parent, label_text, description, widget_type, key, main_window, is_last=False):
    """Create a standardized setting item with improved styling."""
    # Frame for the setting item
    item_frame = ctk.CTkFrame(parent, fg_color="transparent")
    item_frame.pack(fill="x", padx=40, pady=(0, 30 if not is_last else 40))
    
    # Container with hover effect
    container = ctk.CTkFrame(
        item_frame,
        corner_radius=12,
        fg_color=("#f8fafc", "#252830"),
        border_width=1,
        border_color=("#e2e8f0", "#374151")
    )
    container.pack(fill="x", pady=(0, 0))
    
    # Content frame within the container
    content_frame = ctk.CTkFrame(container, fg_color="transparent")
    content_frame.pack(fill="x", padx=25, pady=25)
    
    # Frame for label and description
    label_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    label_frame.pack(side="left", fill="x", expand=True)
    
    # Setting name label
    ctk.CTkLabel(
        label_frame,
        text=label_text,
        font=("Chivo", 16, "bold"),
        text_color=("#1f2937", "#ffffff"),
        anchor="w"
    ).pack(fill="x", pady=(0, 4))
    
    # Description of the setting
    ctk.CTkLabel(
        label_frame,
        text=description,
        font=("Gambetta", 13),
        text_color=("#64748b", "#94a3b8"),
        anchor="w",
        wraplength=400
    ).pack(fill="x")
    
    # Frame for the input widget
    widget_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    widget_frame.pack(side="right", padx=(30, 0))
    
    # Create widget based on type
    if widget_type == "entry":
        widget = ctk.CTkEntry(
            widget_frame,
            width=220,
            height=45,
            corner_radius=12,
            border_width=2,
            border_color=("#d1d5db", "#374151"),
            fg_color=("#ffffff", "#1f2937"),
            text_color=("#1f2937", "#ffffff"),
            font=("Chivo", 14),
            justify="center"
        )
        if key == "TriggerKey":
            main_window.trigger_key_entry = widget
            widget.insert(0, main_window.triggerbot.config.get('Trigger', {}).get('TriggerKey', ''))
            widget.bind("<FocusOut>", lambda e: main_window.save_settings())
            widget.bind("<Return>", lambda e: main_window.save_settings())
        elif key == "ShotDelayMin":
            main_window.min_delay_entry = widget
            widget.insert(0, str(main_window.triggerbot.config.get('Trigger', {}).get('ShotDelayMin', 0.01)))
            widget.bind("<FocusOut>", lambda e: main_window.save_settings())
            widget.bind("<Return>", lambda e: main_window.save_settings())
        elif key == "ShotDelayMax":
            main_window.max_delay_entry = widget
            widget.insert(0, str(main_window.triggerbot.config.get('Trigger', {}).get('ShotDelayMax', 0.03)))
            widget.bind("<FocusOut>", lambda e: main_window.save_settings())
            widget.bind("<Return>", lambda e: main_window.save_settings())
        elif key == "PostShotDelay":
            main_window.post_shot_delay_entry = widget
            widget.insert(0, str(main_window.triggerbot.config.get('Trigger', {}).get('PostShotDelay', 0.1)))
            widget.bind("<FocusOut>", lambda e: main_window.save_settings())
            widget.bind("<Return>", lambda e: main_window.save_settings())
        widget.pack()
    
    elif widget_type == "checkbox":
        if key == "ToggleMode":
            main_window.toggle_mode_var = ctk.BooleanVar(value=main_window.triggerbot.config.get('Trigger', {}).get('ToggleMode', False))
            widget = ctk.CTkCheckBox(
                widget_frame,
                text="",
                variable=main_window.toggle_mode_var,
                width=30,
                height=30,
                corner_radius=8,
                border_width=2,
                fg_color=("#D5006D", "#E91E63"),
                hover_color=("#B8004A", "#C2185B"),
                checkmark_color="#ffffff",
                command=main_window.save_settings
            )
        elif key == "AttackOnTeammates":
            main_window.attack_teammates_var = ctk.BooleanVar(value=main_window.triggerbot.config.get('Trigger', {}).get('AttackOnTeammates', False))
            widget = ctk.CTkCheckBox(
                widget_frame,
                text="",
                variable=main_window.attack_teammates_var,
                width=30,
                height=30,
                corner_radius=8,
                border_width=2,
                fg_color=("#D5006D", "#E91E63"),
                hover_color=("#B8004A", "#C2185B"),
                checkmark_color="#ffffff",
                command=main_window.save_settings
            )
        widget.pack()
    
    else:
        raise ValueError(f"Unsupported widget type: {widget_type}")
    
    return item_frame