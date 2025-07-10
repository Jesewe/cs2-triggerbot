import customtkinter as ctk

def populate_faq(main_window, frame):
    """Populate the FAQ frame with questions and answers."""
    # Scrollable container for FAQ content
    faq_container = ctk.CTkScrollableFrame(
        frame,
        fg_color="transparent"
    )
    faq_container.pack(fill="both", expand=True, padx=40, pady=40)
    
    # Frame for page title and subtitle
    title_frame = ctk.CTkFrame(faq_container, fg_color="transparent")
    title_frame.pack(fill="x", pady=(0, 40))
    
    # FAQ title with icon
    ctk.CTkLabel(
        title_frame,
        text="❓ Frequently Asked Questions",
        font=("Chivo", 32, "bold"),
        text_color=("#1f2937", "#E0E0E0")
    ).pack(anchor="w")
    
    # Subtitle providing context
    ctk.CTkLabel(
        title_frame,
        text="Find answers to common questions about TriggerBot, Overlay, Bunnyhop, and NoFlash usage and configuration",
        font=("Gambetta", 16),
        text_color=("#6b7280", "#9ca3af")
    ).pack(anchor="w", pady=(8, 0))
    
    # List of FAQ items
    faqs = [
        ("What is a TriggerBot?", "A TriggerBot automatically shoots when your crosshair is positioned over an enemy player, providing enhanced reaction times in competitive gameplay. It works by detecting enemy pixels and triggering mouse clicks."),
        ("What does the Overlay (ESP) feature do?", "The Overlay (ESP) feature displays visual information on the game screen, such as enemy bounding boxes, snaplines, health numbers, nicknames, and a minimap, helping you track opponents and teammates effectively."),
        ("What is the Bunnyhop feature?", "The Bunnyhop feature automates the process of bunny hopping in Counter-Strike 2, allowing continuous jumping to maintain speed and improve movement control without manual input."),
        ("What is the NoFlash feature?", "The NoFlash feature reduces or eliminates the effect of flashbangs in Counter-Strike 2, ensuring you maintain visibility and can continue playing effectively even when flashed."),
        ("Is this tool safe to use?", "This tool is for educational purposes only. Using automation tools in online games violates terms of service and may result in bans. Use at your own risk."),
        ("How do I configure the trigger key?", "Navigate to the Trigger Settings tab and enter your preferred key in the Trigger Key field. You can use keyboard keys (e.g., 'x', 'c', 'v') or mouse buttons (e.g., 'mouse4' for mouse button 4, 'mouse5' for mouse button 5)."),
        ("What are the delay settings for?", "Delay settings in the Trigger Settings tab give the TriggerBot a more natural feel by adding timing differences. You can set minimum and maximum delays to randomize how quickly it shoots, and the Post Shot Delay adds a pause after each shot to mimic human reaction times."),
        ("How do I customize the Overlay (ESP) settings?", "In the Overlay Settings tab, you can enable or disable features like bounding boxes, snaplines, health numbers, nicknames, and the minimap. You can also adjust colors, line thickness, and minimap size to suit your preferences."),
        ("Can I use these features on FACEIT or ESEA?", "No, automation tools like TriggerBot, Overlay, Bunnyhop, or NoFlash are not allowed on anti-cheat platforms like FACEIT, ESEA, or VAC-secured servers. Using them will likely result in a permanent ban. Stick to casual servers or offline practice."),
        ("How do I update the offsets?", "The app automatically fetches the latest offsets from the server on startup. You can check the last update time on the Dashboard."),
        ("Why isn't the TriggerBot triggering?", "Common issues include: incorrect trigger key configuration, the game window not being focused, the crosshair not being on an enemy, or changed game settings. Verify your settings in the Trigger Settings tab."),
        ("Why isn't the Overlay (ESP) displaying?", "Ensure the Overlay feature is enabled in General Settings and that the game is running. Check the Overlay Settings tab to confirm visibility options (e.g., bounding boxes, snaplines) are enabled. Also, verify that your game is in a compatible mode (e.g., windowed or borderless)."),
        ("Why doesn't Bunnyhop work consistently?", "Bunnyhop may fail if the game window is not focused, the Bunnyhop feature is disabled in General Settings, or your timing settings interfere. Check the General Settings tab and ensure consistent key inputs."),
        ("Why is NoFlash not working?", "Ensure NoFlash is enabled in General Settings. It may not work if the game’s anti-cheat detects memory modifications or if the offsets are outdated. Restart the app to refresh offsets and verify game compatibility."),
        ("What should I do if the app crashes?", "Try restarting the app, ensuring you have the latest version, and checking system requirements. Verify that no antivirus is blocking the app. Check the Logs tab for error details."),
        ("Is there a hotkey to toggle features on/off?", "Yes, you can set a toggle hotkey for the TriggerBot in the Trigger Settings tab. Other features like Overlay, Bunnyhop, and NoFlash can be toggled via General Settings, but they don’t have individual hotkeys.")
    ]
    
    # Create FAQ cards
    for i, (question, answer) in enumerate(faqs):
        # Card for each FAQ item
        faq_card = ctk.CTkFrame(
            faq_container,
            corner_radius=12,
            fg_color=("#ffffff", "#161b22"),
            border_width=1,
            border_color=("#e5e7eb", "#30363d")
        )
        faq_card.pack(fill="x", pady=(0, 16))
        
        # Frame for question header
        question_frame = ctk.CTkFrame(faq_card, fg_color="transparent")
        question_frame.pack(fill="x", padx=24, pady=(20, 10))
        
        # Number badge for question
        number_badge = ctk.CTkFrame(
            question_frame,
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#D5006D"
        )
        number_badge.pack(side="left", padx=(0, 12))
        number_badge.pack_propagate(False)
        
        # Number inside badge
        ctk.CTkLabel(
            number_badge,
            text=str(i+1),
            font=("Chivo", 12, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Question text
        question_label = ctk.CTkLabel(
            question_frame,
            text=question,
            font=("Chivo", 16, "bold"),
            text_color=("#1f2937", "#E0E0E0"),
            anchor="w"
        )
        question_label.pack(side="left", fill="x", expand=True)
        
        # Frame for answer text
        answer_frame = ctk.CTkFrame(faq_card, fg_color="transparent")
        answer_frame.pack(fill="x", padx=66, pady=(0, 20))
        
        # Answer text with wrapping
        ctk.CTkLabel(
            answer_frame,
            text=answer,
            font=("Gambetta", 14),
            text_color=("#4b5563", "#9ca3af"),
            anchor="w",
            wraplength=750,
            justify="left"
        ).pack(fill="x")
    
    # Footer with additional help information
    footer_frame = ctk.CTkFrame(
        faq_container,
        corner_radius=12,
        fg_color=("#f8fafc", "#0d1117"),
        border_width=1,
        border_color=("#e2e8f0", "#21262d")
    )
    footer_frame.pack(fill="x", pady=(30, 0))
    
    # Footer title
    ctk.CTkLabel(
        footer_frame,
        text="💡 Still have questions?",
        font=("Chivo", 16, "bold"),
        text_color=("#1f2937", "#E0E0E0")
    ).pack(pady=(20, 5))
    
    # Footer guidance
    ctk.CTkLabel(
        footer_frame,
        text="Check the documentation or visit github issues for additional support and tips.",
        font=("Gambetta", 14),
        text_color=("#6b7280", "#9ca3af")
    ).pack(pady=(0, 20))