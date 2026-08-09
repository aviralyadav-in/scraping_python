import customtkinter as ctk
from tkinter import messagebox
import threading

from telegram_deals_scraper import start_scraper


# ================= APP SETTINGS =================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ================= STRICT INPUT VALIDATION =================

def validate_channel(new_value):

    # Empty allowed (backspace support)
    if new_value == "":
        return True

    # Max length check
    if len(new_value) > 32:
        return False

    # First character must be an alphabet letter
    if len(new_value) == 1:
        return new_value[0].isalpha()

    # Allow only letters and underscores
    return all(
        ch.isalpha() or ch == "_"
        for ch in new_value
    )


def validate_limit(new_value):

    if new_value == "":
        return True

    if not new_value.isdigit():
        return False

    if int(new_value) > 100:
        return False

    return True


# ================= SCRAPER =================

def run_scraper():

    channel = channel_entry.get().strip()
    limit = limit_entry.get().strip()

    # Channel validation
    if len(channel) < 5:

        messagebox.showerror(
            "Invalid Channel",
            "Channel name must have minimum 5 characters."
        )

        return

    # Limit validation
    if limit == "":

        messagebox.showerror(
            "Invalid Limit",
            "Enter number of deals."
        )

        return

    # Disable button
    start_button.configure(
        state="disabled",
        text="⟳  Scraping..."
    )

    # Update status area
    update_status(
        "SCRAPING",
        "Scraping in progress",
        "Fetching deals from Telegram...",
        "#D97706"
    )

    try:

        # Start scraper
        start_scraper(
            channel,
            int(limit)
        )

        # Success status
        update_status(
            "SUCCESS",
            "Completed Successfully",
            "Your deals have been scraped successfully.",
            "#059669"
        )

        messagebox.showinfo(
            "Scraping Complete",
            "Deals scraped successfully!"
        )

    except Exception as e:

        # Failed status
        update_status(
            "ERROR",
            "Scraping Failed",
            "An error occurred while scraping deals.",
            "#DC2626"
        )

        messagebox.showerror(
            "Scraping Error",
            str(e)
        )

    finally:

        # Enable button again
        start_button.configure(
            state="normal",
            text="▶  Start Scraping"
        )


def start_thread():

    threading.Thread(
        target=run_scraper,
        daemon=True
    ).start()


# ================= STATUS UPDATE =================

def update_status(status_type, title, description, color):

    # Use Tkinter main thread for UI updates
    try:

        app.after(
            0,
            lambda: apply_status(
                status_type,
                title,
                description,
                color
            )
        )

    except Exception:
        pass


def apply_status(status_type, title, description, color):

    # Main status dot
    status_dot.configure(
        text="●",
        text_color=color
    )

    # Main status title
    status_label.configure(
        text=title,
        text_color=color
    )

    # Description
    status_description.configure(
        text=description
    )

    # Top status badge
    if status_type == "SCRAPING":

        top_status.configure(
            text="  ●  SCRAPING  ",
            text_color="#D97706",
            fg_color="#FEF3C7"
        )

    elif status_type == "SUCCESS":

        top_status.configure(
            text="  ●  COMPLETED  ",
            text_color="#059669",
            fg_color="#D1FAE5"
        )

    elif status_type == "ERROR":

        top_status.configure(
            text="  ●  ERROR  ",
            text_color="#DC2626",
            fg_color="#FEE2E2"
        )

    else:

        top_status.configure(
            text="  ●  READY  ",
            text_color="#475569",
            fg_color="#E2E8F0"
        )


# ================= WINDOW =================

app = ctk.CTk()

app.title(
    "Telegram Deals Scraper"
)

app.geometry(
    "820x700"
)

app.resizable(
    False,
    False
)

app.configure(
    fg_color="#F8FAFC"
)


# ================= HEADER =================

header = ctk.CTkFrame(
    app,
    height=135,
    corner_radius=0,
    fg_color="#0F172A"
)

header.pack(
    fill="x"
)

header.pack_propagate(False)


# Header inner container

header_inner = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

header_inner.pack(
    fill="both",
    expand=True,
    padx=48
)


# ================= HEADER LEFT =================

header_left = ctk.CTkFrame(
    header_inner,
    fg_color="transparent"
)

header_left.pack(
    side="left",
    pady=25
)


# Icon

icon_box = ctk.CTkFrame(
    header_left,
    width=58,
    height=58,
    corner_radius=16,
    fg_color="#1E3A8A"
)

icon_box.pack(
    side="left"
)

icon_box.pack_propagate(False)


ctk.CTkLabel(
    icon_box,
    text="✦",
    font=(
        "Segoe UI",
        30,
        "bold"
    ),
    text_color="#93C5FD"
).pack(
    expand=True
)


# Title area

title_area = ctk.CTkFrame(
    header_left,
    fg_color="transparent"
)

title_area.pack(
    side="left",
    padx=16
)


ctk.CTkLabel(
    title_area,
    text="Telegram Deals Scraper",
    font=(
        "Segoe UI",
        25,
        "bold"
    ),
    text_color="#FFFFFF"
).pack(
    anchor="w"
)


ctk.CTkLabel(
    title_area,
    text="Smart deal collection & management",
    font=(
        "Segoe UI",
        12
    ),
    text_color="#94A3B8"
).pack(
    anchor="w",
    pady=(4, 0)
)


# ================= HEADER RIGHT STATUS =================

top_status = ctk.CTkLabel(
    header_inner,
    text="  ●  READY  ",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    text_color="#475569",
    fg_color="#E2E8F0",
    corner_radius=20
)

top_status.pack(
    side="right",
    pady=40
)


# ================= MAIN AREA =================

main_container = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

