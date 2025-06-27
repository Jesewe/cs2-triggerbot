import customtkinter as ctk

def populate_general_settings(main_window, frame):
    """
    Populates the General Settings tab with UI elements for configuring main application features.
    All changes are saved in real-time to the configuration.
    """
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
        text="⚙️  General Settings",
        font=("Chivo", 36, "bold"),
        text_color=("#1f2937", "#ffffff"),
        anchor="w"
    )
    title_label.pack(side="left")

    # Subtitle providing context
    subtitle_label = ctk.CTkLabel(
        title_frame,
        text="Configure main application features",
        font=("Gambetta", 16),
        text_color=("#64748b", "#94a3b8"),
        anchor="w"
    )
    subtitle_label.pack(side="left", padx=(20, 0), pady=(10, 0))

    # Create section for general feature settings
    create_features_section(main_window, settings)

def create_features_section(main_window, parent):
    """Create section for configuring main application features."""
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
        text="🔧  Feature Configuration",
        font=("Chivo", 24, "bold"),
        text_color=("#1f2937", "#ffffff"),
        anchor="w"
    ).pack(side="left")

    # Description of section purpose
    ctk.CTkLabel(
        header,
        text="Enable or disable main application features",
        font=("Gambetta", 14),
        text_color=("#64748b", "#94a3b8"),
        anchor="e"
    ).pack(side="right")

    # List of settings for feature configuration
    settings_list = [
        ("Enable Trigger", "checkbox", "Trigger", "Toggle the trigger bot feature"),
        ("Enable Overlay", "checkbox", "Overlay", "Toggle the ESP overlay feature"),
        ("Enable Bunnyhop", "checkbox", "Bunnyhop", "Toggle the bunnyhop feature"),
        ("Enable Noflash", "checkbox", "Noflash", "Toggle the noflash feature")
    ]

    # Create each setting item
    for i, (label_text, widget_type, key, description) in enumerate(settings_list):
        create_setting_item(
            section,
            label_text,
            description,
            widget_type,
            key,
            main_window,
            is_last=(i == len(settings_list) - 1)
        )

def create_setting_item(parent, label_text, description, widget_type, key, main_window, is_last=False):
    item_frame = ctk.CTkFrame(parent, fg_color="transparent")
    item_frame.pack(fill="x", padx=40, pady=(0, 30 if not is_last else 40))
    
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
    
    label_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    label_frame.pack(side="left", fill="x", expand=True)
    
    ctk.CTkLabel(
        label_frame,
        text=label_text,
        font=("Chivo", 16, "bold"),
        text_color=("#1f2937", "#ffffff"),
        anchor="w"
    ).pack(fill="x", pady=(0, 4))
    
    ctk.CTkLabel(
        label_frame,
        text=description,
        font=("Gambetta", 13),
        text_color=("#64748b", "#94a3b8"),
        anchor="w",
        wraplength=400
    ).pack(fill="x")
    
    widget_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    widget_frame.pack(side="right", padx=(30, 0))
    
    if widget_type == "checkbox":
        # Create a BooleanVar with the current config value
        var = ctk.BooleanVar(value=main_window.triggerbot.config["General"].get(key, False))
        # Create the checkbox widget
        widget = ctk.CTkCheckBox(
            widget_frame,
            text="",
            variable=var,
            width=30,
            height=30,
            corner_radius=8,
            border_width=2,
            fg_color=("#D5006D", "#E91E63"),
            hover_color=("#B8004A", "#C2185B"),
            checkmark_color="#ffffff",
            command=lambda: main_window.save_settings(show_message=False)
        )
        # Assign the BooleanVar to the appropriate main_window attribute
        if key == "Trigger":
            main_window.trigger_var = var
        elif key == "Overlay":
            main_window.overlay_var = var
        elif key == "Bunnyhop":
            main_window.bunnyhop_var = var
        elif key == "Noflash":
            main_window.noflash_var = var
        widget.pack()
    
    else:
        raise ValueError(f"Unsupported widget type: {widget_type}")
    
    return item_frame