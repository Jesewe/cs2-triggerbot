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
        text="Find answers to common questions about TriggerBot usage and configuration",
        font=("Gambetta", 16),
        text_color=("#6b7280", "#9ca3af")
    ).pack(anchor="w", pady=(8, 0))
    
    # List of FAQ items
    faqs = [
        ("What is a TriggerBot?", "A TriggerBot automatically shoots when your crosshair is positioned over an enemy player, providing enhanced reaction times in competitive gameplay. It works by detecting enemy pixels and triggering mouse clicks."),
        ("Is this tool safe to use?", "This tool is provided for educational and research purposes only. Using automation tools in online games may violate terms of service and could result in account penalties. Always check game rules before use."),
        ("How do I configure the trigger key?", "Navigate to Settings and enter your preferred key in the Trigger Key field. You can use keyboard keys (e.g., 'x', 'c', 'v') or mouse buttons (e.g., 'mouse4' for mouse button 4, 'mouse5' for mouse button 5)."),
        ("What are the delay settings for?", "Delay settings give the bot a more natural feel by adding timing differences. You can set minimum and maximum delays to randomize how quickly it shoots. Plus, the Post Shot Delay adds a short pause after each shot, making it seem like a real person is reacting."),
        ("Can I use this on FACEIT or ESEA?", "No, you can't use automation tools on anti-cheat platforms like FACEIT, ESEA, or VAC-secured servers. Doing so will get you a permanent ban. Stick to casual servers or practice offline instead."),
        ("How do I update the offsets?", "When you start the app, it automatically gets the latest offsets from the server. You can see when it was last updated on the dashboard. If you want to refresh it manually, just go to Settings."),
        ("Why isn't the bot triggering?", "Here are some usual problems: the trigger key might be set wrong, the game window isn't focused, you might not see the enemy in your crosshair, or your game settings might have changed. Take a look at your Settings to make sure everything's set up right."),
        ("What should I do if the app crashes?", "First, try restarting the app. If it's still crashing, make sure you have the latest version, check that your system meets the requirements, and see if any antivirus is blocking the app."),
        ("Is there a hotkey to toggle the bot on/off?", "Yes, you can set a toggle hotkey in Settings. This allows you to quickly enable/disable the triggerbot during gameplay without alt-tabbing to the application.")
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