main_container.pack(
    fill="both",
    expand=True,
    padx=55,
    pady=(28, 15)
)


# ================= MAIN CARD =================

card = ctk.CTkFrame(
    main_container,
    corner_radius=22,
    fg_color="#FFFFFF",
    border_width=1,
    border_color="#E2E8F0"
)

card.pack(
    fill="x"
)


# ================= CARD HEADER =================

card_header = ctk.CTkFrame(
    card,
    fg_color="transparent"
)

card_header.pack(
    fill="x",
    padx=40,
    pady=(28, 4)
)


ctk.CTkLabel(
    card_header,
    text="Deal Collection",
    font=(
        "Segoe UI",
        19,
        "bold"
    ),
    text_color="#0F172A"
).pack(
    anchor="w"
)


ctk.CTkLabel(
    card,
    text="Connect to a Telegram channel and choose the number of deals to collect.",
    font=(
        "Segoe UI",
        11
    ),
    text_color="#64748B"
).pack(
    anchor="w",
    padx=40,
    pady=(0, 23)
)


# ================= CHANNEL =================

ctk.CTkLabel(
    card,
    text="TELEGRAM CHANNEL",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    text_color="#334155"
).pack(
    anchor="w",
    padx=40,
    pady=(0, 7)
)


channel_vcmd = app.register(
    validate_channel
)


channel_entry = ctk.CTkEntry(
    card,
    width=600,
    height=50,
    corner_radius=11,
    border_width=1,
    border_color="#CBD5E1",
    fg_color="#F8FAFC",
    text_color="#0F172A",
    font=(
        "Segoe UI",
        14,
        "bold"
    ),
    placeholder_text="Example: amazinglootsdeals",
    placeholder_text_color="#94A3B8",
    validate="key",
    validatecommand=(
        channel_vcmd,
        "%P"
    )
)

channel_entry.pack(
    padx=40
)


ctk.CTkLabel(
    card,
    text="Letters and underscores only  •  Maximum 32 characters",
    font=(
        "Segoe UI",
        10
    ),
    text_color="#94A3B8"
).pack(
    anchor="w",
    padx=40,
    pady=(5, 19)
)


channel_entry.insert(
    0,
    "amazinglootsdealsoffers"
)


# ================= LIMIT =================

ctk.CTkLabel(
    card,
    text="NUMBER OF DEALS",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    text_color="#334155"
).pack(
    anchor="w",
    padx=40,
    pady=(0, 7)
)


limit_vcmd = app.register(
    validate_limit
)


limit_entry = ctk.CTkEntry(
    card,
    width=600,
    height=50,
    corner_radius=11,
    border_width=1,
    border_color="#CBD5E1",
    fg_color="#F8FAFC",
    text_color="#0F172A",
    font=(
        "Segoe UI",
        14,
        "bold"
    ),
    placeholder_text="Example: 20",
    placeholder_text_color="#94A3B8",
    validate="key",
    validatecommand=(
        limit_vcmd,
        "%P"
    )
)

limit_entry.pack(
    padx=40
)


ctk.CTkLabel(
    card,
    text="Choose between 1 and 100 deals",
    font=(
        "Segoe UI",
        10
    ),
    text_color="#94A3B8"
).pack(
    anchor="w",
    padx=40,
    pady=(5, 28)
)


limit_entry.insert(
    0,
    "20"
)


# ================= START BUTTON =================

start_button = ctk.CTkButton(
    main_container,
    text="▶  Start Scraping",
    width=320,
    height=54,
    corner_radius=13,
    fg_color="#2563EB",
    hover_color="#1D4ED8",
    text_color="#FFFFFF",
    font=(
        "Segoe UI",
        15,
        "bold"
    ),
    command=start_thread
)

start_button.pack(
    pady=(22, 18)
)


# ================= STATUS CARD =================

status_card = ctk.CTkFrame(
    main_container,
    height=88,
    corner_radius=15,
    fg_color="#FFFFFF",
    border_width=1,
    border_color="#E2E8F0"
)

status_card.pack(
    fill="x"
)

status_card.pack_propagate(False)


status_content = ctk.CTkFrame(
    status_card,
    fg_color="transparent"
)

status_content.pack(
    fill="both",
    expand=True,
    padx=22
)


# Status dot

status_dot = ctk.CTkLabel(
    status_content,
    text="●",
    font=(
        "Segoe UI",
        18,
        "bold"
    ),
    text_color="#64748B"
)

status_dot.pack(
    side="left",
    padx=(3, 12)
)


# Status text

status_text_frame = ctk.CTkFrame(
    status_content,
    fg_color="transparent"
)

status_text_frame.pack(
    side="left"
)


status_label = ctk.CTkLabel(
    status_text_frame,
    text="Ready",
    font=(
        "Segoe UI",
        13,
        "bold"
    ),
    text_color="#334155"
)

status_label.pack(
    anchor="w"
)


status_description = ctk.CTkLabel(
    status_text_frame,
    text="Enter your details and start scraping.",
    font=(
        "Segoe UI",
        10
    ),
    text_color="#94A3B8"
)

status_description.pack(
    anchor="w",
    pady=(2, 0)
)


# ================= FOOTER =================

footer = ctk.CTkFrame(
    app,
    height=45,
    corner_radius=0,
    fg_color="#F1F5F9"
)

footer.pack(
    fill="x",
    side="bottom"
)

footer.pack_propagate(False)


ctk.CTkLabel(
    footer,
    text="Python   •   Telethon   •   Telegram API   •   Requests",
    font=(
        "Segoe UI",
        10
    ),
    text_color="#64748B"
).pack(
    pady=13
)


# ================= START APPLICATION =================

app.mainloop()

