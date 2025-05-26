import customtkinter as ctk

def populate_settings(main_window, frame):
    """Populate the settings frame with configuration options."""
    # Settings container
    settings = ctk.CTkScrollableFrame(
        frame,
        fg_color="transparent"
    )
    settings.pack(fill="both", expand=True, padx=40, pady=40)
    
    # Page title with improved styling
    title_frame = ctk.CTkFrame(settings, fg_color="transparent")
    title_frame.pack(fill="x", pady=(0, 40))
    
    # Title with accent color
    title_label = ctk.CTkLabel(
        title_frame,
        text="⚙️ Settings",
        font=ctk.CTkFont(size=36, weight="bold"),
        text_color=("#1f2937", "#ffffff")
    )
    title_label.pack(side="left")
    
    # Subtitle
    subtitle_label = ctk.CTkLabel(
        title_frame,
        text="Configure your CS2 bot preferences",
        font=ctk.CTkFont(size=16),
        text_color=("#64748b", "#94a3b8")
    )
    subtitle_label.pack(side="left", padx=(20, 0), pady=(10, 0))
    
    # Settings sections with improved spacing
    create_trigger_config_section(main_window, settings)
    create_timing_settings_section(main_window, settings)
    
    # Action buttons with enhanced design
    actions_frame = ctk.CTkFrame(
        settings,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    actions_frame.pack(fill="x", pady=(40, 0))
    
    actions_content = ctk.CTkFrame(actions_frame, fg_color="transparent")
    actions_content.pack(fill="x", padx=40, pady=40)
    
    # Header
    header_frame = ctk.CTkFrame(actions_content, fg_color="transparent")
    header_frame.pack(fill="x", pady=(0, 30))
    
    ctk.CTkLabel(
        header_frame,
        text="💾 Configuration Management",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=("#1f2937", "#ffffff")
    ).pack(side="left")
    
    ctk.CTkLabel(
        header_frame,
        text="Save, reset, or manage your configuration",
        font=ctk.CTkFont(size=14),
        text_color=("#64748b", "#94a3b8")
    ).pack(side="right")
    
    # Buttons with improved layout
    buttons_frame = ctk.CTkFrame(actions_content, fg_color="transparent")
    buttons_frame.pack(fill="x")
    
    # Primary actions (left side)
    primary_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
    primary_frame.pack(side="left")
    
    save_btn = ctk.CTkButton(
        primary_frame,
        text="💾 Save Settings",
        command=main_window.save_settings,
        width=160,
        height=50,
        corner_radius=16,
        fg_color=("#22c55e", "#16a34a"),
        hover_color=("#16a34a", "#15803d"),
        font=ctk.CTkFont(size=16, weight="bold"),
        border_width=2,
        border_color=("#16a34a", "#15803d")
    )
    save_btn.pack(side="left", padx=(0, 15))
    
    reset_btn = ctk.CTkButton(
        primary_frame,
        text="🔄 Reset Defaults",
        command=main_window.reset_to_defaults,
        width=160,
        height=50,
        corner_radius=16,
        fg_color=("#6b7280", "#4b5563"),
        hover_color=("#4b5563", "#374151"),
        font=ctk.CTkFont(size=16, weight="bold"),
        border_width=2,
        border_color=("#4b5563", "#374151")
    )
    reset_btn.pack(side="left")
    
    # Secondary actions (right side)
    secondary_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
    secondary_frame.pack(side="right")
    
    config_btn = ctk.CTkButton(
        secondary_frame,
        text="📁 Open Config",
        command=main_window.open_config_directory,
        width=140,
        height=50,
        corner_radius=16,
        fg_color=("#3b82f6", "#2563eb"),
        hover_color=("#2563eb", "#1d4ed8"),
        font=ctk.CTkFont(size=16, weight="bold"),
        border_width=2,
        border_color=("#2563eb", "#1d4ed8")
    )
    config_btn.pack(side="left", padx=(0, 15))
    
    import_btn = ctk.CTkButton(
        secondary_frame,
        text="📤 Share/Import",
        command=main_window.show_share_import_dialog,
        width=140,
        height=50,
        corner_radius=16,
        fg_color=("#8b5cf6", "#7c3aed"),
        hover_color=("#7c3aed", "#6d28d9"),
        font=ctk.CTkFont(size=16, weight="bold"),
        border_width=2,
        border_color=("#7c3aed", "#6d28d9")
    )
    import_btn.pack(side="left")

def create_trigger_config_section(main_window, parent):
    """Create trigger configuration section."""
    section = ctk.CTkFrame(
        parent,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    section.pack(fill="x", pady=(0, 30))
    
    # Section header
    header = ctk.CTkFrame(section, fg_color="transparent")
    header.pack(fill="x", padx=40, pady=(40, 30))
    
    ctk.CTkLabel(
        header,
        text="🎯 Trigger Configuration",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=("#1f2937", "#ffffff")
    ).pack(side="left")
    
    ctk.CTkLabel(
        header,
        text="Control how the trigger responds",
        font=ctk.CTkFont(size=14),
        text_color=("#64748b", "#94a3b8")
    ).pack(side="right")
    
    # Settings items with improved layout
    settings_list = [
        ("Trigger Key", "entry", "trigger_key", "Key to activate trigger (e.g., 'x' or 'x1' for mouse button 4)"),
        ("Toggle Mode", "checkbox", "toggle_mode", "Enable toggle mode instead of hold mode"),
        ("Attack Teammates", "checkbox", "attack_teammates", "Allow triggering on teammates")
    ]
    
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
    """Create timing settings section."""
    section = ctk.CTkFrame(
        parent,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    section.pack(fill="x", pady=(0, 30))
    
    # Section header
    header = ctk.CTkFrame(section, fg_color="transparent")
    header.pack(fill="x", padx=40, pady=(40, 30))
    
    ctk.CTkLabel(
        header,
        text="⏱️ Timing Settings",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=("#1f2937", "#ffffff")
    ).pack(side="left")
    
    ctk.CTkLabel(
        header,
        text="Fine-tune shooting delays",
        font=ctk.CTkFont(size=14),
        text_color=("#64748b", "#94a3b8")
    ).pack(side="right")
    
    # Settings items with improved layout
    settings_list = [
        ("Min Shot Delay", "entry", "min_delay", "Minimum delay between shots (seconds)"),
        ("Max Shot Delay", "entry", "max_delay", "Maximum delay between shots (seconds)"),
        ("Post Shot Delay", "entry", "post_delay", "Delay after shooting (seconds)")
    ]
    
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
    item_frame = ctk.CTkFrame(parent, fg_color="transparent")
    item_frame.pack(fill="x", padx=40, pady=(0, 30 if not is_last else 40))
    
    # Main container with hover effect background
    container = ctk.CTkFrame(
        item_frame,
        corner_radius=12,
        fg_color=("#f8fafc", "#252830"),
        border_width=1,
        border_color=("#e2e8f0", "#374151")
    )
    container.pack(fill="x", pady=(0, 0))
    
    content_frame = ctk.CTkFrame(container, fg_color="transparent")
    content_frame.pack(fill="x", padx=25, pady=25)
    
    # Left side - Label and description
    label_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    label_frame.pack(side="left", fill="x", expand=True)
    
    # Setting name
    ctk.CTkLabel(
        label_frame,
        text=label_text,
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=("#1f2937", "#ffffff"),
        anchor="w"
    ).pack(fill="x", pady=(0, 4))
    
    # Description
    ctk.CTkLabel(
        label_frame,
        text=description,
        font=ctk.CTkFont(size=13),
        text_color=("#64748b", "#94a3b8"),
        anchor="w",
        wraplength=400
    ).pack(fill="x")
    
    # Right side - Widget
    widget_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    widget_frame.pack(side="right", padx=(30, 0))
    
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
            font=ctk.CTkFont(size=14)
        )
        widget.pack()
        
        # Set values based on key
        if key == "trigger_key":
            main_window.trigger_key_entry = widget
            widget.insert(0, main_window.bot.config.get('Settings', {}).get('TriggerKey', ''))
        elif key == "min_delay":
            main_window.min_delay_entry = widget
            widget.insert(0, str(main_window.bot.config.get('Settings', {}).get('ShotDelayMin', 0.01)))
        elif key == "max_delay":
            main_window.max_delay_entry = widget
            widget.insert(0, str(main_window.bot.config.get('Settings', {}).get('ShotDelayMax', 0.03)))
        elif key == "post_delay":
            main_window.post_shot_delay_entry = widget
            widget.insert(0, str(main_window.bot.config.get('Settings', {}).get('PostShotDelay', 0.1)))
    
    elif widget_type == "checkbox":
        if key == "toggle_mode":
            main_window.toggle_mode_var = ctk.BooleanVar(value=main_window.bot.config.get('Settings', {}).get('ToggleMode', False))
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
                checkmark_color="#ffffff"
            )
        elif key == "attack_teammates":
            main_window.attack_teammates_var = ctk.BooleanVar(value=main_window.bot.config.get('Settings', {}).get('AttackOnTeammates', False))
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
                checkmark_color="#ffffff"
            )
        
        widget.pack()
    
    return item_frame