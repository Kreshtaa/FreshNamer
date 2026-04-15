from logger import setup_logger
log = setup_logger()

def build_config_from_gui(gui) -> dict:
    """
    Reads all GUI fields and builds a config dict expected by rename_files().
    """
    log.debug("[CONFIG] Building config from GUI")

    config = {}

    def read_category(cat_key, widgets):
        enabled = widgets["enabled"].isChecked()
        mode = "advanced" if widgets["advanced_mode"].isChecked() else "normal"
        log.debug(f"[CONFIG] Category '{cat_key}' enabled={enabled} mode={mode}")

        # Normal mode
        if mode == "normal":
            prefix = widgets["prefix"].text()
            suffix = widgets["suffix"].text()
            padding = int(widgets["padding"].currentText())
            start = int(widgets["start"].value())

            log.debug(f"[CONFIG] Normal mode: prefix='{prefix}' suffix='{suffix}' padding={padding} start={start}")

            return {
                "enabled": enabled,
                "mode": "normal",
                "prefix": prefix,
                "suffix": suffix,
                "padding": padding,
                "start": start,
                "advanced": ""
            }
        # Advanced Mode
        fmt = widgets["advanced_text"].text()
        start = int(widgets["start"].value())

        log.debug(f"[CONFIG] Advanced mode: pattern='{fmt}' start={start}")

        # Validate advanced format string
        try:
            fmt.format(
                original="test",
                num=1,
                num_padded="01",
                prefix="",
                suffix="",
                category="test",
                folder="/test"
            )
        except Exception as e:
            log.error(f"[CONFIG] Invalid format string for '{cat_key}': {e}")
            raise ValueError(f"Invalid format string for '{cat_key}': {e}")
        
        return {
            "enabled": enabled,
            "mode": "advanced",
            "prefix": "",
            "suffix": "",
            "padding": 0,
            "start": start,
            "advanced": fmt
        }
    
    # Build config for each category
    config["image"] = read_category("image", gui.widgets_image)
    config["video"] = read_category("video", gui.widgets_video)
    config["gif"] = read_category("gif", gui.widgets_gif)
    config["audio"] = read_category("audio", gui.widgets_audio)
    config["document"] = read_category("document", gui.widgets_document)

    return config
        