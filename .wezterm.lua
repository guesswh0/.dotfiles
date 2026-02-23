local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.font = wezterm.font("Hack Nerd Font")
config.font_size = 14
config.color_scheme = 'AdventureTime'

config.enable_tab_bar = false
-- config.window_decorations = "RESIZE"

config.window_background_opacity = 0.7
config.macos_window_background_blur = 3

config.default_cursor_style = 'BlinkingUnderline'
config.cursor_blink_rate = 800

config.native_macos_fullscreen_mode = false

wezterm.on("gui-startup", function()
    local _, _, window = wezterm.mux.spawn_window{}
    window:gui_window():toggle_fullscreen()
end)

config.keys = {
	{ mods = "OPT", key = "LeftArrow", action = wezterm.action.SendKey({ mods = "ALT", key = "b" }) },
	{ mods = "OPT", key = "RightArrow", action = wezterm.action.SendKey({ mods = "ALT", key = "f" }) },
	{ mods = "CMD", key = "LeftArrow", action = wezterm.action.SendKey({ mods = "CTRL", key = "a" }) },
	{ mods = "CMD", key = "RightArrow", action = wezterm.action.SendKey({ mods = "CTRL", key = "e" }) },
	{ mods = "CMD", key = "Backspace", action = wezterm.action.SendKey({ mods = "CTRL", key = "u" }) },

    { key = 'd', mods = 'CMD', action = wezterm.action.SplitHorizontal({ domain = 'CurrentPaneDomain' }), },
    { key = 'd', mods = 'CMD|SHIFT', action = wezterm.action.SplitVertical({ domain = 'CurrentPaneDomain' }), },
    { key = 'w', mods = 'CMD', action = wezterm.action.CloseCurrentPane({ confirm = false }), },
    { key = 'w', mods = 'CMD|SHIFT', action = wezterm.action.CloseCurrentTab({ confirm = false }), },
    { key = '[', mods = 'CMD', action = wezterm.action.ActivatePaneDirection('Left') },
    { key = ']', mods = 'CMD', action = wezterm.action.ActivatePaneDirection('Right') },
}


return config