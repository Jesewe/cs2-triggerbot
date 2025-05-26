import customtkinter as ctk

def populate_faq(main_window, frame):
    """Populate the FAQ frame with questions and answers."""
    faq_container = ctk.CTkScrollableFrame(
        frame,
        fg_color="transparent"
    )
    faq_container.pack(fill="both", expand=True, padx=40, pady=40)
    
    # Page title with subtitle
    title_frame = ctk.CTkFrame(faq_container, fg_color="transparent")
    title_frame.pack(fill="x", pady=(0, 40))
    
    ctk.CTkLabel(
        title_frame,
        text="❓ Frequently Asked Questions",
        font=ctk.CTkFont(size=32, weight="bold"),
        text_color=("#1f2937", "#E0E0E0")
    ).pack(anchor="w")
    
    ctk.CTkLabel(
        title_frame,
        text="Find answers to common questions about TriggerBot usage and configuration",
        font=ctk.CTkFont(size=16),
        text_color=("#6b7280", "#9ca3af")
    ).pack(anchor="w", pady=(8, 0))
    
    # FAQ items
    faqs = [
        ("What is a TriggerBot?", "A TriggerBot automatically shoots when your crosshair is positioned over an enemy player, providing enhanced reaction times in competitive gameplay. It works by detecting enemy pixels and triggering mouse clicks."),
        
        ("Is this tool safe to use?", "This tool is provided for educational and research purposes only. Using automation tools in online games may violate terms of service and could result in account penalties. Always check game rules before use."),
        
        ("How do I configure the trigger key?", "Navigate to Settings and enter your preferred key in the Trigger Key field. You can use keyboard keys (e.g., 'x', 'c', 'v') or mouse buttons (e.g., 'x1' for mouse button 4, 'x2' for mouse button 5)."),
        
        ("What are the delay settings for?", "Delay settings add realistic timing variations to make the bot behavior less detectable. Min/Max delays control shot timing randomization, while Post Shot Delay adds a pause after each shot to simulate human reaction time."),
        
        ("Can I use this on FACEIT or ESEA?", "No, using automation tools on anti-cheat protected platforms like FACEIT, ESEA, or VAC-secured servers is strictly prohibited and will result in permanent bans. Use only on casual servers or offline practice."),
        
        ("How do I update the offsets?", "Offsets are automatically fetched from the server when the application starts. The dashboard shows the last update timestamp for your reference. Manual refresh is available in Settings if needed."),
        
        ("Why isn't the bot triggering?", "Common issues include: incorrect trigger key binding, game not in focus, enemy not clearly visible in crosshair, or game resolution/settings changed. Check Settings and ensure proper configuration."),

        ("What should I do if the app crashes?", "Try restarting the application first. If crashes persist, check that you have the latest version, ensure your system meets requirements, and verify no antivirus is blocking the application."),

        ("Is there a hotkey to toggle the bot on/off?", "Yes, you can set a toggle hotkey in Settings. This allows you to quickly enable/disable the triggerbot during gameplay without alt-tabbing to the application.")
    ]
    
    for i, (question, answer) in enumerate(faqs):
        faq_card = ctk.CTkFrame(
            faq_container,
            corner_radius=12,
            fg_color=("#ffffff", "#161b22"),
            border_width=1,
            border_color=("#e5e7eb", "#30363d")
        )
        faq_card.pack(fill="x", pady=(0, 16))
        
        # Question header
        question_frame = ctk.CTkFrame(faq_card, fg_color="transparent")
        question_frame.pack(fill="x", padx=24, pady=(20, 10))
        
        # Question number badge
        number_badge = ctk.CTkFrame(
            question_frame,
            width=30,
            height=30,
            corner_radius=15,
            fg_color="#D5006D"
        )
        number_badge.pack(side="left", padx=(0, 12))
        number_badge.pack_propagate(False)
        
        ctk.CTkLabel(
            number_badge,
            text=str(i+1),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Question text
        question_label = ctk.CTkLabel(
            question_frame,
            text=question,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#1f2937", "#E0E0E0"),
            anchor="w"
        )
        question_label.pack(side="left", fill="x", expand=True)
        
        # Answer
        answer_frame = ctk.CTkFrame(faq_card, fg_color="transparent")
        answer_frame.pack(fill="x", padx=66, pady=(0, 20))
        
        ctk.CTkLabel(
            answer_frame,
            text=answer,
            font=ctk.CTkFont(size=14),
            text_color=("#4b5563", "#9ca3af"),
            anchor="w",
            wraplength=750,
            justify="left"
        ).pack(fill="x")
    
    # Footer with additional help
    footer_frame = ctk.CTkFrame(
        faq_container,
        corner_radius=12,
        fg_color=("#f8fafc", "#0d1117"),
        border_width=1,
        border_color=("#e2e8f0", "#21262d")
    )
    footer_frame.pack(fill="x", pady=(30, 0))
    
    ctk.CTkLabel(
        footer_frame,
        text="💡 Still have questions?",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=("#1f2937", "#E0E0E0")
    ).pack(pady=(20, 5))
    
    ctk.CTkLabel(
        footer_frame,
        text="Check the documentation or visit github issues for additional support and tips.",
        font=ctk.CTkFont(size=14),
        text_color=("#6b7280", "#9ca3af")
    ).pack(pady=(0, 20))