# -*- coding: utf-8 -*-

from DynaUI import Locale

__all__ = ["Locale"]

Locale.DEFAULT = {
    "TITLE"               : "LabPype",

    "GROUP_NONE"          : "---- Not grouped ----",  # value is used as a key for widget group
    "GROUP_NEW"           : "New Group",

    "WIDGET_FAIL"         : "Task failed",
    "WIDGET_DONE"         : "Task done",

    "GADGET_SEARCH"       : "Search Widgets",
    "GADGET_CANCEL"       : "Clear search",
    "HIDER_GADGET"        : "Toggle Widget Panel Visibility",
    "HIDER_HARBOR"        : "Toggle Interaction Panel Visibility",

    "TOOL_OPTION"         : "Settings",
    "TOOL_FILE_N"         : "New Project",
    "TOOL_FILE_O"         : "Open Project",
    "TOOL_FILE_S"         : "Save Project",
    "TOOL_ALGN_L"         : "Align Left",
    "TOOL_ALGN_V"         : "Align Vertical",
    "TOOL_ALGN_R"         : "Align Right",
    "TOOL_ALGN_T"         : "Align Top",
    "TOOL_ALGN_H"         : "Align Horizontal",
    "TOOL_ALGN_B"         : "Align Bottom",
    "TOOL_DIST_H"         : "Distribute Horizontally",
    "TOOL_DIST_V"         : "Distribute Vertically",
    "TOOL_MOVE_T"         : "Move to Top",
    "TOOL_MOVE_U"         : "Move Up",
    "TOOL_MOVE_D"         : "Move Down",
    "TOOL_MOVE_B"         : "Move to Bottom",
    "TOOL_T_ANCR"         : "Toggle Anchor Visibility",
    "TOOL_T_NAME"         : "Toggle Name Visibility",
    "TOOL_T_SNAP"         : "Snap to Grid",
    "TOOL_T_CURV"         : "Curved Line",
    "TOOL_T_DIAG"         : "Toggle All Dialogs",
    "TOOL_T_FSCN"         : "Toggle Full Screen",
    "TOOL_CANCEL"         : "Close All Dialogs",
    "TOOL_DELETE"         : "Remove Selected Widget",
    "TOOL_T_SHOW"         : "Collapse or Expand all",
    "TOOL_T_TEXT"         : "Toggle Label Display",
    "TOOL_MANAGE"         : "Manage Widgets",

    "MSG_TOO_MANY_WIDGETS": "Too many widgets!",
    "MSG_SINGLETON_EXISTS": "This widget can only have one instance!",
    "MSG_CIRCULAR_LINKAGE": "Circular reference is not allowed!",
    "MSG_WORKSPACE_FAIL"  : "Failed to use \"%s\" as workspace.",
    "MSG_UNKNOWN_WIDGET"  : "Failed to load the file: Unknown widget %s",
    "MSG_LOAD_FILE_FAILED": "Failed to load the file!",
    "MSG_SAVE_FILE_FAILED": "Failed to save the file!",

    "GENERAL_HEAD_FAIL"   : "An error has occurred",
    "GENERAL_HEAD_LOAD"   : "Load...",
    "GENERAL_HEAD_SAVE"   : "Save...",

    "GENERAL_READY"       : "OK",
    "GENERAL_BEGIN"       : "Run",
    "GENERAL_ABORT"       : "Stop",
    "GENERAL_APPLY"       : "Apply",
    "GENERAL_CLOSE"       : "Cancel",
    "GENERAL_RESET"       : "Reset",

    "DIALOG_HEAD_LOAD"    : "Load project/scheme",
    "DIALOG_HEAD_SAVE"    : "Save project/scheme",
    "DIALOG_HEAD_NEW?"    : "New project confirm",
    "DIALOG_LOAD_MODE_A"  : "Append",
    "DIALOG_LOAD_MODE_O"  : "Open",
    "DIALOG_LOAD_ONLY_Y"  : "Scheme only: Yes",
    "DIALOG_LOAD_ONLY_N"  : "Scheme only: No",
    "DIALOG_LOAD_LIST_S"  : "Schemes",
    "DIALOG_LOAD_LIST_P"  : "Projects",
    "DIALOG_CLEAN_S"      : "Clean recent schemes",
    "DIALOG_CLEAN_P"      : "Clean recent projects",
    "DIALOG_SAVE_MODE_S"  : "Save scheme",
    "DIALOG_SAVE_MODE_P"  : "Save project",
    "DIALOG_NEW?_INFO"    : "Canvas is not empty. Are you sure you want to clear the canvas?",

    "MANAGE_TITLE"        : "Widget Manage",
    "MANAGE_PKG_REMOTE"   : "Download from repository",
    "MANAGE_PKG_BROWSE"   : "Install from disk",
    "MANAGE_PKG_REMOVE"   : "Remove selected package",

    "MANAGE_HEAD_REMOTE"  : "Download from url",
    "MANAGE_REMOTE_FAIL"  : "Fail to download from url:\n%s",

    "MANAGE_NEW_GROUP"    : "+ Add New Group +",
    "MANAGE_HELP_HEAD"    : "How to manage widgets",
    "MANAGE_HELP_TEXT"    : "To add widget, \n"
                            "To remove widget, \n"
                            "To add group, \n"
                            "To remove group, \n"
                            "To rearrange widget, \n"
                            "To rearrange group, \n"
                            "To change group name, \n",

    "MSG_PKG_INIT_FAIL"   : "The following package(s) cannot be loaded:\n%s",
    "MSG_PKG_INSTALL_HEAD": "Package install",
    "MSG_PKG_EXTRACT_FAIL": "Failed to extract %s",
    "MSG_PKG_INSTALL_DONE": "The following packages have been successfully installed:",
    "MSG_PKG_INSTALL_FAIL": "The following packages cannot be installed:",
    "MSG_PKG_ALREADY_HERE": "The following packages are already installed:",

}
